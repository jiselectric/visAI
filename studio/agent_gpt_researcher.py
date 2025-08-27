"""
GPT-Researcher Inspired Data Analysis Agent
Implements recursive query generation and deep research for dataset analysis
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Counter, Dict, List, Optional, Set, Union

import pandas as pd
from helpers import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict
from utils.data_utils import (
    execute_pandas_query_for_computation,
    generate_dataset_summary,
    sample_data,
)
from utils.file_operation import (
    clean_markdown_output,
    load_cached_json,
    read_csv_data,
    save_json_data,
)
from utils.generate_dataset_profile import generate_dataset_profile
from utils.llm_operations import extract_json_from_response, invoke_llm_with_prompt

# Type alias for JSON-compatible types
JSONType = Union[str, int, float, bool, None, Dict[str, "JSONType"], List["JSONType"]]


@dataclass
class DataQuery:
    """Represents a data analysis query with research metadata"""

    query: str
    analysis_type: str
    key_columns: List[str]
    expected_chart_type: str
    research_goal: str = ""
    depth_level: int = 1
    parent_query: str = ""
    learnings: List[str] = None

    def __post_init__(self):
        if self.learnings is None:
            self.learnings = []


@dataclass
class ResearchProgress:
    """Track progress through deep research"""

    current_depth: int = 1
    total_depth: int = 2
    current_breadth: int = 0
    total_breadth: int = 4
    current_query: Optional[str] = None
    total_queries: int = 0
    completed_queries: int = 0


class State(TypedDict):
    # Keep existing dataset components
    dataset_profile: JSONType
    dataset_info: JSONType
    dataset_summary: JSONType
    # Deep research components
    initial_queries: JSONType  # GPT-Researcher inspired initial query generation
    research_results: JSONType  # Deep recursive research results
    final_report: JSONType  # Comprehensive research report


class DataResearchConductor:
    """
    Data-focused research conductor inspired by GPT-Researcher
    Implements recursive query generation and deep analysis
    """

    def __init__(self, dataset_profile: Dict, dataset_info: Dict, config: Dict = None):
        self.dataset_profile = dataset_profile
        self.dataset_info = dataset_info
        self.config = config or {}

        # Deep research configuration (inspired by GPT-Researcher)
        self.breadth = self.config.get("deep_research_breadth", 4)
        self.depth = self.config.get("deep_research_depth", 2)
        self.concurrency_limit = self.config.get("deep_research_concurrency", 2)
        self.max_queries_per_level = self.config.get("max_queries_per_level", 6)

        # Research tracking
        self.all_learnings = []
        self.all_queries: List[DataQuery] = []
        self.research_context = []
        self.visited_patterns = set()  # Track analyzed patterns to avoid duplication

        # Get LLM
        self.llm = get_llm(temperature=0.1, max_tokens=4096)

    async def generate_initial_research_queries(
        self, num_queries: int = None
    ) -> List[DataQuery]:
        """Generate initial research queries inspired by GPT-Researcher methodology"""
        if num_queries is None:
            num_queries = self.breadth

        print(f"🔍 Generating {num_queries} initial research queries...")

        # Check cache
        cached_queries = load_cached_json("initial_research_queries.json")
        if cached_queries:
            print("Using cached initial research queries")
            return [DataQuery(**q) for q in cached_queries]

        system_prompt = """
        You are an AI research assistant inspired by GPT-Researcher methodology.
        Generate diverse, insightful research queries that explore different dimensions of the dataset.
        
        Focus on creating queries that:
        1. Explore temporal patterns and trends
        2. Investigate statistical distributions and outliers
        3. Examine relationships and correlations between variables
        4. Compare different categories or segments
        5. Identify key performance metrics and anomalies
        6. Can lead to follow-up questions for deeper investigation
        """

        # Get dataset overview for context
        dataset_overview = {
            "shape": self.dataset_profile.get("shape", "unknown"),
            "columns": list(self.dataset_profile.keys())[:20],  # Limit for prompt size
            "sample_insights": self._extract_key_dataset_insights(),
        }

        prompt = f"""
        Based on this dataset profile, generate {num_queries} diverse research queries for comprehensive analysis:

        Dataset Overview:
        {json.dumps(dataset_overview, indent=2)}

        Generate queries that would create a compelling research narrative exploring:
        - Temporal trends and patterns (if time data exists)
        - Statistical distributions and data quality issues
        - Relationships between different variables
        - Comparative analysis across categories
        - Performance metrics and outliers
        - Business insights and actionable findings

        IMPORTANT: Include diverse visualization types for compelling analysis:
        - Interactive scatter plots (for correlations)
        - Line charts (for trends over time)
        - Heatmaps (for correlation matrices or cross-tabulations)
        - Bar charts (for categorical comparisons)
        - Histograms (for distributions)
        - Box plots (for outlier detection)

        For each query, provide:
        - A clear, specific research question
        - The type of analysis needed
        - Key columns to focus on
        - Expected visualization type (ensure variety)
        - Research goal explaining what insight this seeks

        Return JSON:
        {{
            "queries": [
                {{
                    "query": "Specific research question about the data",
                    "analysis_type": "trend|distribution|comparison|correlation|outlier|performance",
                    "key_columns": ["relevant", "column", "names"],
                    "expected_chart_type": "scatter|line|heatmap|bar|histogram|box",
                    "research_goal": "What specific insight or pattern this query aims to uncover"
                }}
            ]
        }}
        """

        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=prompt, replacements={}
        )

        queries_data = extract_json_from_response(response)
        queries = []

        for i, q_data in enumerate(queries_data.get("queries", [])[:num_queries]):
            query = DataQuery(
                query=q_data["query"],
                analysis_type=q_data.get("analysis_type", "general"),
                key_columns=q_data.get("key_columns", []),
                expected_chart_type=q_data.get("expected_chart_type", "bar"),
                research_goal=q_data.get("research_goal", ""),
                depth_level=1,
                parent_query="",
            )
            queries.append(query)

        # Cache results
        query_dicts = [self._query_to_dict(q) for q in queries]
        save_json_data(query_dicts, "initial_research_queries.json", "./datasets")

        return queries

    def _extract_key_dataset_insights(self) -> List[str]:
        """Extract key insights from dataset profile to guide query generation"""
        insights = []

        # Check for time-related columns
        time_columns = [
            col
            for col in self.dataset_profile.keys()
            if any(
                time_word in col.lower()
                for time_word in ["date", "time", "year", "month", "day"]
            )
        ]
        if time_columns:
            insights.append(f"Contains time-related data: {time_columns}")

        # Check for numeric columns with interesting distributions
        numeric_insights = []
        for col, profile in self.dataset_profile.items():
            if profile.get("type_inferred") == "continuous":
                stats = profile.get("summary_stats", {})
                if stats.get("std", 0) > stats.get("mean", 0):
                    numeric_insights.append(f"{col} has high variability")

        if numeric_insights:
            insights.extend(numeric_insights[:3])  # Limit insights

        # Check for categorical columns with many categories
        categorical_insights = []
        for col, profile in self.dataset_profile.items():
            if profile.get("type_inferred") == "categorical":
                unique_count = profile.get("distinct_values", 0)
                if unique_count > 10:
                    categorical_insights.append(f"{col} has {unique_count} categories")

        if categorical_insights:
            insights.extend(categorical_insights[:2])

        return insights[:5]  # Limit to 5 key insights

    async def conduct_deep_research(
        self, initial_queries: List[DataQuery], on_progress=None
    ) -> Dict[str, Any]:
        """
        Conduct deep recursive research inspired by GPT-Researcher
        """
        print(
            f"🔬 Starting deep research with {len(initial_queries)} initial queries..."
        )
        print(
            f"   Breadth: {self.breadth}, Depth: {self.depth}, Concurrency: {self.concurrency_limit}"
        )

        start_time = time.time()
        progress = ResearchProgress(
            total_depth=self.depth, total_breadth=len(initial_queries)
        )

        all_results = []
        all_learnings = []
        all_context = []

        # Process initial queries with concurrency control
        semaphore = asyncio.Semaphore(self.concurrency_limit)

        async def process_single_query(query: DataQuery) -> Dict[str, Any]:
            async with semaphore:
                return await self._research_single_query(query, progress, on_progress)

        # Execute initial queries
        print(f"📊 Processing {len(initial_queries)} initial queries...")
        tasks = [process_single_query(query) for query in initial_queries]
        initial_results = await asyncio.gather(*tasks)
        initial_results = [r for r in initial_results if r is not None]

        all_results.extend(initial_results)

        # Extract learnings and generate follow-up queries for deeper research
        for result in initial_results:
            all_learnings.extend(result.get("learnings", []))
            if result.get("context"):
                all_context.append(result["context"])

        # Recursive deeper research
        current_depth = 1
        current_queries = initial_queries.copy()

        while current_depth < self.depth and current_queries:
            current_depth += 1
            progress.current_depth = current_depth

            print(f"🔍 Generating follow-up queries for depth level {current_depth}...")

            # Generate follow-up queries based on current results
            follow_up_queries = await self._generate_follow_up_queries(
                current_queries, all_learnings, depth_level=current_depth
            )

            if not follow_up_queries:
                print(f"   No follow-up queries generated for depth {current_depth}")
                break

            print(
                f"📊 Processing {len(follow_up_queries)} follow-up queries at depth {current_depth}..."
            )
            progress.total_breadth = len(follow_up_queries)
            progress.current_breadth = 0

            # Process follow-up queries
            tasks = [process_single_query(query) for query in follow_up_queries]
            deeper_results = await asyncio.gather(*tasks)
            deeper_results = [r for r in deeper_results if r is not None]

            all_results.extend(deeper_results)

            # Update learnings and context
            for result in deeper_results:
                all_learnings.extend(result.get("learnings", []))
                if result.get("context"):
                    all_context.append(result["context"])

            # Prepare for next iteration
            current_queries = follow_up_queries

        # Synthesize all research results
        end_time = time.time()
        execution_time = end_time - start_time

        print(
            f"✅ Deep research complete! Processed {len(all_results)} total queries in {execution_time:.1f}s"
        )

        return {
            "research_results": all_results,
            "learnings": list(set(all_learnings)),  # Remove duplicates
            "context": all_context,
            "execution_time": execution_time,
            "total_queries": len(all_results),
            "depth_reached": current_depth,
        }

    async def _research_single_query(
        self, query: DataQuery, progress: ResearchProgress, on_progress=None
    ) -> Optional[Dict[str, Any]]:
        """Research a single query and extract insights"""
        try:
            print(f"   📈 Analyzing: {query.query[:60]}...")

            if on_progress:
                progress.current_query = query.query
                on_progress(progress)

            # Generate pandas code for the research question
            computation_result = await self._compute_query_data(query)

            if not computation_result or computation_result.get("error"):
                print(
                    f"      Skipping - computation failed: {computation_result.get('error', 'unknown error')}"
                )
                return None

            # Extract data and chart info
            computed_data = computation_result.get("data", {})
            chart_path = computation_result.get("chart_path")
            has_chart = computation_result.get("has_chart", False)
            generated_code = computation_result.get("generated_code", "")

            if not computed_data or len(str(computed_data)) > 10000:
                print(f"      Skipping - data too large or empty")
                return None

            # Use generated Python chart instead of Vega-Lite
            chart_spec = {
                "chart_path": chart_path,
                "has_chart": has_chart,
                "python_code": generated_code,
            }

            # Extract insights and learnings
            insights, learnings = await self._extract_insights_and_learnings(
                query, computed_data, chart_spec
            )

            # Generate narrative using Python code
            narrative = await self._generate_narrative(query, insights, chart_spec)

            # Update progress
            progress.completed_queries += 1
            progress.current_breadth += 1

            if on_progress:
                on_progress(progress)

            return {
                "query": query.query,
                "analysis_type": query.analysis_type,
                "research_goal": query.research_goal,
                "depth_level": query.depth_level,
                "computed_data": computed_data,
                "chart_spec": chart_spec,
                "insights": insights,
                "learnings": learnings,
                "narrative": narrative,
                "context": f"Query: {query.query}\nFindings: {' '.join(insights)}\nLearnings: {' '.join(learnings)}",
            }

        except Exception as e:
            print(f"      ❌ Error analyzing query: {str(e)[:100]}...")
            return None

    async def _compute_query_data(self, query: DataQuery) -> Dict[str, Any]:
        """Generate and execute pandas query"""
        # Sample relevant columns for context
        column_samples = sample_data(query.key_columns, 5) if query.key_columns else {}

        system_prompt = """
        You are a pandas expert generating precise data analysis code.
        Focus on creating meaningful, visualizable results that answer the research question.
        """

        prompt = f"""
        Research Question: {query.query}
        Research Goal: {query.research_goal}
        Analysis Type: {query.analysis_type}
        Key Columns: {query.key_columns}
        Expected Chart: {query.expected_chart_type}
        
        Dataset Info:
        - Rows: {self.dataset_info.get('num_rows', 'unknown')}
        - Columns: {self.dataset_info.get('attributes', [])}
        
        Sample Data for Key Columns:
        {json.dumps(column_samples, indent=2)}
        
        Generate pandas code that:
        1. Answers the specific research question using ALL rows in the dataset
        2. Creates a {query.expected_chart_type} visualization using matplotlib/seaborn
        3. Handles missing values appropriately
        4. Uses the ENTIRE dataset for computation (don't limit input data)
        5. Create new columns if needed (e.g., page_length = last_page - first_page)
        6. Final result can be aggregated/summarized but computation should use all data
        7. MUST create a chart using plt or sns and show it
        8. Store the final computed result in a variable called 'result'
        
        IMPORTANT CONSTRAINTS:
        - ONLY use variables that are defined: df, pd, plt, sns, chart_path
        - NEVER reference variables that don't exist in the dataset
        - Dataset columns: {list(self.dataset_info.get('attributes', []))}
        - If you need to filter data, use df[df['column'].isin(['value1', 'value2'])]
        - Always check if columns exist before using them
        - DO NOT create undefined variables like 'conferences_of_interest'
        
        Chart types to use: {query.expected_chart_type} (scatter, histogram, bar, line, heatmap, box, violin, etc.)
        
        Example structure:
        ```python
        # Check data and create analysis using ONLY existing columns
        if 'Conference' in df.columns:
            result = df.groupby('Conference')['AminerCitationCount'].mean()
        else:
            result = df.describe()
        
        # Create visualization  
        plt.figure(figsize=(10, 6))
        if len(result) > 0:
            sns.barplot(x=result.index, y=result.values)
            plt.title('Analysis Results')
            plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()  # This will be captured and saved automatically
        ```
        
        Return ONLY the pandas code with NO explanations, NO markdown, NO undefined variables.
        """

        pandas_code = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=prompt, replacements={}
        )

        # Clean and execute
        cleaned_code = clean_markdown_output(pandas_code, "python")
        result = execute_pandas_query_for_computation(cleaned_code)

        # Add the generated code to the result for narrative generation
        if isinstance(result, dict):
            result["generated_code"] = cleaned_code

        return result

    async def _generate_chart_spec(
        self, query: DataQuery, computed_data: Dict
    ) -> Dict[str, Any]:
        """Generate Vega-Lite chart specification"""
        system_prompt = """
        You are a Vega-Lite expert creating insightful visualizations for research questions.
        Generate clear, effective charts that use inline data (NOT external CSV files).
        CRITICAL: Always use "data": {"values": [actual_data_array]} format, never reference external files.
        """

        prompt = f"""
        Research Question: {query.query}
        Research Goal: {query.research_goal}
        Chart Type: {query.expected_chart_type}
        
        Data to Visualize:
        {json.dumps(computed_data, indent=2)}
        
        Create a Vega-Lite specification that:
        1. Uses INLINE data with "data": {{"values": [actual_data]}} format
        2. NEVER references external CSV files or URLs
        3. Clearly answers the research question
        4. Supports the research goal
        5. Uses appropriate visual encodings for the data type
        6. Has informative titles and labels
        7. Is publication-ready and professional
        8. Includes interactive features when appropriate (tooltips, selection)
        
        EXAMPLE FORMAT:
        {{
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {{"values": [your_actual_data_here]}},
            "mark": "appropriate_mark",
            "encoding": {{ "x": ..., "y": ... }},
            "title": "Descriptive Title"
        }}
        
        Return only the complete Vega-Lite JSON specification with inline data.
        """

        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=prompt, replacements={}
        )

        return extract_json_from_response(response)

    async def _extract_insights_and_learnings(
        self, query: DataQuery, computed_data: Dict, chart_spec: Dict
    ) -> tuple[List[str], List[str]]:
        """Extract insights and learnings from analysis results"""
        system_prompt = """
        You are a data research expert extracting actionable insights and learnings from analysis results.
        Focus on patterns, anomalies, and findings that could lead to deeper research questions.
        """

        prompt = f"""
        Research Question: {query.query}
        Research Goal: {query.research_goal}
        Analysis Type: {query.analysis_type}
        
        Computed Data:
        {json.dumps(computed_data, indent=2)}
        
        Chart Specification:
        {json.dumps(chart_spec, indent=2)}
        
        Extract:
        1. Key insights (3-5 specific findings from the data)
        2. Research learnings (2-3 broader patterns or discoveries that could inform follow-up research)
        
        Focus on:
        - Quantitative findings with specific numbers
        - Unusual patterns or outliers
        - Trends and relationships
        - Data quality observations
        - Business or domain implications
        
        Return JSON:
        {{
            "insights": ["Specific finding 1", "Specific finding 2", ...],
            "learnings": ["Broader learning 1", "Broader learning 2", ...]
        }}
        """

        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=prompt, replacements={}
        )

        result = extract_json_from_response(response)
        return result.get("insights", []), result.get("learnings", [])

    async def _generate_narrative(
        self, query: DataQuery, insights: List[str], chart_spec: Dict
    ) -> str:
        """Generate narrative explanation for the analysis including chart description"""
        system_prompt = """
        You are a data storytelling expert creating compelling narratives from research findings.
        Transform technical findings into accessible, engaging stories that include detailed chart descriptions.
        """

        python_code = chart_spec.get("python_code", "")
        has_chart = chart_spec.get("has_chart", False)

        chart_info = ""
        if has_chart and python_code:
            chart_info = f"""
        
        Python Visualization Code Generated:
        ```python
        {python_code}
        ```
        
        Chart Generated: Yes (saved as {chart_spec.get('chart_path', 'chart file')})
        """
        else:
            chart_info = "No visualization was generated for this analysis."

        prompt = f"""
        Research Question: {query.query}
        Research Goal: {query.research_goal}
        Analysis Type: {query.analysis_type}
        
        Key Insights:
        {chr(10).join(f"• {insight}" for insight in insights)}
        {chart_info}
        
        Create a compelling narrative (2-3 paragraphs) that:
        1. Explains what the analysis reveals
        2. Describes the visualization created (based on the Python code) and what it shows
        3. Highlights the most important findings from both data and visualization
        4. Connects findings to the research goal
        5. Discusses implications and significance
        6. Is accessible to a general audience
        
        If a chart was generated, explain:
        - What type of visualization was created (based on the Python code)
        - What patterns, trends, or insights the chart reveals
        - How the visualization supports the research findings
        
        Focus on storytelling that makes data insights and visualizations engaging and actionable.
        """

        return invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=prompt, replacements={}
        )

    async def _generate_follow_up_queries(
        self,
        previous_queries: List[DataQuery],
        all_learnings: List[str],
        depth_level: int,
    ) -> List[DataQuery]:
        """Generate follow-up research queries based on previous findings"""

        if depth_level > self.depth:
            return []

        print(
            f"   🔄 Generating follow-up queries based on {len(all_learnings)} learnings..."
        )

        # Generate more follow-ups to reach target of 12+ total charts
        if depth_level == 2:
            max_follow_ups = self.breadth  # Generate as many as initial breadth
        else:
            max_follow_ups = max(3, self.breadth // depth_level)

        system_prompt = """
        You are a research expert generating follow-up questions based on previous findings.
        Create queries that dive deeper into interesting patterns discovered in the initial research.
        """

        # Summarize previous research for context
        previous_context = {
            "previous_queries": [
                q.query for q in previous_queries[-5:]
            ],  # Last 5 queries
            "key_learnings": all_learnings[-10:],  # Last 10 learnings
            "depth_level": depth_level,
        }

        prompt = f"""
        Based on previous research findings, generate {max_follow_ups} follow-up research queries for deeper investigation:

        Previous Research Context:
        {json.dumps(previous_context, indent=2)}

        Generate follow-up queries that:
        1. Investigate specific patterns or anomalies discovered
        2. Explore causal relationships suggested by the findings
        3. Segment or drill down into interesting subgroups
        4. Validate or challenge initial findings
        5. Connect different findings to uncover broader insights

        IMPORTANT: Use diverse, advanced visualization types:
        - Interactive scatter plots with color coding
        - Correlation heatmaps
        - Multi-dimensional analysis charts
        - Box plots for outlier investigation
        - Advanced bar charts with grouping
        - Line charts for temporal analysis

        Ensure queries are:
        - More specific than previous queries
        - Based on actual learnings from the data
        - Focused on areas with high insight potential
        - Different from queries already explored
        - Using diverse visualization types

        Return JSON:
        {{
            "follow_up_queries": [
                {{
                    "query": "Specific follow-up research question",
                    "analysis_type": "trend|distribution|comparison|correlation|outlier|performance",
                    "key_columns": ["relevant", "columns"],
                    "expected_chart_type": "scatter|heatmap|box|line|bar|histogram",
                    "research_goal": "What deeper insight this follow-up seeks",
                    "parent_insight": "Which previous learning/finding this builds on"
                }}
            ]
        }}
        """

        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=prompt, replacements={}
        )

        try:
            follow_up_data = extract_json_from_response(response)
            follow_ups = []

            for q_data in follow_up_data.get("follow_up_queries", []):
                # Avoid duplicating research patterns
                query_signature = (
                    f"{q_data['query'][:50]}_{q_data.get('analysis_type', 'general')}"
                )
                if query_signature not in self.visited_patterns:
                    query = DataQuery(
                        query=q_data["query"],
                        analysis_type=q_data.get("analysis_type", "general"),
                        key_columns=q_data.get("key_columns", []),
                        expected_chart_type=q_data.get("expected_chart_type", "bar"),
                        research_goal=q_data.get("research_goal", ""),
                        depth_level=depth_level,
                        parent_query=q_data.get("parent_insight", ""),
                    )
                    follow_ups.append(query)
                    self.visited_patterns.add(query_signature)

            print(f"   Generated {len(follow_ups)} unique follow-up queries")
            return follow_ups[:max_follow_ups]

        except Exception as e:
            print(f"   ❌ Error generating follow-up queries: {e}")
            return []

    def _query_to_dict(self, query: DataQuery) -> Dict:
        """Convert DataQuery to dict for serialization"""
        return {
            "query": query.query,
            "analysis_type": query.analysis_type,
            "key_columns": query.key_columns,
            "expected_chart_type": query.expected_chart_type,
            "research_goal": query.research_goal,
            "depth_level": query.depth_level,
            "parent_query": query.parent_query,
            "learnings": query.learnings,
        }


# Workflow Steps
def generate_initial_queries(state: State):
    """Step 1: Generate initial research queries using GPT-Researcher methodology"""
    print("Step 1 / 3: Generating Initial Research Queries (GPT-Researcher Deep Mode)")

    # Check cache
    cached_queries = load_cached_json("deep_research_queries.json")
    if cached_queries:
        print("Using cached deep research queries")
        return {"initial_queries": cached_queries}

    # Create research conductor
    conductor = DataResearchConductor(
        dataset_profile=state["dataset_profile"],
        dataset_info=state["dataset_info"],
        config={
            "deep_research_breadth": 4,
            "deep_research_depth": 3,
            "deep_research_concurrency": 4,
        },
    )

    # Generate initial queries
    try:
        # Since we can't use async in LangGraph nodes directly, we'll use asyncio.run
        import asyncio

        initial_queries = asyncio.run(conductor.generate_initial_research_queries())

        # Convert to dict for state
        query_dicts = [conductor._query_to_dict(q) for q in initial_queries]
        save_json_data(query_dicts, "deep_research_queries.json", "./datasets")

        return {"initial_queries": query_dicts}

    except Exception as e:
        print(f"Error generating initial queries: {e}")
        # Fallback to simple query generation
        fallback_queries = [
            {
                "query": "What are the key trends and patterns in this dataset?",
                "analysis_type": "trend",
                "key_columns": [],
                "expected_chart_type": "line",
                "research_goal": "Identify overall patterns and trends",
                "depth_level": 1,
                "parent_query": "",
                "learnings": [],
            }
        ]
        return {"initial_queries": fallback_queries}


def conduct_deep_research(state: State):
    """Step 2: Conduct deep recursive research"""
    print("Step 2 / 3: Conducting Deep Recursive Research")

    # Check cache
    cached_results = load_cached_json("deep_research_results.json")
    if cached_results:
        print("Using cached deep research results")
        return {"research_results": cached_results}

    initial_queries_data = state["initial_queries"]

    # Create research conductor
    conductor = DataResearchConductor(
        dataset_profile=state["dataset_profile"],
        dataset_info=state["dataset_info"],
        config={
            "deep_research_breadth": 4,
            "deep_research_depth": 3,
            "deep_research_concurrency": 4,
        },
    )

    # Convert dict queries back to DataQuery objects
    initial_queries = [DataQuery(**q_data) for q_data in initial_queries_data]

    try:
        # Run deep research
        import asyncio

        research_results = asyncio.run(conductor.conduct_deep_research(initial_queries))

        save_json_data(research_results, "deep_research_results.json", "./datasets")
        return {"research_results": research_results}

    except Exception as e:
        print(f"Error in deep research: {e}")
        # Return minimal results structure
        return {
            "research_results": {
                "research_results": [],
                "learnings": ["Deep research encountered an error"],
                "context": ["Error in research process"],
                "execution_time": 0,
                "total_queries": 0,
                "depth_reached": 1,
            }
        }


def generate_final_report(state: State):
    """Step 3: Generate comprehensive final research report"""
    print("Step 3 / 3: Generating Final Research Report")

    # Check cache
    cached_report = load_cached_json("final_deep_research_report.json")
    if cached_report:
        print("Using cached final research report")
        return {"final_report": cached_report}

    research_results = state["research_results"]
    dataset_profile = state["dataset_profile"]

    # Generate comprehensive report
    system_prompt = """
    You are a research paper writer creating comprehensive analysis reports from deep research findings.
    Synthesize multiple levels of research into a coherent, insightful narrative.
    """

    # Extract key information for report generation
    total_queries = research_results.get("total_queries", 0)
    depth_reached = research_results.get("depth_reached", 1)
    learnings = research_results.get("learnings", [])
    execution_time = research_results.get("execution_time", 0)

    # Generate report title
    title_prompt = f"""
    Generate a compelling title for a comprehensive data analysis research report.
    
    Research Overview:
    - Deep research with {total_queries} queries across {depth_reached} levels
    - Dataset with {dataset_profile.get("shape", ["unknown", "unknown"])[0]} rows
    - Execution time: {execution_time:.1f} seconds
    - Key learnings: {len(learnings)}
    
    Make the title specific, professional, and research-oriented.
    Return only the title.
    """

    title = invoke_llm_with_prompt(
        system_content=system_prompt, prompt_template=title_prompt, replacements={}
    ).strip()

    # Generate introduction
    intro_prompt = f"""
    Write a comprehensive introduction for this deep research analysis report.
    
    Title: {title}
    Dataset Profile: Shape {dataset_profile.get("shape", "unknown")}
    Research Methodology: Deep recursive research with breadth-first and depth-first exploration
    Total Analyses: {total_queries} queries across {depth_reached} depth levels
    Key Findings: {learnings[:5]}
    
    The introduction should:
    1. Set context for the comprehensive analysis approach
    2. Explain the GPT-Researcher inspired methodology
    3. Preview the multi-level research findings
    4. Highlight the depth and breadth of investigation
    5. Be 3-4 paragraphs, professional and engaging
    """

    introduction = invoke_llm_with_prompt(
        system_content=system_prompt, prompt_template=intro_prompt, replacements={}
    ).strip()

    # Generate conclusion
    conclusion_prompt = f"""
    Write a comprehensive conclusion for this deep research analysis.
    
    Research Summary:
    - {total_queries} total queries across {depth_reached} levels of investigation
    - Execution time: {execution_time:.1f} seconds
    - Major learnings: {learnings}
    
    The conclusion should:
    1. Synthesize the most significant findings across all research levels
    2. Highlight patterns and insights that emerged from the recursive investigation
    3. Discuss the value of the deep research methodology
    4. Suggest implications and potential follow-up research areas
    5. Be 3-4 paragraphs, insightful and forward-looking
    """

    conclusion = invoke_llm_with_prompt(
        system_content=system_prompt, prompt_template=conclusion_prompt, replacements={}
    ).strip()

    # Structure the final report
    final_report = {
        "title": {"narrative": title},
        "introduction": {"narrative": introduction},
    }

    # Add research results as sections
    for i, result in enumerate(research_results.get("research_results", []), 1):
        section_key = f"research_{i:02d}_depth_{result.get('depth_level', 1)}"
        chart_spec = result.get("chart_spec", {})
        chart_path = (
            chart_spec.get("chart_path") if isinstance(chart_spec, dict) else None
        )

        final_report[section_key] = {
            "chart_path": chart_path,
            "narrative": f"## {result.get('query', 'Research Query')}\n\n**Research Goal:** {result.get('research_goal', 'N/A')}\n\n**Analysis Level:** Depth {result.get('depth_level', 1)}\n\n{result.get('narrative', 'Analysis narrative not available.')}\n\n**Key Insights:**\n"
            + "\n".join([f"• {insight}" for insight in result.get("insights", [])]),
        }

    # Add conclusion
    final_report["conclusion"] = {"narrative": conclusion}

    # Add research methodology section
    methodology = f"""
    ## Research Methodology
    
    This analysis employed a **deep recursive research methodology** inspired by GPT-Researcher, featuring:
    
    **Multi-Level Investigation:**
    - **Breadth**: {research_results.get('research_results', [])} parallel research streams
    - **Depth**: {depth_reached} levels of recursive investigation  
    - **Total Queries**: {total_queries} analytical questions
    
    **Recursive Query Generation:**
    - Initial queries explored different data dimensions
    - Follow-up queries were generated based on discovered insights
    - Each level built upon learnings from the previous level
    
    **Research Process:**
    1. Generate initial research queries covering different analytical perspectives
    2. Execute pandas-based data analysis for each query
    3. Extract insights and learnings from results
    4. Generate follow-up queries based on interesting findings
    5. Recursively investigate deeper patterns and relationships
    6. Synthesize findings across all research levels
    
    **Execution Metrics:**
    - Analysis Time: {execution_time:.1f} seconds
    - Research Levels Reached: {depth_reached}
    - Total Insights Generated: {len(learnings)}
    """

    final_report["methodology"] = {"narrative": methodology}

    save_json_data(final_report, "final_deep_research_report.json", "./datasets")
    return {"final_report": final_report}


def create_workflow():
    """Create the GPT-Researcher inspired deep research workflow"""
    builder = StateGraph(State)

    builder.add_node("generate_initial_queries", generate_initial_queries)
    builder.add_node("conduct_deep_research", conduct_deep_research)
    builder.add_node("generate_final_report", generate_final_report)

    builder.add_edge(START, "generate_initial_queries")
    builder.add_edge("generate_initial_queries", "conduct_deep_research")
    builder.add_edge("conduct_deep_research", "generate_final_report")
    builder.add_edge("generate_final_report", END)

    return builder.compile()


class Agent:
    def __init__(self):
        self.workflow = None

    def initialize(self):
        self.workflow = create_workflow()

    def initialize_state_from_csv(self) -> dict:
        """Initialize state with dataset profile and info"""
        path = "./dataset.csv"

        # Read CSV data
        csv_data = read_csv_data(path)
        dataset_info = {
            "file_name": path,
            "num_rows": csv_data["num_rows"],
            "attributes": csv_data["headers"],
            "rows": csv_data["data"],
        }

        # Load dataset and generate profile
        df = pd.read_csv(path)
        dataset_profile = generate_dataset_profile(df)

        save_json_data(dataset_profile, "dataset_profile.json", "./datasets")

        return {"dataset_profile": dataset_profile, "dataset_info": dataset_info}

    def decode_output(self, output: dict):
        """Generate HTML report from final report"""
        if "final_report" in output:
            print("Generating HTML report from deep research findings...")
            self.generate_deep_research_html_report(
                output["final_report"], "output.html"
            )
        else:
            print("No final report found in output")

    def generate_deep_research_html_report(
        self, research_components: dict, output_path: str
    ):
        """Generate HTML report for deep research results"""
        html_lines = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "  <meta charset='utf-8'>",
            "  <title>Deep Research Analysis Report</title>",
            "  <style>",
            "    body { font-family: 'Georgia', serif; margin: 2em auto; max-width: 1200px; line-height: 1.6; color: #333; }",
            "    .header { text-align: center; border-bottom: 3px solid #2c3e50; padding-bottom: 1em; margin-bottom: 2em; }",
            "    h1 { color: #2c3e50; font-size: 2.2em; margin-bottom: 0.5em; }",
            "    .subtitle { color: #7f8c8d; font-size: 1.1em; font-style: italic; }",
            "    h2 { color: #34495e; margin-top: 2.5em; border-left: 4px solid #3498db; padding-left: 1em; }",
            "    h3 { color: #7f8c8d; margin-top: 1.8em; }",
            "    .research-section { margin: 2.5em 0; padding: 1.5em; border: 1px solid #ecf0f1; border-radius: 8px; background: #fafafa; }",
            "    .chart-container { margin: 2em auto; text-align: center; }",
            "    .chart-image { max-width: 100%; height: auto; margin: 1em auto; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }",
            "    .narrative { margin: 1.5em 0; text-align: justify; }",
            "    .insights-list { background: #f8f9fa; padding: 1em; border-left: 3px solid #28a745; margin: 1em 0; }",
            "    .methodology { background: #e8f4fd; padding: 1.5em; border-radius: 5px; margin: 2em 0; }",
            "    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1em; margin: 1.5em 0; }",
            "    .stat-card { background: white; padding: 1em; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }",
            "    .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }",
            "    .stat-label { color: #7f8c8d; font-size: 0.9em; }",
            "  </style>",
            "</head>",
            "<body>",
        ]

        vis_counter = 0

        # Process each component
        for key, component in research_components.items():
            if isinstance(component, dict):

                # Header for title
                if key == "title":
                    html_lines.extend(
                        [
                            "<div class='header'>",
                            f"<h1>{component['narrative']}</h1>",
                            "<div class='subtitle'>Deep Recursive Research Analysis • GPT-Researcher Inspired</div>",
                            "</div>",
                        ]
                    )

                # Special formatting for methodology
                elif key == "methodology":
                    narrative_html = self.markdown_to_html_enhanced(
                        component["narrative"]
                    )
                    html_lines.append(
                        f'<div class="methodology">{narrative_html}</div>'
                    )

                # Research sections with charts
                elif "chart_path" in component and "narrative" in component:
                    narrative = component["narrative"]
                    chart_path = component.get("chart_path")

                    # Extract title from narrative
                    lines = narrative.split("\n")
                    title = ""
                    content = narrative

                    if lines and (
                        lines[0].startswith("#") or lines[0].startswith("##")
                    ):
                        title = lines[0].replace("#", "").strip()
                        content = "\n".join(lines[1:]).strip()

                    html_lines.append('<div class="research-section">')

                    if title:
                        html_lines.append(f"<h2>{title}</h2>")

                    # Add chart if it exists
                    # Fix path resolution - charts are in studio/charts/ but we might be running from different directory
                    if chart_path:
                        # Try multiple possible paths
                        possible_paths = [
                            chart_path,  # Original path
                            os.path.join("studio", chart_path),  # From parent directory
                            os.path.join(
                                os.path.dirname(__file__), chart_path
                            ),  # Relative to agent.py
                        ]

                        actual_chart_path = None
                        for path in possible_paths:
                            if os.path.exists(path):
                                actual_chart_path = path
                                break

                        if actual_chart_path:
                            # Convert image to base64 for embedding
                            import base64

                            try:
                                with open(actual_chart_path, "rb") as img_file:
                                    img_data = base64.b64encode(img_file.read()).decode(
                                        "utf-8"
                                    )
                                    html_lines.extend(
                                        [
                                            '<div class="chart-container">',
                                            f'  <img src="data:image/png;base64,{img_data}" class="chart-image" alt="Research Chart {vis_counter + 1}">',
                                            "</div>",
                                        ]
                                    )
                                    vis_counter += 1
                            except Exception as e:
                                html_lines.append(
                                    f'<div class="chart-container"><p>Chart could not be loaded from {actual_chart_path}: {str(e)}</p></div>'
                                )
                        else:
                            # Debug: show what paths were tried
                            html_lines.append(
                                f'<div class="chart-container"><p>Chart file not found. Tried paths: {", ".join(possible_paths)}</p></div>'
                            )
                    else:
                        html_lines.append(
                            '<div class="chart-container"><p>No chart path provided for this analysis.</p></div>'
                        )

                    # Add narrative
                    if content:
                        narrative_html = self.markdown_to_html_enhanced(content)
                        html_lines.append(
                            f'<div class="narrative">{narrative_html}</div>'
                        )

                    html_lines.append("</div>")

                # Regular sections (introduction, conclusion)
                elif "narrative" in component:
                    narrative_html = self.markdown_to_html_enhanced(
                        component["narrative"]
                    )
                    html_lines.append(f'<div class="narrative">{narrative_html}</div>')

        html_lines.extend(["</body>", "</html>"])

        # Write to file
        import os
        from pathlib import Path

        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)

        Path(output_path).write_text("\n".join(html_lines), encoding="utf-8")
        print(f"Deep research HTML report generated: {output_path}")

    def markdown_to_html_enhanced(self, md: str) -> str:
        """Enhanced markdown to HTML converter"""
        import re

        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", md, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)

        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # Convert bullet points with better styling
        html = re.sub(r"^• (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)

        # Wrap consecutive list items
        html = re.sub(
            r"(<li>.*?</li>(?:\s*<li>.*?</li>)*)",
            r'<ul class="insights-list">\1</ul>',
            html,
            flags=re.DOTALL,
        )

        html = re.sub(r"^---\s*$", r"<hr/>", html, flags=re.MULTILINE)

        # Convert paragraphs
        parts = [p.strip() for p in html.split("\n\n") if p.strip()]
        paragraphs = []
        for part in parts:
            if not any(
                tag in part for tag in ["<h1>", "<h2>", "<h3>", "<ul>", "<hr/>"]
            ):
                paragraphs.append(f"<p>{part}</p>")
            else:
                paragraphs.append(part)

        return "\n".join(paragraphs)

    def process(self):
        if self.workflow is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        print("🚀 Starting GPT-Researcher Inspired Deep Data Analysis...")
        print("📊 Deep Recursive Research Methodology:")
        print("   1. Generate Initial Research Queries")
        print("   2. Conduct Deep Recursive Research")
        print("   3. Generate Comprehensive Final Report")
        print("")

        # Initialize state
        state = self.initialize_state_from_csv()

        # Generate dataset summary
        state = generate_dataset_summary(state)

        # Run workflow
        output_state = self.workflow.invoke(state)

        # Flatten output
        def _flatten(value):
            return getattr(value, "content", value)

        result = {k: _flatten(v) for k, v in output_state.items()}

        # Generate HTML report
        self.decode_output(result)

        print(
            "\n✅ Deep research analysis complete! Check output.html for comprehensive findings."
        )
        return result
