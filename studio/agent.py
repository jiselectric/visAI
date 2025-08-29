import base64
import io
import json
import os
from typing import Any, Dict, List, Union

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from helpers import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from Researcher import ResearchConfig, Researcher
from typing_extensions import TypedDict
from utils.file_operation import load_cached_json, read_csv_data, save_json_data
from utils.generate_dataset_profile import generate_dataset_profile

# Type alias for JSON-compatible types
JSONType = Union[str, int, float, bool, None, Dict[str, "JSONType"], List["JSONType"]]


class State(TypedDict):
    message: str
    dataset_info: JSONType
    dataset_profile: JSONType
    research_questions: JSONType
    research_results: JSONType
    final_arrangement: JSONType


def generate_research_questions(state: State):
    """Step 1: Generate Research Questions using Researcher class"""

    # Initialize Researcher
    config = ResearchConfig(depth=3, breadth=4, max_workers=8, use_caching=True)
    researcher = Researcher(config, state["dataset_profile"])  # type: ignore

    # Generate questions
    questions = researcher.step1_generate_research_questions()

    # Convert to serializable format
    questions_data = [
        {
            "question": q.question,
            "parent_question": q.parent_question,
            "level": q.level,
            "visualization": q.visualization,
            "category": q.category,
            "source_columns": q.source_columns,
        }
        for q in questions
    ]

    return {"research_questions": questions_data}


def conduct_research(state: State):
    """Step 2: Conduct Research for all questions with parallel processing"""
    print("=== Step 2: Conduct Research ===")

    # Initialize Researcher with existing questions
    config = ResearchConfig(depth=3, breadth=4, max_workers=6, use_caching=True)
    researcher = Researcher(config, state["dataset_profile"])  # type: ignore

    # Restore research questions from state
    from Researcher import ResearchQuestion

    researcher.research_questions = [
        ResearchQuestion(**q) for q in state["research_questions"]  # type: ignore
    ]

    # Conduct research
    results = researcher.step2_conduct_research()

    # Convert to serializable format
    results_data = [
        {
            "question": r.question,
            "computed_data": r.computed_data,
            "explanation": r.explanation,
            "visualization_code": r.visualization_code,
            "title": r.title,
            "category": r.category,
            "source_columns": r.source_columns,
        }
        for r in results
    ]

    return {"research_results": results_data}


def arrange_results(state: State):
    """Step 3: Arrange and organize research results with complete structure for HTML generation"""
    print("=== Step 3: Arrange Results ===")

    # Initialize Researcher with existing data
    config = ResearchConfig(depth=3, breadth=4, max_workers=6, use_caching=True)
    researcher = Researcher(config, state["dataset_profile"])  # type: ignore

    # Restore research results from state
    from Researcher import ResearchResult

    researcher.research_results = [
        ResearchResult(**r) for r in state["research_results"]  # type: ignore
    ]

    # Arrange results
    final_arrangement = researcher.step3_arrange_results()

    # Ensure the final arrangement has all necessary structure for deterministic HTML generation
    structured_output = {
        "metadata": {
            "total_questions": len(state["research_questions"]) if state["research_questions"] else 0,  # type: ignore
            "total_results": len(state["research_results"]) if state["research_results"] else 0,  # type: ignore
            "dataset_columns": len(state["dataset_profile"]) if state["dataset_profile"] else 0,  # type: ignore
            "dataset_rows": state["dataset_info"]["num_rows"] if state["dataset_info"] else 0,  # type: ignore
        },
        "title": final_arrangement.get("title", "Comprehensive Data Analysis Report"),
        "introduction": final_arrangement.get("introduction", ""),
        "conclusion": final_arrangement.get("conclusion", ""),
        "results": final_arrangement.get("results", []),
    }

    return {"final_arrangement": structured_output}


def create_workflow():
    """Create the agentic workflow using LangGraph (Steps 1-3 only)"""
    builder = StateGraph(State)

    # Add nodes for LLM-based steps only
    builder.add_node("generate_research_questions", generate_research_questions)
    builder.add_node("conduct_research", conduct_research)
    builder.add_node("arrange_results", arrange_results)

    # Define the workflow edges
    builder.add_edge(START, "generate_research_questions")
    builder.add_edge("generate_research_questions", "conduct_research")
    builder.add_edge("conduct_research", "arrange_results")
    builder.add_edge("arrange_results", END)

    return builder.compile()


