import json
import os
from typing import Any, Counter, Dict, List, Union

from helpers import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from report_html import generate_html_report
from report_pdf import generate_pdf_report
from typing_extensions import TypedDict
from utils.data_utils import execute_pandas_query, generate_dataset_summary, sample_data
from utils.file_operation import (
    clean_markdown_output,
    load_cached_json,
    load_prompt_template,
    read_csv_data,
    save_json_data,
)
from utils.llm_operations import extract_json_from_response, invoke_llm_with_prompt

# Type alias for JSON-compatible types
JSONType = Union[str, int, float, bool, None, Dict[str, "JSONType"], List["JSONType"]]


class State(TypedDict):
    message: str
    raw_data: JSONType  # Step 0.1: Read the dataset
    dataset_info: JSONType  # Step 0.1: Read the dataset
    dataset_summary: JSONType  # Step 0.2: Generate dataset summary
    visualizable_dataset: JSONType  # Step 1: Select visualizable columns
    visualization_queries: JSONType  # Step 2: Generate visualization queries
    top_k_visualization_queries: JSONType  # Step 3: Select top-K queries
    computed_visualization_data: (
        JSONType  # Step 4: Compute data for visualization queries
    )
    generated_vegalite_charts: JSONType  # Step 5: Generate Vega-Lite Charts
    generated_vegalite_charts_with_narrative: (
        JSONType  # Step 6: Generate Narrative for Vega-Lite Charts
    )
    generated_research_paper_components: (
        JSONType  # Step 7: Generate Research Paper Components
    )


# Step 1: Select appropriate columns to visualize
def select_visualizable_data(state: State):
    print("Step 1 / 10: Select Visualizable Columns")
    dataset_summary = state["dataset_summary"]

    # Check if cached result exists
    cached_data = load_cached_json("01_visualizable_dataset.json")
    if cached_data:
        print("Using cached - 01_visualizable_dataset.json")
        return {"visualizable_dataset": cached_data}

    sys_prompt = load_prompt_template("01_select_visualizable_dataset.md")

    # Generate response using LLM
    dataset_summary_json = json.dumps(dataset_summary, indent=2, ensure_ascii=False)

    response_content = invoke_llm_with_prompt(
        system_content="You are a data visualization expert. Given a JSON object that summarizes each column of a dataset (with fields like column_name, examples, unique_value_count, top_frequencies, etc.), select only the columns appropriate for visualization.",
        prompt_template=sys_prompt,
        replacements={
            "{{dataset_summary_json}}": dataset_summary_json,
        },
    )

    # Extract JSON from response
    visualizable_dataset = extract_json_from_response(response_content)

    # Save the result
    save_json_data(visualizable_dataset, "01_visualizable_dataset.json")

    return {"visualizable_dataset": visualizable_dataset}


# Step 2: Generate queries to inspire visualization generation
def generate_visualization_queries(state: State):
    print("Step 2 / 10: Generate Visualization Queries")
    attributes = state["dataset_info"]["attributes"]  # type: ignore
    visualizable_dataset = state["visualizable_dataset"]

    # Check if cached result exists
    cached_data = load_cached_json("02_visualization_queries.json")
    if cached_data:
        print("Using cached - 02_visualization_queries.json")
        return {"visualization_queries": cached_data}

    sys_prompt = load_prompt_template("02_generate_visualization_queries.md")

    # Generate response using LLM
    visualizable_dataset_json = json.dumps(
        visualizable_dataset, indent=2, ensure_ascii=False
    )

    response_content = invoke_llm_with_prompt(
        system_content="You are a highly skilled LLM data analyst tasked with helping another LLM generate insightful visualizations from a structured dataset. Your role is to analyze a dataset summary and produce natural language queries that guide visualization generation.",
        prompt_template=sys_prompt,
        replacements={
            "{{visualizable_dataset_json}}": visualizable_dataset_json,
            "{{attributes}}": str(attributes),  # type: ignore
        },
    )

    # Extract JSON from response
    visualization_queries = extract_json_from_response(response_content)
    # Extract all keys from visualization_queries and store them as "attributes"
    visualization_queries["attributes"] = list(visualization_queries.keys())  # type: ignore

    # Save the result
    save_json_data(visualization_queries, "02_visualization_queries.json")

    return {"visualization_queries": visualization_queries}


