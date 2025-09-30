import concurrent.futures
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd
from utils.data_utils import execute_pandas_query_for_computation, sample_data
from utils.file_operation import (
    clean_markdown_output,
    load_cached_json,
    load_prompt_template,
    save_json_data,
)
from utils.llm_operations import extract_json_from_response, invoke_llm_with_prompt


@dataclass
class ResearchConfig:
    depth: int = 2
    breadth: int = 3
    max_workers: int = 4
    use_caching: bool = True


@dataclass
class ResearchQuestion:
    level: int  # 0 for breadth questions, 1+ for depth questions
    question: str
    parent_question: Optional[str]
    visualization: str = (
        ""  # suggested visualization type (e.g., bar chart, line chart, pie chart, etc.)
    )
    category: str = (
        ""  # suggested category of the question (e.g., temporal, categorical, numerical, etc.)
    )
    source_columns: List[str] = field(default_factory=list)


@dataclass
class ResearchResult:
    question: str
    title: str = ""
    explanation: str = ""
    visualization_code: str = ""
    computed_data: Any = None
    category: str = ""
    source_columns: List[str] = field(default_factory=list)


class Researcher:
    def __init__(self, config: ResearchConfig, dataset_profile: Dict):
        self.config = config
        self.dataset_profile = dataset_profile
        self.research_questions: List[ResearchQuestion] = []
        self.research_results: List[ResearchResult] = []

    # Step 1: Generate research questions
    def generate_research_questions(self):
        print("Step 1: Generating Research Questions...")

        # Check cache first
        if self.config.use_caching:
            cached_questions = load_cached_json(
                "final_research_questions.json", "./datasets"
            )
            if cached_questions:
                print("Using cached research questions")
                self.research_questions = [
                    ResearchQuestion(**q) for q in cached_questions["questions"]
                ]
                return self.research_questions

        # Step 1.1: Questions that explore the overall dataset
        breadth_questions = self._generate_breadth_questions()

        # Step 1.2: Questions that explore the depth of the dataset
        depth_questions = self._generate_depth_questions_parallel(breadth_questions)

        # Store the questions in the instance variable
        self.research_questions = breadth_questions + depth_questions

        # Save research questions to JSON
        if self.config.use_caching:
            questions_dict = {
                "questions": [
                    {
                        "question": q.question,
                        "parent_question": q.parent_question,
                        "level": q.level,
                        "visualization": q.visualization,
                        "category": q.category,
                        "source_columns": q.source_columns,
                    }
                    for q in self.research_questions
                ]
            }
            save_json_data(
                questions_dict, "final_research_questions.json", "./datasets"
            )

        return self.research_questions

    # Step 2: Conduct research
    def conduct_research(self):
        print("Step 2: Conducting Research...")

        # Check cache first
        if self.config.use_caching:
            cached_results = load_cached_json("research_results.json", "./datasets")
            if cached_results:
                print("Using cached research results")
                self.research_results = [
                    ResearchResult(**r) for r in cached_results["results"]
                ]
                return self.research_results

        # Conduct research in parallel
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            # Submit all research tasks
            research_results_to_question = {
                executor.submit(self._conduct_research_for_question, question): question
                for question in self.research_questions
            }

            # Collect results
            results = []
            for research_result in concurrent.futures.as_completed(
                research_results_to_question
            ):
                question = research_results_to_question[research_result]
                try:
                    result = research_result.result()
                    if result:
                        results.append(result)
                except Exception as exc:
                    print(
                        f'Research for "{question.question}" generated an exception: {exc}'
                    )

        self.research_results = results

        # Save research results to JSON
        if self.config.use_caching:
            from utils.data_utils import convert_numpy_types

            results_dict = {
                "results": [
                    {
                        "question": research_result.question,
                        "title": research_result.title,
                        "explanation": research_result.explanation,
                        "visualization_code": research_result.visualization_code,
                        "computed_data": convert_numpy_types(
                            research_result.computed_data
                        ),
                        "category": research_result.category,
                        "source_columns": research_result.source_columns,
                    }
                    for research_result in self.research_results
                ]
            }
            save_json_data(results_dict, "research_results.json", "./datasets")

        return results

    # Step 3: Generate final report
    def generate_final_report(self):
        print("Step 3: Generating Final Report...")

        # Check cache first
        if self.config.use_caching:
            cached_arrangement = load_cached_json("final_report.json", "./datasets")
            if cached_arrangement:
                print("Using cached final report")
                return cached_arrangement

        system_prompt = load_prompt_template("sys_prompts", "generate_final_report.md")

        research_results_array = [
            {
                "question": result.question,
                "title": result.title,
                "explanation": result.explanation,
                "visualization_code": result.visualization_code,
                "computed_data": result.computed_data,
                "category": result.category,
                "source_columns": result.source_columns,
            }
            for result in self.research_results
        ]

        final_report = invoke_llm_with_prompt(
            system_prompt,
            "",
            {
                "research_results": json.dumps(research_results_array, indent=2),
            },
            {},
        )

        final_report_json = extract_json_from_response(final_report)

        final_report = {
            "title": final_report_json.get("title", ""),  # type: ignore
            "introduction": final_report_json.get("introduction", ""),  # type: ignore
            "arranged_research_sections": [
                research_results_array[idx] for idx in final_report_json.get("arranged_research_sections", [])  # type: ignore
            ],
            "conclusion": final_report_json.get("conclusion", ""),  # type: ignore
            "total_results": len(final_report_json.get("arranged_research_sections", [])),  # type: ignore
        }

        # Save final report to JSON
        if self.config.use_caching:
            save_json_data(final_report, "final_report.json", "./datasets")

        return final_report

    # Step 1.1: Generate breadth questions
    def _generate_breadth_questions(self):
        print(f"    Step 1.1: Generating {self.config.breadth} breadth questions...")

        system_prompt = load_prompt_template(
            "sys_prompts", "generate_breadth_questions.md"
        )

        dataset_profile_json = json.dumps(self.dataset_profile, indent=2)

        breadth_questions_data = invoke_llm_with_prompt(
            system_prompt,
            "",
            {
                "breadth": self.config.breadth,
                "dataset_profile_json": dataset_profile_json,
            },
            {},
        )
        breadth_questions_data_json = extract_json_from_response(breadth_questions_data)

        if self.config.use_caching:
            save_json_data(
                dict(questions=breadth_questions_data_json),
                "breadth_questions_data.json",
                "./datasets",
            )

        breadth_questions = []

        for i, q_data in enumerate(breadth_questions_data_json):
            question = ResearchQuestion(
                level=0,
                parent_question=None,
                question=q_data["question"],  # type: ignore
                visualization=q_data.get("visualization", ""),  # type: ignore
                category=q_data.get("category", f"category_{i}"),  # type: ignore
                source_columns=q_data.get("source_columns", []),  # type: ignore
            )
            breadth_questions.append(question)

        return breadth_questions

    # Step 1.2: Generate depth questions in parallel for each breadth question
    def _generate_depth_questions_parallel(
        self, breadth_questions: List[ResearchQuestion]
    ) -> List[ResearchQuestion]:
        """Generate depth questions in parallel for each breadth question"""
        print(
            f"    Step 1.2: Generating {self.config.depth} follow-up questions for each {self.config.breadth} breadth question in parallel..."
        )

        depth_questions = []

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            follow_up_to_parent_question = {
                executor.submit(
                    self._generate_depth_questions_for_parent, parent_question
                ): parent_question
                for parent_question in breadth_questions
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(follow_up_to_parent_question):
                parent = follow_up_to_parent_question[future]
                try:
                    questions = future.result()
                    depth_questions.extend(questions)
                except Exception as exc:
                    print(
                        f'Question generation for "{parent.question}" generated an exception: {exc}'
                    )

        return depth_questions

    # Step 1.2.1: Generate depth questions for a parent question
    def _generate_depth_questions_for_parent(
        self, parent_question: ResearchQuestion
    ) -> List[ResearchQuestion]:

        system_prompt = load_prompt_template(
            "sys_prompts", "generate_depth_questions.md"
        )

        dataset_profile_json = json.dumps(self.dataset_profile, indent=2)
        response = invoke_llm_with_prompt(
            system_prompt,
            "",
            {
                "dataset_profile_json": dataset_profile_json,
                "parent_question": parent_question.question,
                "parent_question_category": parent_question.category,
                "parent_question_source_columns": parent_question.source_columns,
            },
            {},
        )

        questions_data = extract_json_from_response(response)

        depth_questions = []

        for level in range(1, self.config.depth + 1):
            if level - 1 < len(questions_data):
                q_data = questions_data[level - 1]  # type: ignore
                question = ResearchQuestion(
                    level=level,
                    question=q_data["question"],
                    parent_question=parent_question.question,
                    visualization=q_data.get("visualization", ""),
                    category=q_data.get("category", parent_question.category),
                    source_columns=q_data.get("source_columns", []),
                )
                depth_questions.append(question)

        return depth_questions

    # Step 2.1: Conduct research for a question
    def _conduct_research_for_question(
        self, question: ResearchQuestion
    ) -> ResearchResult:
        # Step 2.1: Generate Pandas Code
        pandas_code = self._generate_pandas_code(question)

        # Step 2.2: Execute Pandas Code
        computed_data = execute_pandas_query_for_computation(pandas_code)

        if not computed_data or len(computed_data) > 10000:
            print(
                f"Skipping question - inapplicable data: {question.question} : {len(computed_data)}"
            )
            return None  # type: ignore

        system_prompt = load_prompt_template(
            "sys_prompts", "conduct_research_for_question.md"
        )

        research_result = invoke_llm_with_prompt(
            system_prompt,
            "",
            {
                "question": question,
                "computed_data": computed_data,
            },
            {},
        )

        research_result_json = extract_json_from_response(research_result)

        return ResearchResult(
            question=question.question,
            title=research_result_json.get("title", ""),  # type: ignore
            visualization_code=research_result_json.get("visualization_schema", ""),  # type: ignore
            computed_data=computed_data,
            explanation=research_result_json.get("narrative", ""),  # type: ignore
            category=question.category,
            source_columns=question.source_columns,
        )

    # Step 2.1.1: Generate Pandas Code
    def _generate_pandas_code(self, question: ResearchQuestion) -> str:
        sampled_data = sample_data(question.source_columns, sample_size=5)
        sample_data_stringified = "\n".join(
            [f"{col}: {values}" for col, values in sampled_data.items()]
        )

        system_prompt = load_prompt_template("sys_prompts", "generate_pandas_code.md")
        user_prompt = load_prompt_template("user_prompts", "generate_pandas_code.md")

        pandas_code = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {},
            {
                "question": question.question,
                "visualization": question.visualization,
                "category": question.category,
                "source_columns": question.source_columns,
                "sampled_data": sample_data_stringified,
            },
        )

        pandas_code = clean_markdown_output(pandas_code)

        return pandas_code