class Agent:
    def __init__(self):
        self.workflow = None

    def initialize(self):
        self.workflow = create_workflow()

    def initialize_state_from_csv(self) -> dict:
        """Initialize state with dataset profile and info"""
        path = "./dataset.csv"

        # Check if cached data exists
        cached_info = load_cached_json("dataset_info.json", "./datasets")
        cached_profile = load_cached_json("dataset_profile.json", "./datasets")

        if cached_info and cached_profile:
            print("Using cached dataset info and profile")
            return {"dataset_info": cached_info, "dataset_profile": cached_profile}

        # Generate dataset info
        csv_data = read_csv_data(path)
        dataset_info = {
            "file_name": path,
            "num_rows": csv_data["num_rows"],
            "attributes": csv_data["headers"],
            "rows": csv_data["data"],
        }
        save_json_data(dataset_info, "dataset_info.json", "./datasets")

        # Generate dataset profile
        import pandas as pd

        df = pd.read_csv(path)
        dataset_profile = generate_dataset_profile(df)
        save_json_data(dataset_profile, "dataset_profile.json", "./datasets")

        print(
            f"Dataset initialized: {dataset_info['num_rows']} rows, {len(dataset_info['attributes'])} columns"
        )
        return {"dataset_info": dataset_info, "dataset_profile": dataset_profile}

    def decode_output(self, output_state: dict):
        """
        Step 4: Deterministic HTML generation from structured final_arrangement
        This is where the Agent class handles the final HTML output generation
        """
        print("=== Step 4: Generate HTML Output ===")

        final_arrangement = output_state.get("final_arrangement", {})

        # Generate HTML content
        html_content = self.generate_html_report_with_python_charts(final_arrangement)

        # Save HTML file
        output_path = "output.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML report generated: {output_path}")
        return html_content

    def generate_html_report_with_python_charts(
        self, final_arrangement: Dict[str, Any]
    ) -> str:
        """Generate HTML report with Python visualizations rendered as images"""

        metadata = final_arrangement.get("metadata", {})

        html_lines = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "  <meta charset='utf-8'>",
            "  <title>Research Data Analysis Report</title>",
            "  <style>",
            "    body { font-family: 'Georgia', serif; margin: 2em auto; max-width: 1200px; line-height: 1.6; background-color: #fafafa; }",
            "    .container { background: white; padding: 2em; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }",
            "    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-bottom: 2em; }",
            "    h2 { color: #34495e; margin-top: 2.5em; margin-bottom: 1em; border-left: 4px solid #3498db; padding-left: 1em; }",
            "    h3 { color: #7f8c8d; margin-top: 2em; margin-bottom: 1em; }",
            "    .section { margin: 3em 0; padding: 2em; border: 1px solid #ecf0f1; border-radius: 8px; background-color: #f8f9fa; }",
            "    .result-item { margin: 2em 0; padding: 2em; border: 1px solid #dee2e6; border-radius: 8px; background: white; }",
            "    .chart-container { text-align: center; margin: 2em 0; padding: 1em; background: white; border-radius: 8px; }",
            "    .chart-container img { max-width: 100%; height: auto; border: 1px solid #dee2e6; border-radius: 4px; }",
            "    .chart-container div[id^='vis_'] { margin: 0 auto; display: inline-block; }",
            "    .explanation { margin: 1.5em 0; padding: 1em; background-color: #f1f3f4; border-radius: 6px; }",
            "    .category-badge { display: inline-block; background: #3498db; color: white; padding: 0.3em 0.8em; border-radius: 15px; font-size: 0.8em; margin-bottom: 1em; }",
            "    strong { color: #2c3e50; }",
            "    code { background-color: #f1f3f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }",
            "    .error-chart { padding: 2em; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; color: #721c24; text-align: center; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <div class='container'>",
        ]

        # Title
        title = final_arrangement.get("title", "Data Analysis Report")
        html_lines.append(f"    <h1>{title}</h1>")

        # Introduction
        introduction = final_arrangement.get("introduction", "")
        if introduction:
            html_lines.extend(
                [
                    "    <div class='section'>",
                    "      <h2>Introduction</h2>",
                    f"      {self.markdown_to_html_enhanced(introduction)}",
                    "    </div>",
                ]
            )

        # Results
        results = final_arrangement.get("results", [])
        if results:
            html_lines.extend(
                [
                    "    <div class='section'>",
                    "      <h2>Research Findings</h2>",
                ]
            )

            for i, result in enumerate(results):
                # Generate chart image if visualization code exists
                chart_html = self.generate_chart_html(
                    result.get("visualization_code", ""),
                    result.get("computed_data"),
                    f"chart_{i}",
                )

                html_lines.extend(
                    [
                        "      <div class='result-item'>",
                        f"        <div class='category-badge'>{result.get('category', 'Analysis')}</div>",
                        f"        <h3>{result.get('title', 'Research Finding')}</h3>",
                    ]
                )

                # Add chart
                html_lines.extend(
                    [
                        "        <div class='chart-container'>",
                        f"          {chart_html}",
                        "        </div>",
                    ]
                )

                # Add explanation
                explanation = result.get("explanation", "")
                if explanation:
                    html_lines.extend(
                        [
                            "        <div class='explanation'>",
                            f"          {self.markdown_to_html_enhanced(explanation)}",
                            "        </div>",
                        ]
                    )

                # Research steps section removed

                html_lines.append("      </div>")

            html_lines.append("    </div>")

        # Conclusion
        conclusion = final_arrangement.get("conclusion", "")
        if conclusion:
            html_lines.extend(
                [
                    "    <div class='section'>",
                    "      <h2>Conclusion</h2>",
                    f"      {self.markdown_to_html_enhanced(conclusion)}",
                    "    </div>",
                ]
            )

        html_lines.extend(
            [
                "  </div>",
                "</body>",
                "</html>",
            ]
        )

        return "\n".join(html_lines)

    def generate_chart_html(
        self, viz_code: str, computed_data: Any, chart_id: str
    ) -> str:
        """Generate HTML for visualization - handles Python matplotlib/seaborn code"""
        if not viz_code:
            return '<div class="error-chart">No visualization code available</div>'

        try:
            # Handle as Python matplotlib/seaborn code
            import numpy as np
            import pandas as pd

            # Clear any existing plots
            plt.clf()
            plt.figure(figsize=(10, 6))

            # Prepare the data
            if isinstance(computed_data, list) and computed_data:
                df = pd.DataFrame(computed_data)
            elif isinstance(computed_data, dict):
                df = pd.DataFrame([computed_data])
            else:
                df = pd.DataFrame()

            # Create execution environment
            exec_env = {
                "df": df,
                "data": computed_data,
                "pd": pd,
                "np": np,
                "plt": plt,
                "sns": sns,
                "matplotlib": matplotlib,
                "chart_path": None,  # We'll handle saving directly via buffer
            }

            # Execute the visualization code
            exec(viz_code, exec_env)

            # Save plot to base64 string
            buffer = io.BytesIO()
            plt.savefig(
                buffer, format="png", dpi=150, bbox_inches="tight", facecolor="white"
            )
            buffer.seek(0)

            # Convert to base64
            image_data = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()

            # Clear the plot
            plt.clf()
            plt.close()

            return f'<img src="data:image/png;base64,{image_data}" alt="Chart {chart_id}" style="max-width: 100%; height: auto;">'

        except Exception as e:
            print(f"Error generating chart {chart_id}: {e}")
            return f'<div class="error-chart">Error generating visualization: {str(e)}</div>'

    def markdown_to_html_enhanced(self, md: str) -> str:
        """Enhanced markdown to HTML converter"""
        import re

        # Convert markdown headers
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", md, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)

        # Convert bold and italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # Convert code blocks
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # Convert lists
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = re.sub(r"(<li>.*</li>)", r"<ul>\1</ul>", html, flags=re.DOTALL)

        # Convert paragraphs (split by double newlines)
        parts = [p.strip() for p in html.split("\n\n") if p.strip()]
        paragraphs = []
        for part in parts:
            if not any(tag in part for tag in ["<h1>", "<h2>", "<h3>", "<ul>", "<li>"]):
                paragraphs.append(f"<p>{part}</p>")
            else:
                paragraphs.append(part)

        return "".join(paragraphs)

    def process(self):
        """Execute the complete workflow"""
        if self.workflow is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        # Initialize the state & read the dataset
        print("Initializing dataset...")
        state = self.initialize_state_from_csv()

        # Invoke the workflow (Steps 1-3)
        print("Starting research workflow...")
        output_state = self.workflow.invoke(state)

        # Flatten the output
        def _flatten(value):
            return getattr(value, "content", value)

        result = {k: _flatten(v) for k, v in output_state.items()}

        # Step 4: Generate HTML output deterministically
        html_content = self.decode_output(result)

        print("\n=== Workflow Completed ===")
        print(
            f"Generated research questions: {len(result.get('research_questions', []))}"
        )
        print(f"Completed analyses: {len(result.get('research_results', []))}")
        print(f"HTML report saved: output.html")

        return result