# Step 3: Select top-K queries that would produce the research paper with natural logical flow
def select_top_k_visualization_queries(state: State):
    print("Step 3 / 10: Select Top-K Visualization Queries")
    visualization_queries = state["visualization_queries"]
    attributes = state["visualization_queries"]["attributes"]  # type: ignore

    # Check if cached result exists
    cached_data = load_cached_json("03_top_k_visualization_queries.json")
    if cached_data:
        print("Using cached - 03_top_k_visualization_queries.json")
        return {"top_k_visualization_queries": cached_data}

    sys_prompt = load_prompt_template("03_select_top_k_visualization_queries.md")

    # Generate response using LLM
    visualization_queries_json = json.dumps(
        visualization_queries, indent=2, ensure_ascii=False
    )

    K = 7  # number of queries to select
    response_content = invoke_llm_with_prompt(
        system_content="You are a highly skilled scholar who is writing a research paper. You are given a list of visualization queries that give deep insights into the dataset. Your task is to select the top-{K} queries that would produce the research paper with natural logical flow.",
        prompt_template=sys_prompt,
        replacements={
            "{{K}}": str(K),
            "{{visualization_queries_json}}": visualization_queries_json,
            "{{attributes}}": str(attributes),  # type: ignore
        },
    )

    # Extract JSON from response
    top_k_visualization_queries = extract_json_from_response(response_content)

    # Save the result
    save_json_data(top_k_visualization_queries, "03_top_k_visualization_queries.json")

    return {"top_k_visualization_queries": top_k_visualization_queries}


# Step 4: Compute the data for each visualization query
def compute_data_for_visualization_queries(state: State):
    print("Step 4 / 10: Compute Data for Visualization Queries")
    dataset_info = state["dataset_info"]
    top_k_visualization_queries = state["top_k_visualization_queries"]

    # Check if cached result exists
    cached_data = load_cached_json("04_computed_visualization_data.json")
    if cached_data:
        print("Using cached - 04_computed_visualization_data.json")
        return {"computed_visualization_data": cached_data}

    # Extract the selected_queries list from the response structure
    if (
        isinstance(top_k_visualization_queries, dict)
        and "selected_queries" in top_k_visualization_queries
    ):
        queries_list = top_k_visualization_queries["selected_queries"]
    elif isinstance(top_k_visualization_queries, list):
        queries_list = top_k_visualization_queries
    else:
        raise ValueError(
            f"Unexpected structure for top_k_visualization_queries: {type(top_k_visualization_queries)}"
        )

    computed_visualization_data = {}
    if isinstance(queries_list, list):
        for visualization_query in queries_list:
            query = visualization_query["query"]  # type: ignore
            chart_type = visualization_query["chart_type"]  # type: ignore
            columns = [
                part.strip()
                for part in visualization_query["source_attribute"].split(" & ")  # type: ignore
            ]

            # Sample 10 examples for each column
            attributes_samples = sample_data(columns, 10)

            sys_prompt = load_prompt_template(
                "04_generate_pandas_query_to_compute_data.md"
            )

            # Generate response using LLM
            attributes_samples_json = json.dumps(
                attributes_samples, indent=2, ensure_ascii=False
            )

            pandas_query = invoke_llm_with_prompt(
                system_content="You are a highly skilled data analyst with expertise in pandas. You are given a query, target visualization type(s), and sample data for target attribute(s). Your task is to generate a pandas query to accurately compute the data for the query.",
                prompt_template=sys_prompt,
                replacements={
                    "{{num_rows}}": str(dataset_info["num_rows"]),  # type: ignore
                    "{{attributes}}": str(dataset_info["attributes"]),  # type: ignore
                    "{{query}}": query,
                    "{{chart_type}}": chart_type,
                    "{{attributes_samples_json}}": attributes_samples_json,
                },  # type: ignore
            )

            cleaned_pandas_query = clean_markdown_output(pandas_query, "pandas")
            computed_data = execute_pandas_query(cleaned_pandas_query)

            computed_visualization_data[visualization_query["source_attribute"]] = {  # type: ignore
                "query": query,
                "computed_data": computed_data,
            }

    # Save the result
    save_json_data(computed_visualization_data, "04_computed_visualization_data.json")

    return {"computed_visualization_data": computed_visualization_data}


