import concurrent.futures
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from utils.file_operation import load_cached_json, load_prompt_template, save_json_data
from utils.llm_operations import invoke_llm_with_prompt
from utils.llm_operations import extract_json_from_response


@dataclass
class ResearchConfig:
    depth: int = 3
    breadth: int = 4
    max_workers: int = 8
    use_caching: bool = True


@dataclass
class ResearchQuestion:
    level: int  # 0 for breadth questions, 1+ for depth questions
    question: str
    parent_question: Optional[str]
    visualization: str = ""
    category: str = ""
    source_columns: List[str] = field(default_factory=list)


@dataclass
class ResearchResult:
    question: str
    computed_data: Any = None
    explanation: str = ""
    visualization_code: str = ""
    title: str = ""
    category: str = ""
    source_columns: List[str] = field(default_factory=list)


class Researcher:
    def __init__(self, config: ResearchConfig, dataset_profile: Dict):
        self.config = config
        self.dataset_profile = dataset_profile
        self.research_questions: List[ResearchQuestion] = []
        self.research_results: List[ResearchResult] = []

    def step1_generate_research_questions(self) -> List[ResearchQuestion]:
        print(" === Step 1: Generating Research Questions === ")

        # Check cache first
        if self.config.use_caching:
            cached_questions = load_cached_json("research_questions.json")
            if cached_questions:
                print("Using cached research questions")
                self.research_questions = [
                    ResearchQuestion(**q) for q in cached_questions  # type: ignore
                ]
                return self.research_questions

        # Step 1.1: Generate breadth questions
        breadth_questions = self._generate_breadth_questions()

        # Step 1.2: Generate depth questions in parallel
        depth_questions = self._generate_depth_questions_parallel(breadth_questions)

        self.research_questions = breadth_questions + depth_questions

        # Cache the results
        if self.config.use_caching:
            questions_dict = [
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
            save_json_data(questions_dict, "research_questions.json")  # type: ignore

        print(f"Generated {len(self.research_questions)} total research questions")
        return self.research_questions

    def _generate_breadth_questions(self) -> List[ResearchQuestion]:
        """Generate breadth-amount of wide-ranging questions covering different aspects of data"""
        print(
            f"  === Step 1.1: Generating {self.config.breadth} breadth questions... === "
        )

        system_prompt = load_prompt_template("sys_prompt_generate_breadth_questions.md")
        user_prompt = load_prompt_template("user_prompt_generate_breadth_questions.md")

        dataset_profile_json = json.dumps(self.dataset_profile, indent=2)
        response = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={"dataset_profile_json": dataset_profile_json},
        )

        try:
            questions_data = extract_json_from_response(response)

            # Check if it's an error response
            if isinstance(questions_data, dict) and "error" in questions_data:
                raise json.JSONDecodeError(questions_data["error"], "", 0)

            # Ensure we have a list after error check
            if not isinstance(questions_data, list):
                raise json.JSONDecodeError("Expected list of questions", "", 0)

            breadth_questions = []

            for i, q_data in enumerate(questions_data[: self.config.breadth]):
                question = ResearchQuestion(
                    level=0,
                    question=q_data["question"],
                    parent_question=None,
                    visualization=q_data.get("visualization", ""),
                    category=q_data.get("category", f"category_{i}"),
                    source_columns=q_data.get("source_columns", []),
                )
                breadth_questions.append(question)

            return breadth_questions

        except json.JSONDecodeError as e:
            print(f"Error parsing breadth questions: {e}")
            # Fallback questions
            return [
                ResearchQuestion(
                    question=f"What are the key patterns in the data for analysis {i}?",
                    parent_question=None,
                    level=0,
                    visualization="scatter plot",  # better fallback than bar chart
                    category=f"fallback_{i}",
                    source_columns=[],
                )
                for i in range(self.config.breadth)
            ]

    def _generate_depth_questions_parallel(
        self, breadth_questions: List[ResearchQuestion]
    ) -> List[ResearchQuestion]:
        """Generate depth questions in parallel for each breadth question"""
        print(
            f"  === Step 1.2: Generating {self.config.depth} follow-up questions for each breadth question in parallel... === "
        )

        depth_questions = []

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            # Submit all tasks
            future_to_parent = {
                executor.submit(
                    self._generate_depth_questions_for_parent, parent
                ): parent
                for parent in breadth_questions
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_parent):
                parent = future_to_parent[future]
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
        """Generate depth questions for a specific parent question"""

        system_prompt = load_prompt_template("sys_prompt_generate_depth_questions.md")
        user_prompt = load_prompt_template("user_prompt_generate_depth_questions.md")

        dataset_profile_json = json.dumps(self.dataset_profile, indent=2)
        response = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "dataset_profile_json": dataset_profile_json,
                "parent_question": parent_question.question,
                "parent_question_category": parent_question.category,
                "parent_question_visualization": parent_question.visualization,
            },
        )

        try:
            questions_data = extract_json_from_response(response)

            # Check if it's an error response
            if isinstance(questions_data, dict) and "error" in questions_data:
                raise json.JSONDecodeError(questions_data["error"], "", 0)

            # Ensure we have a list after error check
            if not isinstance(questions_data, list):
                raise json.JSONDecodeError("Expected list of questions", "", 0)

            depth_questions = []

            for level in range(1, self.config.depth + 1):
                if level - 1 < len(questions_data):
                    q_data = questions_data[level - 1]
                    question = ResearchQuestion(
                        question=q_data["question"],
                        parent_question=parent_question.question,
                        level=level,
                        visualization=q_data.get("visualization", ""),
                        category=q_data.get("category", parent_question.category),
                        source_columns=q_data.get("source_columns", []),
                    )
                    depth_questions.append(question)

            return depth_questions

        except json.JSONDecodeError as e:
            print(
                f"Error parsing depth questions for '{parent_question.question}': {e}"
            )
            # Fallback depth questions
            return [
                ResearchQuestion(
                    question=f"What specific patterns emerge when analyzing {parent_question.category} in detail (level {i})?",
                    parent_question=parent_question.question,
                    level=i,
                    visualization="scatter plot",  # better fallback than bar chart
                    category=parent_question.category,
                    source_columns=[],
                )
                for i in range(1, self.config.depth + 1)
            ]

    def step2_conduct_research(self) -> List[ResearchResult]:
        """
        Step 2: Conduct Research from Generated Questions
        For each question: establish steps, compute data, create visualization, generate explanation
        """
        print("Step 2: Conducting Research for All Questions")

        # Conduct research in parallel
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            # Submit all research tasks
            future_to_question = {
                executor.submit(self._conduct_research_for_question, question): question
                for question in self.research_questions
            }

            # Collect results
            results = []
            for future in concurrent.futures.as_completed(future_to_question):
                question = future_to_question[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as exc:
                    print(
                        f'Research for "{question.question}" generated an exception: {exc}'
                    )

        self.research_results = results

        # Cache the results
        if self.config.use_caching:
            results_dict = [
                {
                    "question": r.question,
                    "computed_data": r.computed_data,
                    "explanation": r.explanation,
                    "visualization_code": r.visualization_code,
                    "title": r.title,
                    "category": r.category,
                }
                for r in self.research_results
            ]
            save_json_data(results_dict, "research_results.json")  # type: ignore

        print(f"Completed research for {len(self.research_results)} questions")
        return self.research_results

    def _conduct_research_for_question(
        self, question: ResearchQuestion
    ) -> Optional[ResearchResult]:
        """Conduct research for a single question with simplified steps"""
        try:
            # Step 1: Generate pandas code
            pandas_code = self._generate_pandas_code(question)
            if not pandas_code:
                print(f"Failed to generate pandas code for: {question.question}")
                return None

            # Step 2: Execute pandas code to get computed data
            computed_data = self._execute_pandas_query_for_computation(pandas_code)

            # Check if data is empty
            if not computed_data:
                print(f"Skipping question - no data returned: {question.question}")
                return None

            # Check if data is too large
            if len(computed_data) > 10000:
                print(
                    f"Skipping question - data too large: {question.question} | Size {len(computed_data)}"
                )
                return None

            # Generate visualization code, explanation, and title in parallel where possible
            # Phase 1: Run viz_code and title generation in parallel (independent)
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(2, self.config.max_workers)
            ) as executor:
                viz_future = executor.submit(
                    self._generate_visualization_code, question, computed_data
                )
                title_future = executor.submit(
                    self._generate_title, question, computed_data
                )

                viz_code = viz_future.result()
                title = title_future.result()

            # Phase 2: Generate explanation (depends on viz_code)
            explanation = self._generate_explanation(question, computed_data, viz_code)

            return ResearchResult(
                question=question.question,
                computed_data=computed_data,
                explanation=explanation,
                visualization_code=viz_code,
                title=title,
                category=question.category,
                source_columns=question.source_columns,
            )

        except Exception as e:
            print(f"Error conducting research for question '{question.question}': {e}")
            return None

    def _generate_pandas_code(self, question: ResearchQuestion) -> str:
        """Generate pandas code to compute data for the research question"""
        print(f"Generating pandas code for question: {question.question}")

        # Get sample data for source columns
        from utils.data_utils import sample_data

        sample_data_dict = sample_data(question.source_columns, sample_size=5)
        # Convert to safe string format to avoid f-string conflicts
        sample_data_result = "\n".join(
            [f"{col}: {values}" for col, values in sample_data_dict.items()]
        )

        system_prompt = load_prompt_template("sys_prompt_generate_pandas_code.md")

        user_prompt = load_prompt_template("user_prompt_generate_pandas_code.md")

        pandas_code = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "{question}": question.question,
                "{parent_question}": question.parent_question
                or "None - this is the parent question",
                "{visualization}": question.visualization,
                "{category}": question.category,
                "{source_columns}": str(question.source_columns),
                "{sample_data_result}": sample_data_result,
            },
        )

        # Clean the pandas code
        pandas_code = self._clean_markdown_output(pandas_code)

        return pandas_code

    def _clean_markdown_output(self, output: str) -> str:
        """Clean markdown formatting from LLM output"""
        output = output.strip()
        if output.startswith("```python"):
            output = output.split("```python")[1].split("```")[0].strip()
        elif output.startswith("```"):
            output = output.split("```")[1].split("```")[0].strip()
        return output

    def _execute_pandas_query_for_computation(self, pandas_code: str) -> List[Dict]:
        """Execute pandas query and return computed result"""
        try:
            import pandas as pd

            df = pd.read_csv("./dataset.csv")

            # Create execution environment
            local_vars = {"df": df, "pd": pd}

            # Execute the pandas code
            exec(pandas_code, {"pd": pd}, local_vars)

            # Get the result (should be stored in 'result' variable)
            if "result" in local_vars:
                result = local_vars["result"]
                # Convert to records format if it's a DataFrame
                if hasattr(result, "to_dict"):
                    return result.to_dict("records")
                # If result is already a list, return it
                elif isinstance(result, list):
                    return result
                # Otherwise, wrap single values or other types in a list
                else:
                    return [{"value": result}] if result is not None else []
            else:
                print("Warning: No 'result' variable found in pandas code execution")
                return []

        except Exception as e:
            print(f"Error executing pandas code: {e}")
            return []

    def _generate_visualization_code(
        self, question: ResearchQuestion, computed_data: Any
    ) -> str:
        """Generate Python matplotlib/seaborn code for the computed data"""
        # Use entire computed data, not just a sample
        full_data = json.dumps(computed_data, indent=2)

        system_prompt = load_prompt_template(
            "sys_prompt_generate_visualization_code.md"
        )
        user_prompt = load_prompt_template("user_prompt_generate_visualization_code.md")

        viz_code = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "{question}": question.question,
                "{visualization}": question.visualization,
                "{category}": question.category,
                "{full_data}": full_data,
            },
        )

        # Clean the code to remove markdown formatting
        viz_code = self._clean_markdown_output(viz_code)

        return viz_code

    def _generate_explanation(
        self, question: ResearchQuestion, computed_data: Any, viz_code: str
    ) -> str:
        """Generate 2-3 paragraph explanation of the data and visualization"""
        data_summary = str(computed_data)[:1000] if computed_data else "No data"

        system_prompt = load_prompt_template("sys_prompt_generate_explanation.md")
        user_prompt = load_prompt_template("user_prompt_generate_explanation.md")

        explanation = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "question": question.question,
                "data_summary": data_summary,
            },
            temperature=0.8,  # Higher temperature for more creative and varied explanations
        )

        return explanation

    def _generate_title(self, question: ResearchQuestion, computed_data: Any) -> str:
        """Generate a precise, compelling title for the research result"""
        data_summary = str(computed_data)[:500] if computed_data else "No data"

        system_prompt = load_prompt_template("sys_prompt_generate_title.md")
        user_prompt = load_prompt_template("user_prompt_generate_title.md")

        title = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "question": question.question,
                "data_summary": data_summary,
            },
        )

        return title.strip().strip('"')

    def _filter_quality_results_with_llm(self) -> List[ResearchResult]:
        """Use LLM agent to filter out non-renderable and redundant visualizations"""
        if not self.research_results:
            return []

        # Prepare results summary for LLM analysis
        results_summary = []
        for i, result in enumerate(self.research_results):
            summary = {
                "index": i,
                "question": result.question,
                "category": result.category,
                "has_data": bool(
                    result.computed_data and len(result.computed_data) > 0
                ),
                "has_visualization": bool(
                    result.visualization_code and result.visualization_code.strip()
                ),
                "data_size": len(result.computed_data) if result.computed_data else 0,
                "title": result.title,
            }
            results_summary.append(summary)

        system_prompt = load_prompt_template("sys_prompt_filter_quality_results.md")
        user_prompt = load_prompt_template("user_prompt_filter_quality_results.md")

        response = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "num_results": len(results_summary),
                "results_summary": json.dumps(results_summary, indent=2),
            },
        )

        try:
            from utils.llm_operations import extract_json_from_response

            selected_indices = extract_json_from_response(response)

            if isinstance(selected_indices, list):
                filtered_results = [
                    self.research_results[i]
                    for i in selected_indices
                    if 0 <= i < len(self.research_results)
                ]
                print(
                    f"LLM quality filtering: {len(self.research_results)} -> {len(filtered_results)} results"
                )
                return filtered_results
            else:
                print("LLM filtering failed, using all results")
                return self.research_results

        except Exception as e:
            print(f"Error in LLM filtering: {e}, using all results")
            return self.research_results

    def step3_arrange_results(self) -> Dict[str, Any]:
        """
        Step 3: Final Arrangement of Generated Research Output
        Organize results, generate title, introduction, conclusion, and arrange logically
        """
        print("Step 3: Arranging and Organizing Research Results")

        # Check cache first
        if self.config.use_caching:
            cached_arrangement = load_cached_json("final_arrangement.json")
            if cached_arrangement:
                print("Using cached final arrangement")
                return cached_arrangement

        # Filter out problematic results using LLM
        self.research_results = self._filter_quality_results_with_llm()

        # Generate overall title, introduction, and conclusion
        overall_title = self._generate_overall_title()
        introduction = self._generate_introduction()
        conclusion = self._generate_conclusion()

        # Arrange results in logical order
        ordered_results = self._arrange_results_logically()

        final_arrangement = {
            "title": overall_title,
            "introduction": introduction,
            "conclusion": conclusion,
            "results": ordered_results,
            "total_questions": len(self.research_questions),
            "total_results": len(self.research_results),
        }

        # Cache the arrangement
        if self.config.use_caching:
            save_json_data(final_arrangement, "final_arrangement.json")

        print(f"Arranged {len(ordered_results)} results with overall structure")
        return final_arrangement

    def _generate_overall_title(self) -> str:
        """Generate the best overall title for the research paper"""
        categories = list(set([r.category for r in self.research_results]))

        system_prompt = load_prompt_template("sys_prompt_generate_overall_title.md")
        user_prompt = load_prompt_template("user_prompt_generate_overall_title.md")

        title = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "num_results": len(self.research_results),
                "categories": ", ".join(categories),
                "dataset_keys": str(list(self.dataset_profile.keys())[:10]),
            },
        )

        return title.strip().strip('"')

    def _generate_introduction(self) -> str:
        """Generate comprehensive introduction for the report"""
        dataset_overview = {
            "columns": len(self.dataset_profile),
            "categories": list(set([r.category for r in self.research_results])),
        }

        system_prompt = load_prompt_template("sys_prompt_generate_introduction.md")
        user_prompt = load_prompt_template("user_prompt_generate_introduction.md")

        introduction = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "dataset_overview": json.dumps(dataset_overview, indent=2),
                "num_questions": len(self.research_questions),
                "num_results": len(self.research_results),
            },
        )

        return introduction

    def _generate_conclusion(self) -> str:
        """Generate comprehensive conclusion synthesizing all findings"""
        key_findings = [r.title for r in self.research_results[:10]]  # Top findings

        system_prompt = load_prompt_template("sys_prompt_generate_conclusion.md")
        user_prompt = load_prompt_template("user_prompt_generate_conclusion.md")

        conclusion = invoke_llm_with_prompt(
            system_content=system_prompt,
            prompt_template=user_prompt,
            replacements={
                "key_findings": chr(10).join(
                    ["- " + finding for finding in key_findings]
                ),
                "num_results": len(self.research_results),
            },
        )

        return conclusion

    def _arrange_results_logically(self) -> List[Dict[str, Any]]:
        """Arrange research results in logical order for the report"""
        # Group by category and level for logical flow
        grouped_results = {}
        for result in self.research_results:
            category = result.category
            if category not in grouped_results:
                grouped_results[category] = []
            grouped_results[category].append(result)

        # Sort each category by relevance/impact (using title length as proxy for complexity/importance)
        ordered_results = []
        for category in sorted(grouped_results.keys()):
            category_results = sorted(
                grouped_results[category], key=lambda x: len(x.title), reverse=True
            )
            ordered_results.extend(
                [
                    {
                        "title": r.title,
                        "question": r.question,
                        "explanation": r.explanation,
                        "visualization_code": r.visualization_code,
                        "computed_data": r.computed_data,
                        "category": r.category,
                    }
                    for r in category_results
                ]
            )

        return ordered_results
