import json
import os
from typing import Any, Counter, Dict, List, Union

from helpers import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from report_html import generate_html_report
from report_pdf import generate_pdf_report
from typing_extensions import TypedDict
from utils.data_utils import generate_dataset_summary
from utils.file_operation import (
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
        },
    )

    # Extract JSON from response
    visualization_queries = extract_json_from_response(response_content)

    # Save the result
    save_json_data(visualization_queries, "02_visualization_queries.json")

    return {"visualization_queries": visualization_queries}


# Step 3: Select top-K queries that would produce the research paper with natural logical flow
def select_top_k_visualization_queries(state: State):
    print("Step 3 / 10: Select Top-K Visualization Queries")
    visualization_queries = state["visualization_queries"]

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

    K = 15  # number of queries to select
    response_content = invoke_llm_with_prompt(
        system_content="You are a highly skilled scholar who is writing a research paper. You are given a list of visualization queries that give deep insights into the dataset. Your task is to select the top-{K} queries that would produce the research paper with natural logical flow.",
        prompt_template=sys_prompt,
        replacements={
            "{{K}}": str(K),
            "{{visualization_queries_json}}": visualization_queries_json,
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
    top_k_visualization_queries = state["top_k_visualization_queries"]

    # Check if cached result exists
    cached_data = load_cached_json("04_computed_visualization_data.json")
    if cached_data:
        print("Using cached - 04_computed_visualization_data.json")
        return {"computed_visualization_data": cached_data}

    sys_prompt = load_prompt_template("04_compute_data_for_visualization_queries.md")


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
    builder.add_node("generate_msg", generate_msg)

    builder.add_edge(START, "select_visualizable_data")
    builder.add_edge("select_visualizable_data", "generate_visualization_queries")
    builder.add_edge(
        "generate_visualization_queries", "select_top_k_visualization_queries"
    )
    builder.add_edge("select_top_k_visualization_queries", END)
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
        # if the final output contains Vega-Lite codes, then use generate_html_report
        # if the final output contains Python codes, then use generate_pdf_report

        # generate_pdf_report(output, "output.pdf")
        generate_html_report(output, "output.html")

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