# Step 5: Generate Vega-Lite Charts
def generate_vega_lite_charts(state: State):
    print("Step 5 / 10: Generate Vega-Lite Charts")
    computed_visualization_data = state["computed_visualization_data"]

    # Check if cached result exists
    cached_data = load_cached_json("05_generated_vegalite_charts.json")
    if cached_data:
        print("Using cached - 05_generated_vegalite_charts.json")
        return {"computed_visualization_data": cached_data}

    generated_vega_lite_charts = {}
    for source_attribute, data in computed_visualization_data.items():  # type: ignore
        query = data["query"]  # type: ignore
        computed_data = data["computed_data"]  # type: ignore

        sys_prompt = load_prompt_template("05_generate_vegalite_chart.md")

        # Generate response using LLM
        computed_data_json = json.dumps(computed_data, indent=2, ensure_ascii=False)

        response_content = invoke_llm_with_prompt(
            system_content="You are a highly skilled data analyst with expertise in Vega-Lite charts. You are given a query and a computed data in JSON format. Your task is to generate an accurate Vega-Lite chart to visualize the data.",
            prompt_template=sys_prompt,
            replacements={
                "{{query}}": query,  # type: ignore
                "{{computed_data_json}}": computed_data_json,  # type: ignore
            },  # type: ignore
        )

        cleaned_response_content = clean_markdown_output(response_content, "vegalite")

        generated_vega_lite_charts[source_attribute] = {
            "query": query,
            "vega_lite_chart": cleaned_response_content,
        }

    # Save the result
    save_json_data(generated_vega_lite_charts, "05_generated_vegalite_charts.json")

    return {"generated_vegalite_charts": generated_vega_lite_charts}


# Step 6: Generate Narrative for Vega-Lite Charts
def generate_narrative_for_vegalite_charts(state: State):
    print("Step 6 / 10: Generate Narrative for Vega-Lite Charts")
    generated_vega_lite_charts = state["generated_vegalite_charts"]

    # Check if cached result exists
    cached_data = load_cached_json("06_generated_vegalite_charts_with_narrative.json")
    if cached_data:
        print("Using cached - 06_generated_vegalite_charts_with_narrative.json")
        return {"06_generated_vegalite_charts_with_narrative": cached_data}

    generated_vegalite_charts_with_narrative = {}
    for source_attribute, data in generated_vega_lite_charts.items():  # type: ignore
        query = data["query"]  # type: ignore
        vega_lite_chart = data["vega_lite_chart"]  # type: ignore

        sys_prompt = load_prompt_template("06_generate_narrative_for_vegalite_chart.md")

        # Generate response using LLM
        vega_lite_chart_json = json.dumps(vega_lite_chart, indent=2, ensure_ascii=False)

        response_content = invoke_llm_with_prompt(
            system_content="You are a **data storytelling expert** specializing in transforming complex visualizations into compelling, accessible narratives. Given a query and its corresponding Vega-Lite chart specification, your task is to generate **detailed, insightful explanations** that help readers understand both the data and its implications.",
            prompt_template=sys_prompt,
            replacements={
                "{{query}}": query,  # type: ignore
                "{{vega_lite_chart_json}}": vega_lite_chart_json,  # type: ignore
            },  # type: ignore
        )

        generated_vegalite_charts_with_narrative[query] = {
            "vega_lite_chart": vega_lite_chart,
            "narrative": response_content,
        }

    # Save the result
    save_json_data(
        generated_vegalite_charts_with_narrative,
        "06_generated_vegalite_charts_with_narrative.json",
    )

    return {
        "generated_vegalite_charts_with_narrative": generated_vegalite_charts_with_narrative
    }


# Step 7: Generate Research Paper Components
def generate_research_paper_components(state: State):
    print("Step 7 / 10: Generate Research Paper Components")
    generated_vegalite_charts_with_narrative = state[
        "generated_vegalite_charts_with_narrative"
    ]

    # Check if cached result exists
    cached_data = load_cached_json("07_generated_research_paper_components.json")
    if cached_data:
        print("Using cached - 07_generated_research_paper_components.json")
        return {"generated_research_paper_components": cached_data}

    sys_prompt = load_prompt_template("07_generate_research_paper_components.md")

    generated_vegalite_charts_with_narrative_json = json.dumps(
        generated_vegalite_charts_with_narrative, indent=2, ensure_ascii=False
    )

    response_content = invoke_llm_with_prompt(
        system_content="You are a research paper writing assistant that transforms structured JSON data containing Vega-Lite chart specifications and narratives into a full, well-formatted markdown research paper with Title, Abstract, Keywords, Introduction, Methodology, Results, Discussion, and Conclusion, following detailed formatting and style rules for clarity, insight, and accessibility",
        prompt_template=sys_prompt,
        replacements={
            "{{generated_vegalite_charts_with_narrative_json}}": generated_vegalite_charts_with_narrative_json,  # type: ignore
        },  # type: ignore
    )

    # Extract JSON from response
    response_content_json = extract_json_from_response(response_content)

    # Create Final Report
    generated_research_paper_components = {}
    generated_research_paper_components["title"] = {
        "narrative": response_content_json["title"]
    }
    generated_research_paper_components["abstract"] = {
        "narrative": response_content_json["abstract"]
    }
    generated_research_paper_components["keywords"] = {
        "narrative": response_content_json["keywords"]
    }
    generated_research_paper_components["introduction"] = {
        "narrative": response_content_json["introduction"]
    }
    generated_research_paper_components["methodology"] = {
        "narrative": response_content_json["methodology"]
    }

    # Add each visualization item separately between methodology and results
    for key, value in generated_vegalite_charts_with_narrative.items():  # type: ignore
        generated_research_paper_components[key] = value

    generated_research_paper_components["results"] = {
        "narrative": response_content_json["results"]
    }
    generated_research_paper_components["discussion"] = {
        "narrative": response_content_json["discussion"]
    }
    generated_research_paper_components["conclusion"] = {
        "narrative": response_content_json["conclusion"]
    }

    # Save the result
    save_json_data(
        generated_research_paper_components,
        "07_generated_research_paper_components.json",
    )

    return {"generated_research_paper_components": generated_research_paper_components}


