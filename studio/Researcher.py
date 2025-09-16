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
    breadth: int = 6
    max_workers: int = 8
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
        print(" === Step 1: Generating Research Questions... ===")

        # Check cache first
        if self.config.use_caching:
            cached_questions = load_cached_json("research_questions.json", "./datasets")
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
            save_json_data(questions_dict, "research_questions.json", "./datasets")

        return self.research_questions

    # Step 2: Conduct research
    def conduct_research(self):
        print(" === Step 2: Conducting Research... ===")

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
            results_dict = {
                "results": [
                    {
                        "question": r.question,
                        "title": r.title,
                        "explanation": r.explanation,
                        "visualization_code": r.visualization_code,
                        "computed_data": r.computed_data,
                        "category": r.category,
                        "source_columns": r.source_columns,
                    }
                    for r in self.research_results
                ]
            }
            save_json_data(results_dict, "research_results.json", "./datasets")

        return results

    # Step 3: Generate final report
    def generate_final_report(self):
        print(" === Step 3: Generating Final Report... ===")

        # Check cache first
        if self.config.use_caching:
            cached_arrangement = load_cached_json(
                "final_arrangement.json", "./datasets"
            )
            if cached_arrangement:
                print("Using cached final arrangement")
                return cached_arrangement

        filtered_research_sections = self._filter_research_sections(
            self.research_results
        )

        # Generate Research Paper Title, Introduction, and Conclusion
        introduction = self._generate_research_paper_introduction(
            filtered_research_sections
        )
        conclusion = self._generate_research_paper_conclusion(
            filtered_research_sections
        )
        title = self._generate_research_paper_title(
            filtered_research_sections, introduction, conclusion
        )

        # Arrange the research sections
        arranged_research_sections = self._arrange_research_sections(
            title, introduction, conclusion, filtered_research_sections
        )

        # Convert ResearchResult objects to dictionaries for JSON serialization
        arranged_sections_dicts = []
        for result in arranged_research_sections:
            arranged_sections_dicts.append(
                {
                    "question": result.question,
                    "title": result.title,
                    "explanation": result.explanation,
                    "visualization_code": result.visualization_code,
                    "computed_data": result.computed_data,
                    "category": result.category,
                    "source_columns": result.source_columns,
                }
            )

        final_arrangement = {
            "title": title,
            "introduction": introduction,
            "arranged_research_sections": arranged_sections_dicts,
            "conclusion": conclusion,
            "total_results": len(arranged_research_sections),
        }

        # Save final arrangement to JSON
        if self.config.use_caching:
            save_json_data(final_arrangement, "final_arrangement.json", "./datasets")

        return final_arrangement

    def _generate_breadth_questions(self):
        print(" === Step 1.1: Generating Breadth Questions... ===")

        system_prompt = load_prompt_template(
            "sys_prompts", "generate_breadth_questions.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_breadth_questions.md"
        )

        dataset_profile_json = json.dumps(self.dataset_profile, indent=2)
        breadth_questions_data = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "breadth": self.config.breadth,
                "dataset_profile_json": dataset_profile_json,
            },
        )
        breadth_questions_data_json = extract_json_from_response(breadth_questions_data)

        breadth_questions = []

        for i, q_data in enumerate(breadth_questions_data_json):
            question = ResearchQuestion(
                level=0,
                question=q_data["question"],  # type: ignore
                parent_question=None,
                visualization=q_data.get("visualization", ""),  # type: ignore
                category=q_data.get("category", f"category_{i}"),  # type: ignore
                source_columns=q_data.get("source_columns", []),  # type: ignore
            )
            breadth_questions.append(question)

        return breadth_questions

    def _generate_depth_questions_parallel(
        self, breadth_questions: List[ResearchQuestion]
    ) -> List[ResearchQuestion]:
        """Generate depth questions in parallel for each breadth question"""
        print(
            f"  === Step 1.2: Generating {self.config.depth} follow-up questions for each {self.config.breadth} breadth question in parallel... === "
        )

        depth_questions = []

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            follow_up_to_parent_question = {
                executor.submit(
                    self._generate_depth_questions_for_parent, parent
                ): parent
                for parent in breadth_questions
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

    def _generate_depth_questions_for_parent(
        self, parent_question: ResearchQuestion
    ) -> List[ResearchQuestion]:

        system_prompt = load_prompt_template(
            "sys_prompts", "generate_depth_questions.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_depth_questions.md"
        )

        dataset_profile_json = json.dumps(self.dataset_profile, indent=2)
        response = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "depth": self.config.depth,
                "parent_question": parent_question.question,
                "parent_question_category": parent_question.category,
                "parent_question_source_columns": parent_question.source_columns,
                "dataset_profile_json": dataset_profile_json,
            },
        )

        questions_data = extract_json_from_response(response)

        depth_questions = []
        # Check if it's an error response
        if isinstance(questions_data, dict) and "error" in questions_data:
            raise json.JSONDecodeError(questions_data["error"], "", 0)

        # Ensure we have a list after error check
        if not isinstance(questions_data, list):
            raise json.JSONDecodeError("Expected list of questions", "", 0)

        for level in range(1, self.config.depth + 1):
            if level - 1 < len(questions_data):
                q_data = questions_data[level - 1]
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

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(2, self.config.max_workers)
        ) as executor:
            viz_for_question = executor.submit(
                self._generate_visualization_code, question, computed_data
            )
            title_for_viz = executor.submit(
                self._generate_title_for_visualization, question, computed_data
            )
            narrative_for_viz = executor.submit(
                self._generate_narrative_for_visualization, question, computed_data
            )

            viz_code = viz_for_question.result()
            title = title_for_viz.result()
            narrative = narrative_for_viz.result()

        return ResearchResult(
            question=question.question,
            title=title,
            visualization_code=viz_code,
            computed_data=computed_data,
            explanation=narrative,
            category=question.category,
            source_columns=question.source_columns,
        )

    def _generate_pandas_code(self, question: ResearchQuestion) -> str:
        print(f"Generating pandas code for question: {question.question}")

        sampled_data = sample_data(question.source_columns, sample_size=5)
        sample_data_stringified = "\n".join(
            [f"{col}: {values}" for col, values in sampled_data.items()]
        )

        system_prompt = load_prompt_template("sys_prompts", "generate_pandas_code.md")
        user_prompt = load_prompt_template("user_prompts", "generate_pandas_code.md")

        pandas_code = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
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

    def _generate_visualization_code(
        self, question: ResearchQuestion, computed_data: Any
    ) -> str:
        """Generate Python matplotlib/seaborn code for the computed data"""
        # Use entire computed data, not just a sample
        computed_data = json.dumps(computed_data, indent=2)

        system_prompt = load_prompt_template(
            "sys_prompts", "generate_visualization_code.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_visualization_code.md"
        )

        viz_code = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "question": question.question,
                "visualization": question.visualization,
                "category": question.category,
                "computed_data": computed_data,
            },
        )
        viz_code = clean_markdown_output(viz_code)

        return viz_code

    def _generate_title_for_visualization(
        self, question: ResearchQuestion, computed_data: Any
    ) -> str:
        system_prompt = load_prompt_template(
            "sys_prompts", "generate_visualization_title.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_visualization_title.md"
        )

        title = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "question": question.question,
                "category": question.category,
                "computed_data": computed_data,
            },
        )

        return title

    def _generate_narrative_for_visualization(
        self, question: ResearchQuestion, computed_data: Any
    ) -> str:
        system_prompt = load_prompt_template(
            "sys_prompts", "generate_visualization_narrative.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_visualization_narrative.md"
        )

        narrative = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "question": question.question,
                "category": question.category,
                "computed_data": computed_data,
            },
        )

        return narrative

    def _filter_research_sections(
        self, research_results: List[ResearchResult]
    ) -> List[ResearchResult]:
        if not research_results:
            print("Research results are empty")
            return []

        unfiltered_research_results = []
        for idx, result in enumerate(research_results):
            result_summary = {
                "index": idx,
                "question": result.question,
                "title": result.title,
                "explanation": result.explanation,
                "visualization_code": result.visualization_code,
                "computed_data": result.computed_data,
                "category": result.category,
                "source_columns": result.source_columns,
            }

            unfiltered_research_results.append(result_summary)

        sys_prompt = load_prompt_template("sys_prompts", "filter_research_sections.md")
        user_prompt = load_prompt_template(
            "user_prompts", "filter_research_sections.md"
        )

        selected_indices = invoke_llm_with_prompt(
            sys_prompt,
            user_prompt,
            {
                "research_results_size": len(unfiltered_research_results),
                "research_results": json.dumps(unfiltered_research_results, indent=2),
            },
        )

        selected_indices = extract_json_from_response(selected_indices)
        if isinstance(selected_indices, list):
            filtered_research_results = [
                self.research_results[i] for i in selected_indices
            ]
            print(
                f"LLM quality filtering: {len(self.research_results)} -> {len(filtered_research_results)} results"
            )
            return filtered_research_results
        else:
            print("LLM quality filtering: Failed to extract selected indices")
            return []

    def _generate_research_paper_introduction(
        self, research_results: List[ResearchResult]
    ) -> str:
        system_prompt = load_prompt_template(
            "sys_prompts", "generate_research_paper_introduction.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_research_paper_introduction.md"
        )

        lightweighted_research_results = []
        for result in research_results:
            lightweighted_research_results.append(
                {
                    "question": result.question,
                    "title": result.title,
                    "explanation": result.explanation,
                }
            )

        introduction = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "research_results": json.dumps(
                    lightweighted_research_results, indent=2
                ),
            },
        )
        return introduction

    def _generate_research_paper_conclusion(
        self, research_results: List[ResearchResult]
    ) -> str:
        system_prompt = load_prompt_template(
            "sys_prompts", "generate_research_paper_conclusion.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_research_paper_conclusion.md"
        )

        lightweighted_research_results = []
        for result in research_results:
            lightweighted_research_results.append(
                {
                    "question": result.question,
                    "title": result.title,
                    "explanation": result.explanation,
                }
            )

        conclusion = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "research_results": json.dumps(
                    lightweighted_research_results, indent=2
                ),
            },
        )
        return conclusion

    def _generate_research_paper_title(
        self, research_results: List[ResearchResult], introduction: str, conclusion: str
    ) -> str:
        system_prompt = load_prompt_template(
            "sys_prompts", "generate_research_paper_title.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "generate_research_paper_title.md"
        )

        # Convert ResearchResult objects to dictionaries for JSON serialization
        lightweighted_research_results = []
        for result in research_results:
            lightweighted_research_results.append(
                {
                    "question": result.question,
                    "title": result.title,
                    "explanation": result.explanation,
                }
            )

        title = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            {
                "research_results": json.dumps(
                    lightweighted_research_results, indent=2
                ),
                "introduction": introduction,
                "conclusion": conclusion,
            },
        )
        return title

    def _arrange_research_sections(
        self,
        title: str,
        introduction: str,
        conclusion: str,
        research_results: List[ResearchResult],
    ) -> List[ResearchResult]:
        system_prompt = load_prompt_template(
            "sys_prompts", "arrange_research_sections.md"
        )
        user_prompt = load_prompt_template(
            "user_prompts", "arrange_research_sections.md"
        )

        research_results_with_indices = []
        for idx, result in enumerate(research_results):
            research_results_with_indices.append(
                {
                    "index": idx,
                    "result": result.question,
                    "title": result.title,
                    "explanation": result.explanation,
                    "category": result.category,
                    "source_columns": result.source_columns,
                }
            )

        arranged_indices = invoke_llm_with_prompt(
            system_prompt,
            user_prompt,
            replacements={
                "title": title,
                "introduction": introduction,
                "conclusion": conclusion,
                "research_results": json.dumps(research_results_with_indices, indent=2),
            },
        )

        arranged_indices = extract_json_from_response(arranged_indices)
        if isinstance(arranged_indices, list):
            arranged_research_results = [research_results[i] for i in arranged_indices]
            print(
                f"Research sections arrangement for {len(research_results)} completed"
            )
            return arranged_research_results
        else:
            print("LLM quality filtering: Failed to extract selected indices")
            return []
