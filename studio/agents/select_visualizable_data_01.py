import json

from utils.file_operation import load_cached_json, load_prompt_template, save_json_data
from utils.llm_operations import extract_json_from_response, invoke_llm_with_prompt

from ..agent import State


# Step 1: Select appropriate columns to visualize
def select_visualizable_data(state: State):
    print("Step 1 / 10: Select Visualizable Columns")
    dataset_summary = state["dataset_summary"]

    # Check if cached result exists
    cached_data = load_cached_json("visualizable_dataset.json")
    if cached_data:
        print("Using cached - visualizable_dataset.json")
        return {"visualizable_dataset": cached_data}

    sys_prompt = load_prompt_template("select_visualizable_data_01.md")

    # Generate response using LLM
    dataset_summary_json = json.dumps(dataset_summary, indent=2, ensure_ascii=False)

    response_content = invoke_llm_with_prompt(
        system_content="You are a data visualization expert. Given a JSON object that summarizes each column of a dataset (with fields like column_name, examples, unique_value_count, top_frequencies, etc.), select only the columns appropriate for visualization and output them in the specified JSON format.",
        prompt_template=sys_prompt,
        replacements={
            "{{dataset_summary_json}}": dataset_summary_json,
        },
    )

    # Extract JSON from response
    visualizable_dataset = extract_json_from_response(response_content)

    # Save the result
    save_json_data(visualizable_dataset, "visualizable_dataset.json")

    return {"visualizable_dataset": visualizable_dataset}