def generate_msg(state: State):
    dataset_info = state["dataset_info"]
    # if the prompt is to generate Vega-Lite charts, then specify in sys_prompt and use generate_html_report()
    sys_prompt = f"Please generate Vega-Lite graphs to visualize insights from the dataset, output should be graphs and narrative: {dataset_info}"

    # if the prompt is to generate Python codes, then specify in sys_prompt and use generate_pdf_report()
    # sys_prompt = f"Please generate Python code to visualize insights from the dataset, output should be graphs and narrative: {dataset_info}"

    # get the LLM instance
    llm = get_llm(temperature=0, max_tokens=4096)

    # generate the response
    response = llm.invoke(
        [
            SystemMessage(content=sys_prompt),
            HumanMessage(content="Generate a response."),
        ]
    )
    return {"message": response}


def create_workflow():
    # create the agentic workflow using LangGraph
    builder = StateGraph(State)

    builder.add_node("select_visualizable_data", select_visualizable_data)
    builder.add_node("generate_visualization_queries", generate_visualization_queries)
    builder.add_node(
        "select_top_k_visualization_queries", select_top_k_visualization_queries
    )
    builder.add_node(
        "compute_data_for_visualization_queries", compute_data_for_visualization_queries
    )
    builder.add_node("generate_vega_lite_charts", generate_vega_lite_charts)
    builder.add_node(
        "generate_narrative_for_vegalite_charts", generate_narrative_for_vegalite_charts
    )
    builder.add_node(
        "generate_research_paper_components", generate_research_paper_components
    )

    builder.add_edge(START, "select_visualizable_data")
    builder.add_edge("select_visualizable_data", "generate_visualization_queries")
    builder.add_edge(
        "generate_visualization_queries", "select_top_k_visualization_queries"
    )
    builder.add_edge(
        "select_top_k_visualization_queries", "compute_data_for_visualization_queries"
    )
    builder.add_edge(
        "compute_data_for_visualization_queries", "generate_vega_lite_charts"
    )
    builder.add_edge(
        "generate_vega_lite_charts", "generate_narrative_for_vegalite_charts"
    )
    builder.add_edge(
        "generate_narrative_for_vegalite_charts", "generate_research_paper_components"
    )
    builder.add_edge("generate_research_paper_components", END)
    # builder.add_edge("generate_msg", END)
    return builder.compile()


