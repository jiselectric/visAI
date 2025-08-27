import asyncio
import concurrent.futures
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from utils.file_operation import load_cached_json, load_prompt_template, save_json_data
from utils.llm_operations import invoke_llm_with_prompt


@dataclass
class ResearchConfig:
    depth: int = 3
    breadth: int = 4
    max_workers: int = 8
    use_caching: bool = True


@dataclass
class ResearchQuestion:
    question: str
    parent_question: Optional[str]
    level: int  # 0 for breadth questions, 1+ for depth questions
    visualizable: bool = True
    category: str = ""


@dataclass
class ResearchResult:
    question: str
    computed_data: Any
    explanation: str
    visualization_code: str
    title: str
    steps: List[str]
    category: str = ""


class Researcher:
    def __init__(self, config: ResearchConfig, dataset_profile: Dict):
        self.config = config
        self.dataset_profile = dataset_profile
        self.research_questions: List[ResearchQuestion] = []
        self.research_results: List[ResearchResult] = []

    def step1_generate_research_questions(self) -> List[ResearchQuestion]:
        """
        Step 1: Generate Research Questions
        1a. Generate breadth-amount of wide-ranging questions
        1b. For each breadth question, recursively generate depth-amount of follow-up questions
        """
        print("Step 1: Generating Research Questions")

        # Check cache first
        if self.config.use_caching:
            cached_questions = load_cached_json("research_questions.json")
            if cached_questions:
                print("Using cached research questions")
                self.research_questions = [
                    ResearchQuestion(**q) for q in cached_questions
                ]
                return self.research_questions

        # Step 1a: Generate breadth questions
        breadth_questions = self._generate_breadth_questions()

        # Step 1b: Generate depth questions in parallel
        depth_questions = self._generate_depth_questions_parallel(breadth_questions)

        self.research_questions = breadth_questions + depth_questions

        # Cache the results
        if self.config.use_caching:
            questions_dict = [
                {
                    "question": q.question,
                    "parent_question": q.parent_question,
                    "level": q.level,
                    "visualizable": q.visualizable,
                    "category": q.category,
                }
                for q in self.research_questions
            ]
            save_json_data(questions_dict, "research_questions.json")

        print(f"Generated {len(self.research_questions)} total research questions")
        return self.research_questions

    def _generate_breadth_questions(self) -> List[ResearchQuestion]:
        """Generate breadth-amount of wide-ranging questions covering different aspects of data"""
        print(f"  Generating {self.config.breadth} breadth questions...")

        dataset_summary = json.dumps(self.dataset_profile, indent=2)

        system_prompt = """You are an expert data analyst and researcher. Your task is to generate insightful, 
        visualizable research questions that explore different aspects of the dataset comprehensively.
        
        Generate questions that:
        1. Cover wide-ranging aspects of the data (temporal, categorical, numerical, relational)
        2. Are highly visualizable and would produce compelling charts
        3. Expose meaningful insights about the dataset
        4. Are answerable using the available data columns
        5. Would be interesting to both technical and non-technical audiences"""

        user_prompt = f"""Based on this dataset profile:
        
        {dataset_summary}
        
        Generate exactly {self.config.breadth} diverse research questions that cover different aspects of the data.
        Each question should be:
        - Specific and actionable
        - Visualizable (can be answered with charts/graphs)
        - Insightful (reveals meaningful patterns or trends)
        
        Return the response as a JSON array with objects containing:
        - "question": the research question
        - "category": the category/aspect it explores (e.g., "temporal", "categorical", "correlation", "distribution")
        - "visualizable": true
        
        Example format:
        [
          {{"question": "How has the number of publications changed over time for each conference?", "category": "temporal", "visualizable": true}},
          {{"question": "What is the distribution of paper types across different conferences?", "category": "categorical", "visualizable": true}}
        ]"""

        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        try:
            from utils.llm_operations import extract_json_from_response

            questions_data = extract_json_from_response(response)

            # Check if it's an error response
            if isinstance(questions_data, dict) and "error" in questions_data:
                raise json.JSONDecodeError(questions_data["error"], "", 0)

            breadth_questions = []

            for i, q_data in enumerate(questions_data[: self.config.breadth]):
                question = ResearchQuestion(
                    question=q_data["question"],
                    parent_question=None,
                    level=0,
                    visualizable=q_data.get("visualizable", True),
                    category=q_data.get("category", f"category_{i}"),
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
                    visualizable=True,
                    category=f"fallback_{i}",
                )
                for i in range(self.config.breadth)
            ]

    def _generate_depth_questions_parallel(
        self, breadth_questions: List[ResearchQuestion]
    ) -> List[ResearchQuestion]:
        """Generate depth questions in parallel for each breadth question"""
        print(
            f"  Generating {self.config.depth} follow-up questions for each breadth question in parallel..."
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
        dataset_summary = json.dumps(self.dataset_profile, indent=2)

        system_prompt = """You are an expert data analyst. Given a parent research question about a dataset, 
        generate follow-up questions that dive deeper into the insights the parent question reveals.
        
        The follow-up questions should:
        1. Build upon insights from the parent question
        2. Be more specific and focused
        3. Be highly visualizable
        4. Explore sub-patterns, correlations, or detailed aspects
        5. Be answerable with the available data"""

        user_prompt = f"""Dataset profile:
        {dataset_summary}
        
        Parent question: "{parent_question.question}"
        Category: {parent_question.category}
        
        Generate exactly {self.config.depth} follow-up questions that dive deeper into this parent question.
        
        Return as JSON array with format:
        [
          {{"question": "specific follow-up question", "category": "refined_category", "visualizable": true}}
        ]"""

        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        try:
            from utils.llm_operations import extract_json_from_response

            questions_data = extract_json_from_response(response)

            # Check if it's an error response
            if isinstance(questions_data, dict) and "error" in questions_data:
                raise json.JSONDecodeError(questions_data["error"], "", 0)

            depth_questions = []

            for level in range(1, self.config.depth + 1):
                if level - 1 < len(questions_data):
                    q_data = questions_data[level - 1]
                    question = ResearchQuestion(
                        question=q_data["question"],
                        parent_question=parent_question.question,
                        level=level,
                        visualizable=q_data.get("visualizable", True),
                        category=q_data.get("category", parent_question.category),
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
                    visualizable=True,
                    category=parent_question.category,
                )
                for i in range(1, self.config.depth + 1)
            ]

    def step2_conduct_research(self) -> List[ResearchResult]:
        """
        Step 2: Conduct Research from Generated Questions
        For each question: establish steps, compute data, create visualization, generate explanation
        """
        print("Step 2: Conducting Research for All Questions")

        # Check cache first
        if self.config.use_caching:
            cached_results = load_cached_json("research_results.json")
            if cached_results:
                print("Using cached research results")
                self.research_results = [ResearchResult(**r) for r in cached_results]
                return self.research_results

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
                    "steps": r.steps,
                    "category": r.category,
                }
                for r in self.research_results
            ]
            save_json_data(results_dict, "research_results.json")

        print(f"Completed research for {len(self.research_results)} questions")
        return self.research_results

    def _conduct_research_for_question(
        self, question: ResearchQuestion
    ) -> Optional[ResearchResult]:
        """Conduct research for a single question with detailed steps"""
        try:
            # Step 2a: Establish research steps (max 10)
            steps = self._establish_research_steps(question)

            # Step 2b: Compute data using pandas
            computed_data = self._compute_data_for_question(question, steps)

            if not computed_data or len(computed_data) > 1000:
                print(
                    f"Skipping question - data too large or empty: {question.question}"
                )
                return None

            # Step 2c: Generate Python visualization code
            viz_code = self._generate_visualization_code(question, computed_data)

            # Step 2d: Generate explanation (2-3 paragraphs)
            explanation = self._generate_explanation(question, computed_data, viz_code)

            # Step 2e: Generate precise title
            title = self._generate_title(question, computed_data)

            return ResearchResult(
                question=question.question,
                computed_data=computed_data,
                explanation=explanation,
                visualization_code=viz_code,
                title=title,
                steps=steps,
                category=question.category,
            )

        except Exception as e:
            print(f"Error conducting research for question '{question.question}': {e}")
            return None

    def _establish_research_steps(self, question: ResearchQuestion) -> List[str]:
        """Establish well-designed steps to effectively answer the research question"""
        dataset_profile_str = json.dumps(self.dataset_profile, indent=2)

        system_prompt = """You are a methodical data analyst. Given a research question and dataset profile,
        create a step-by-step plan (maximum 10 steps) to effectively answer the question using data analysis.
        
        You can derive new columns from existing ones (e.g., PageCount = LastPage - FirstPage).
        Focus on the analytical approach and what computations are needed."""

        user_prompt = f"""Dataset profile: {dataset_profile_str}
        
        Research question: "{question.question}"
        Parent question context: {question.parent_question or "None"}
        
        Create a detailed step-by-step plan to answer this question. Each step should be specific and actionable.
        Consider deriving new metrics from existing columns if needed.
        
        Return as JSON array of strings:
        ["Step 1 description", "Step 2 description", ...]
        
        Maximum 10 steps."""

        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        try:
            from utils.llm_operations import extract_json_from_response

            steps_data = extract_json_from_response(response)

            # Check if it's an error response or not a list
            if isinstance(steps_data, dict) and "error" in steps_data:
                raise json.JSONDecodeError(steps_data["error"], "", 0)

            if isinstance(steps_data, list):
                return steps_data[:10]  # Ensure max 10 steps
            else:
                raise json.JSONDecodeError("Expected list of steps", "", 0)
        except json.JSONDecodeError:
            # Fallback steps
            return [
                "Load and examine the dataset",
                "Identify relevant columns for analysis",
                "Clean and prepare the data",
                "Perform statistical analysis",
                "Generate visualizations",
                "Interpret results",
            ]

    def _compute_data_for_question(
        self, question: ResearchQuestion, steps: List[str]
    ) -> Any:
        """Compute data for the research question using pandas"""
        dataset_profile_str = json.dumps(self.dataset_profile, indent=2)
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])

        system_prompt = """You are a data analyst expert in pandas. Generate pandas code to compute data 
        that answers the research question following the established steps. The code should return processed 
        data suitable for visualization.
        
        You can derive new columns from existing ones based on the dataset profile provided."""

        user_prompt = f"""Dataset profile: {dataset_profile_str}
        
        Research question: "{question.question}"
        Research steps: {steps_text}
        
        Generate pandas code to compute the data needed to answer this question.
        The dataset is loaded as 'df' (pandas DataFrame).
        Return ONLY the pandas code without markdown formatting or explanations.
        The code should end with a variable that contains the computed result."""

        pandas_code = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        # Clean the code
        pandas_code = pandas_code.strip()
        if pandas_code.startswith("```python"):
            pandas_code = pandas_code.split("```python")[1].split("```")[0].strip()
        elif pandas_code.startswith("```"):
            pandas_code = pandas_code.split("```")[1].split("```")[0].strip()

        # Execute the pandas code
        try:
            df = pd.read_csv("./dataset.csv")
            local_vars = {"df": df, "pd": pd}
            exec(pandas_code, {"pd": pd}, local_vars)

            # Find the result variable (last assignment or common result names)
            possible_result_vars = [
                "result",
                "computed_data",
                "data",
                "analysis_result",
            ]
            for var_name in reversed(list(local_vars.keys())):
                if var_name not in ["df", "pd"] and not var_name.startswith("_"):
                    result_data = local_vars[var_name]
                    if hasattr(result_data, "to_dict"):
                        return result_data.to_dict("records")
                    return result_data

            return None

        except Exception as e:
            print(f"Error executing pandas code: {e}")
            return None

    def _generate_visualization_code(
        self, question: ResearchQuestion, computed_data: Any
    ) -> str:
        """Generate Python visualization code for the computed data"""
        data_sample = json.dumps(
            computed_data[:5] if isinstance(computed_data, list) else computed_data,
            indent=2,
        )

        system_prompt = """You are a data visualization expert. Generate Python code using matplotlib/seaborn 
        to create an effective visualization for the given data and research question."""

        user_prompt = f"""Research question: "{question.question}"
        
        Sample computed data: {data_sample}
        
        Generate Python visualization code that:
        1. Uses matplotlib/seaborn
        2. Creates an appropriate chart type for the question
        3. Includes proper labels, title, and formatting
        4. Is complete and executable
        
        Return ONLY the Python code without markdown formatting."""

        viz_code = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        # Clean the code
        if viz_code.startswith("```python"):
            viz_code = viz_code.split("```python")[1].split("```")[0].strip()
        elif viz_code.startswith("```"):
            viz_code = viz_code.split("```")[1].split("```")[0].strip()

        return viz_code

    def _generate_explanation(
        self, question: ResearchQuestion, computed_data: Any, viz_code: str
    ) -> str:
        """Generate 2-3 paragraph explanation of the data and visualization"""
        data_summary = str(computed_data)[:1000] if computed_data else "No data"

        system_prompt = """You are a data storytelling expert. Generate a clear, insightful explanation 
        (2-3 paragraphs) that describes what the data reveals and what insights can be drawn from the visualization."""

        user_prompt = f"""Research question: "{question.question}"
        
        Computed data summary: {data_summary}
        Visualization approach: {viz_code[:200]}...
        
        Write 2-3 paragraphs explaining:
        1. What the data shows/reveals
        2. Key insights and patterns
        3. Implications or significance of the findings
        
        Make it accessible to both technical and non-technical audiences."""

        explanation = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        return explanation

    def _generate_title(self, question: ResearchQuestion, computed_data: Any) -> str:
        """Generate a precise, compelling title for the research result"""
        data_summary = str(computed_data)[:500] if computed_data else "No data"

        system_prompt = """You are an expert at creating compelling, precise titles for data analysis results. 
        Generate a title that captures the key finding or insight."""

        user_prompt = f"""Research question: "{question.question}"
        Data summary: {data_summary}
        
        Generate a precise, compelling title (maximum 12 words) that captures the key insight or finding.
        The title should be engaging and informative."""

        title = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        return title.strip().strip('"')

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

        system_prompt = """You are an expert research paper writer. Generate a compelling overall title 
        for a comprehensive data visualization report."""

        user_prompt = f"""This research report analyzes a dataset with {len(self.research_results)} findings 
        across categories: {', '.join(categories)}.
        
        The dataset appears to be about: {list(self.dataset_profile.keys())[:10]}
        
        Generate a compelling, professional title (maximum 15 words) for this comprehensive data analysis report."""

        title = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        return title.strip().strip('"')

    def _generate_introduction(self) -> str:
        """Generate comprehensive introduction for the report"""
        dataset_overview = {
            "columns": len(self.dataset_profile),
            "categories": list(set([r.category for r in self.research_results])),
        }

        system_prompt = """You are an expert research writer. Generate a comprehensive introduction 
        for a data analysis report that sets context and objectives."""

        user_prompt = f"""Dataset overview: {json.dumps(dataset_overview, indent=2)}
        
        Number of research questions analyzed: {len(self.research_questions)}
        Number of successful analyses: {len(self.research_results)}
        
        Write a comprehensive introduction (3-4 paragraphs) that:
        1. Introduces the dataset and its significance
        2. Explains the research methodology and approach
        3. Outlines what the report will cover
        4. Sets expectations for the insights to be presented"""

        introduction = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )

        return introduction

    def _generate_conclusion(self) -> str:
        """Generate comprehensive conclusion synthesizing all findings"""
        key_findings = [r.title for r in self.research_results[:10]]  # Top findings

        system_prompt = """You are an expert research writer. Generate a comprehensive conclusion 
        that synthesizes findings and provides broader insights."""

        user_prompt = f"""Key findings from the analysis:
        {chr(10).join(['- ' + finding for finding in key_findings])}
        
        Total analyses conducted: {len(self.research_results)}
        
        Write a comprehensive conclusion (3-4 paragraphs) that:
        1. Summarizes the key findings and patterns
        2. Discusses broader implications
        3. Highlights the most significant insights
        4. Suggests potential future research directions"""

        conclusion = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
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
                        "steps": r.steps,
                    }
                    for r in category_results
                ]
            )

        return ordered_results
