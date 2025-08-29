import asyncio
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

            if not computed_data or (
                isinstance(computed_data, list) and len(computed_data) > 10000
            ):
                print(
                    f"Skipping question - data too large or empty: {question.question} | Size {len(computed_data)}"
                )
                return None

            # Generate visualization code, explanation, and title (keeping existing methods)
            viz_code = self._generate_visualization_code(question, computed_data)
            explanation = self._generate_explanation(question, computed_data, viz_code)
            title = self._generate_title(question, computed_data)

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

        system_prompt = """You are a highly skilled data analyst with expertise in pandas. You are given a research question, target visualization type, visualization category, the source columns and 5 sample data points for each source column. Your task is to generate an executable pandas query to accurately compute the data needed to answer the research question.

        CRITICAL REQUIREMENTS:
        1. Return ONLY the pandas code - no explanations, no markdown delimiters, no extra text
        2. The code must use ONLY the provided source columns - do not access or create arbitrary columns
        3. The code must be executable Python pandas code
        4. Use 'df' as the DataFrame variable name
        5. The final result should be stored in a variable that can be converted to records format
        6. Handle missing/null values appropriately"""

        user_prompt = """Research Question: "{question}"
        Parent Question Context: {parent_question}
        Visualization Type: {visualization}
        Category: {category}
        Source Columns: {source_columns}

        Sample Data for Source Columns:
        {sample_data_result}

        Examples:

        Example 1:
        Question: "How has the number of publications changed over time for each Conference?"
        Source Columns: ["Year", "Conference"]
        Code:
        result = df.groupby(['Year', 'Conference']).size().reset_index(name='publication_count')

        Example 2: 
        Question: "What is the distribution of PaperType across Conferences?"
        Source Columns: ["PaperType", "Conference"]
        Code:
        result = df.groupby(['Conference', 'PaperType']).size().reset_index(name='count')

        Example 3:
        Question: "Is there a correlation between Downloads_Xplore and AminerCitationCount?"
        Source Columns: ["Downloads_Xplore", "AminerCitationCount"]
        Code:
        result = df[['Downloads_Xplore', 'AminerCitationCount']].dropna()

        Example 4:
        Question: "Which Authors have contributed the most papers overall?"
        Source Columns: ["Authors"]
        Code:
        author_counts = df['Authors'].str.split(';').explode().str.strip().value_counts().head(20)
        result = author_counts.reset_index()
        result.columns = ['Author', 'paper_count']

        Example 5:
        Question: "How does the distribution of AminerCitationCount differ across Conferences?"
        Source Columns: ["AminerCitationCount", "Conference"]
        Code:
        result = df[['Conference', 'AminerCitationCount']].dropna()

        Example 6:
        Question: "What is the year-over-year growth rate of publications for each Conference?"
        Source Columns: ["Year", "Conference"]
        Code:
        yearly_counts = df.groupby(['Conference', 'Year']).size().reset_index(name='count')
        yearly_counts = yearly_counts.sort_values(['Conference', 'Year'])
        yearly_counts['growth_rate'] = yearly_counts.groupby('Conference')['count'].pct_change() * 100
        result = yearly_counts.dropna()

        Example 7:
        Question: "Which Conferences have the highest average citations per paper across different paper types?"
        Source Columns: ["Conference", "PaperType", "AminerCitationCount"]
        Code:
        avg_citations = df.groupby(['Conference', 'PaperType'])['AminerCitationCount'].agg(['mean', 'count']).reset_index()
        avg_citations.columns = ['Conference', 'PaperType', 'avg_citations', 'paper_count']
        result = avg_citations[avg_citations['paper_count'] >= 5].sort_values('avg_citations', ascending=False)

        Example 8:
        Question: "How do download patterns correlate with citation counts for papers published in different time periods?"
        Source Columns: ["Year", "Downloads_Xplore", "AminerCitationCount"]
        Code:
        df_clean = df[['Year', 'Downloads_Xplore', 'AminerCitationCount']].dropna()
        df_clean['period'] = pd.cut(df_clean['Year'], bins=[2005, 2010, 2015, 2020, 2025], labels=['2006-2010', '2011-2015', '2016-2020', '2021+'])
        result = df_clean.groupby('period').agg({
            'Downloads_Xplore': ['mean', 'std'],
            'AminerCitationCount': ['mean', 'std']
        }).round(2).reset_index()
        result.columns = ['period', 'avg_downloads', 'std_downloads', 'avg_citations', 'std_citations']

        Example 9:
        Question: "What is the distribution of paper lengths and how does it vary by Conference and PaperType?"
        Source Columns: ["FirstPage", "LastPage", "Conference", "PaperType"]
        Code:
        df_pages = df[['FirstPage', 'LastPage', 'Conference', 'PaperType']].dropna()
        df_pages['page_length'] = df_pages['LastPage'] - df_pages['FirstPage'] + 1
        df_pages = df_pages[df_pages['page_length'] > 0]  # Filter valid page lengths
        result = df_pages.groupby(['Conference', 'PaperType'])['page_length'].agg(['mean', 'median', 'std', 'count']).round(2).reset_index()
        result.columns = ['Conference', 'PaperType', 'avg_pages', 'median_pages', 'std_pages', 'paper_count']

        Generate pandas code that computes the data needed to answer this research question. The code should:
        - Use only the specified source columns
        - Handle data cleaning/filtering as needed
        - Compute aggregations, groupings, or transformations as required
        - Return data suitable for the specified visualization type
        - Store the final result in a variable named 'result'

        Return ONLY the executable pandas code."""

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

    def _execute_pandas_query_for_computation(self, pandas_code: str) -> Any:
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
                return result
            else:
                print("Warning: No 'result' variable found in pandas code execution")
                return None

        except Exception as e:
            print(f"Error executing pandas code: {e}")
            return None

    def _establish_research_steps(self, question: ResearchQuestion) -> List[str]:
        """Establish well-designed steps to effectively answer the research question"""
        filtered_dataset_profile = {
            k: v
            for k, v in self.dataset_profile.items()
            if k in question.source_columns
        }
        filtered_dataset_profile_json = json.dumps(filtered_dataset_profile, indent=2)

        system_prompt = """You are a methodical data analyst. Given a research question and dataset profile,
        create a step-by-step plan (maximum 10 steps) to effectively answer the question using data analysis.
        
        You can derive new columns from existing ones (e.g., PageCount = LastPage - FirstPage, TotalCitations = CitationCount_CrossRef + AminerCitationCount).
        Focus on the analytical approach and what computations are needed."""

        user_prompt = f"""Dataset profile: {filtered_dataset_profile_json}
        
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
        """Generate Python matplotlib/seaborn code for the computed data"""
        # Use entire computed data, not just a sample
        full_data = json.dumps(computed_data, indent=2)

        system_prompt = """You are a data visualization expert specializing in Python matplotlib and seaborn. You are given a research question, suggested visualization type, category, and computed data. Your task is to generate executable Python code that creates an effective visualization.

        CRITICAL REQUIREMENTS:
        1. Return ONLY executable Python code - no explanations, no markdown delimiters, no extra text
        2. Use matplotlib and seaborn for visualizations
        3. The data is already loaded in a variable called 'data' as a list of dictionaries
        4. Convert the data to a pandas DataFrame using pd.DataFrame(data)
        5. Save the plot using plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        6. Include proper titles, axis labels, and legends
        7. Handle data cleaning and type conversion as needed
        8. Choose the most appropriate visualization type based on the data structure and research question
        9. CRITICAL: For frequency analysis (keyword charts), NEVER use traditional bar charts - use text size to represent frequency instead
        10. CRITICAL: When the suggested visualization is 'keyword chart', create a visualization where text size represents frequency, not bar height"""

        user_prompt = """Research Question: "{question}"
        Suggested Visualization: {visualization}
        Category: {category}

        Computed Data: {full_data}

        Examples:

        Example 1 - Line Chart (Temporal + Categorical):
        df = pd.DataFrame(data)
        plt.figure(figsize=(12, 8))
        sns.lineplot(data=df, x='Year', y='publication_count', hue='Conference', marker='o')
        plt.title('Publications Over Time by Conference')
        plt.xlabel('Year')
        plt.ylabel('Number of Publications')
        plt.legend(title='Conference')
        plt.tight_layout()

        Example 2 - Bar Chart (Categorical):
        df = pd.DataFrame(data)
        plt.figure(figsize=(12, 8))
        sns.barplot(data=df, x='Conference', y='count', hue='PaperType')
        plt.title('Distribution of Paper Types by Conference')
        plt.xlabel('Conference')
        plt.ylabel('Count')
        plt.legend(title='Paper Type')
        plt.xticks(rotation=45)
        plt.tight_layout()

        Example 3 - Scatter Plot (Correlation):
        df = pd.DataFrame(data)
        plt.figure(figsize=(10, 8))
        sns.scatterplot(data=df, x='Downloads_Xplore', y='AminerCitationCount', alpha=0.7, s=60)
        plt.title('Downloads vs Citations Correlation')
        plt.xlabel('Downloads')
        plt.ylabel('Citations')
        plt.tight_layout()

        Example 4 - Horizontal Bar Chart (Ranking):
        df = pd.DataFrame(data)
        df = df.sort_values('paper_count', ascending=True)
        plt.figure(figsize=(10, 8))
        sns.barplot(data=df, y='Author', x='paper_count', orient='h')
        plt.title('Top Authors by Publication Count')
        plt.xlabel('Publication Count')
        plt.ylabel('Author')
        plt.tight_layout()

        Example 5 - Box Plot (Distribution):
        df = pd.DataFrame(data)
        plt.figure(figsize=(10, 8))
        sns.boxplot(data=df, x='Conference', y='AminerCitationCount')
        plt.title('Citation Distribution by Conference')
        plt.xlabel('Conference')
        plt.ylabel('Citation Count')
        plt.xticks(rotation=45)
        plt.tight_layout()

        Example 6 - Histogram (Distribution):
        df = pd.DataFrame(data)
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x='AminerCitationCount', bins=20, kde=True)
        plt.title('Distribution of Citation Counts')
        plt.xlabel('Citation Count')
        plt.ylabel('Frequency')
        plt.tight_layout()

        Example 7 - Heatmap (Correlation Matrix):
        df = pd.DataFrame(data)
        pivot_df = df.pivot_table(values='avg_citations', index='Conference', columns='PaperType', fill_value=0)
        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot_df, annot=True, cmap='viridis', fmt='.1f')
        plt.title('Average Citations by Conference and Paper Type')
        plt.tight_layout()

        Example 8 - Word Cloud (Text Frequency Analysis):
        df = pd.DataFrame(data)
        from wordcloud import WordCloud
        import re
        
        # Sort by frequency
        df_sorted = df.sort_values('count', ascending=False).head(50)
        
        # Prepare text data with frequency weighting
        text_data = []
        for _, row in df_sorted.iterrows():
            text = str(row.iloc[0]).strip()
            count = int(row['count'])
            
            # Clean text
            cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            # Weight by frequency
            for _ in range(min(count, 20)):
                text_data.append(cleaned_text)
        
        # Create word cloud
        full_text = ' '.join(text_data)
        plt.figure(figsize=(12, 8))
        wordcloud = WordCloud(
            width=1200, height=800, background_color='white',
            colormap='viridis', max_words=50, relative_scaling=0.5,
            min_font_size=12, max_font_size=80
        ).generate(full_text)
        
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud (Size Represents Frequency)')
        plt.tight_layout()

        Based on the research question, data structure, and suggested visualization type, generate the most appropriate Python matplotlib/seaborn code. The code should:
        - Convert the data list to a pandas DataFrame
        - Choose the most suitable chart type for the data and question
        - Include proper titles, axis labels, and legends
        - Handle data cleaning and formatting as needed
        - Use appropriate figure sizes and styling
        - Save the plot to chart_path with high quality
        - For keyword charts: Use text size to represent frequency, not traditional bar charts

        Return ONLY the executable Python code."""

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

        # Validate that keyword charts don't use traditional bar charts
        if question.visualization.lower() == "keyword chart":
            viz_code = self._validate_keyword_chart(viz_code)

        return viz_code

    def _validate_keyword_chart(self, viz_code: str) -> str:
        """Ensure keyword charts don't use traditional bar charts"""
        # Check if the code contains bar chart elements
        if any(
            term in viz_code.lower()
            for term in ["barplot", "bar(", "plt.bar", "sns.bar"]
        ):
            # Replace with proper keyword chart implementation
            replacement_code = """df = pd.DataFrame(data)
# Create proper word cloud using WordCloud library
from wordcloud import WordCloud
import re

# Sort by frequency
df_sorted = df.sort_values('count', ascending=False).head(50)  # Top 50 items

# Prepare text data with frequency weighting
text_data = []
for _, row in df_sorted.iterrows():
    # Get text and frequency
    text = str(row.iloc[0]).strip()
    count = int(row['count'])
    
    # Clean text (remove special characters, normalize)
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # Add text multiple times based on frequency for proper weighting
    for _ in range(min(count, 20)):  # Cap repetition at 20 to avoid memory issues
        text_data.append(cleaned_text)

# Join all text
full_text = ' '.join(text_data)

# Create WordCloud with proper parameters
plt.figure(figsize=(12, 8))
wordcloud = WordCloud(
    width=1200,
    height=800,
    background_color='white',
    colormap='viridis',
    max_words=50,
    relative_scaling=0.5,
    min_font_size=12,
    max_font_size=80,
    prefer_horizontal=0.7,
    collocation_threshold=30
).generate(full_text)

# Display the word cloud
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Most Frequent Items (Word Size Represents Frequency)', fontsize=16, fontweight='bold')
plt.tight_layout()"""
            return replacement_code

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
                    }
                    for r in category_results
                ]
            )

        return ordered_results