class Agent:
    def __init__(self):
        self.workflow = None

    def initialize(self):
        self.workflow = create_workflow()

    def initialize_state_from_csv(self) -> dict:
        # The dataset should be first input to the agentic configuration, and it should be generalizable to any dataset
        path = "./dataset.csv"

        # Read CSV data using file operation utility
        csv_data = read_csv_data(path)

        # Prepare data structures
        raw_data = {"headers": csv_data["headers"], "data": csv_data["data"]}
        dataset_info = {
            "file_name": path,
            "num_rows": csv_data["num_rows"],
            "attributes": csv_data["headers"],
            "rows": csv_data["data"],
        }

        # Save data using file operation utilities
        save_json_data(raw_data, "00_raw_data.json", "./datasets")
        save_json_data(dataset_info, "00_dataset_info.json", "./datasets")

        return {"dataset_info": dataset_info, "raw_data": raw_data}

    def decode_output(self, output: dict):
        # New decode logic for step 7 output structure
        if "generated_research_paper_components" in output:
            print("Using new research paper HTML generation...")
            self.generate_research_paper_html_report(output["generated_research_paper_components"], "output.html")
        else:
            print("Using original HTML generation...")
            generate_html_report(output, "output.html")
    
    def generate_research_paper_html_report(self, research_paper_components: dict, output_path: str):
        """
        Generate HTML report from research paper components.
        Each component can have:
        - Only 'narrative' field: render as markdown
        - Both 'narrative' and 'vega_lite_chart': render both
        """
        html_lines = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "  <meta charset='utf-8'>",
            "  <title>Research Paper Report</title>",
            "  <script src='https://cdn.jsdelivr.net/npm/vega@5'></script>",
            "  <script src='https://cdn.jsdelivr.net/npm/vega-lite@5'></script>",
            "  <script src='https://cdn.jsdelivr.net/npm/vega-embed@6'></script>",
            "  <style>",
            "    body { font-family: 'Georgia', serif; margin: 2em auto; max-width: 1000px; line-height: 1.6; }",
            "    h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }",
            "    h2 { color: #34495e; margin-top: 2em; }",
            "    h3 { color: #7f8c8d; margin-top: 1.5em; }",
            "    .visualization-container { margin: 2em 0; padding: 1em; border: 1px solid #ecf0f1; border-radius: 5px; }",
            "    .narrative { margin: 1em 0; }",
            "    strong { color: #2c3e50; }",
            "    code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; }",
            "    hr { margin: 2em 0; border: none; border-top: 1px solid #bdc3c7; }",
            "  </style>",
            "</head>",
            "<body>",
        ]
        
        vis_counter = 0
        
        # Process each component in order
        for key, component in research_paper_components.items():
            if isinstance(component, dict):
                # Check if component has narrative
                if "narrative" in component:
                    narrative_html = self.markdown_to_html_enhanced(component["narrative"])
                    html_lines.append(f'<div class="narrative">{narrative_html}</div>')
                
                # Check if component has vega-lite chart
                if "vega_lite_chart" in component:
                    div_id = f"vis{vis_counter}"
                    html_lines.append(f'<div class="visualization-container">')
                    html_lines.append(f'  <div id="{div_id}"></div>')
                    
                    # Handle both string and dict vega_lite_chart
                    vega_spec = component["vega_lite_chart"]
                    if isinstance(vega_spec, str):
                        try:
                            import json
                            vega_spec = json.loads(vega_spec)
                        except json.JSONDecodeError:
                            html_lines.append(f'<p>Error: Invalid Vega-Lite specification</p>')
                            html_lines.append('</div>')
                            continue
                    
                    spec_json = json.dumps(vega_spec)
                    html_lines.extend([
                        "  <script>",
                        f"    vegaEmbed('#{div_id}', {spec_json})",
                        "      .catch(console.error);",
                        "  </script>",
                    ])
                    html_lines.append('</div>')
                    vis_counter += 1
            else:
                # Handle simple string components
                html_lines.append(f'<div class="narrative">{self.markdown_to_html_enhanced(str(component))}</div>')
        
        html_lines.extend([
            "</body>",
            "</html>"
        ])
        
        # Write to file (ensure it's in the correct directory)
        from pathlib import Path
        import os
        
        # Make sure we're writing to the current working directory (studio/)
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
            
        Path(output_path).write_text("\n".join(html_lines), encoding="utf-8")
        print(f"HTML report generated at: {output_path}")
    
    def markdown_to_html_enhanced(self, md: str) -> str:
        """Enhanced markdown to HTML converter for research papers."""
        import re
        
        # Convert markdown headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Convert bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Convert code blocks
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # Convert lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # Convert horizontal rules
        html = re.sub(r'^---\s*$', r'<hr/>', html, flags=re.MULTILINE)
        
        # Convert paragraphs (split by double newlines)
        parts = [p.strip() for p in html.split('\n\n') if p.strip()]
        paragraphs = []
        for part in parts:
            if not any(tag in part for tag in ['<h1>', '<h2>', '<h3>', '<ul>', '<hr/>']):
                paragraphs.append(f'<p>{part}</p>')
            else:
                paragraphs.append(part)
        
        return '\n'.join(paragraphs)

    def process(self):
        if self.workflow is None:
            raise RuntimeError("Agent not initialised. Call initialize() first.")

        # initialize the state & read the dataset
        state = self.initialize_state_from_csv()

        # Generate dataset summary and update state
        state = generate_dataset_summary(state)

        # invoke the workflow
        output_state = self.workflow.invoke(state)  # type: ignore

        # flatten the output
        def _flatten(value):
            return getattr(value, "content", value)

        result = {k: _flatten(v) for k, v in output_state.items()}

        # decode the output
        self.decode_output(result)

        # return the result
        return result
