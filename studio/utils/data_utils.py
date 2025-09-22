from typing import Any, Counter, Dict, List

import numpy as np
import pandas as pd
from utils.file_operation import save_json_data

# Dataset Path
DATASET_PATH = "./input_datasets/Insurance_dataset.csv"


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def chunk_list(lst: List[Any], batch_size: int):
    """Split a list into batches of specified size"""
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]


def generate_dataset_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive summary of dataset attributes and return updated state"""
    dataset_info = state.get("dataset_info", {})
    dataset_rows = dataset_info.get("rows", [])
    attributes = dataset_info.get("attributes", [])

    if not isinstance(dataset_rows, list):
        raise ValueError("Rows must be a list")
    if not isinstance(attributes, list):
        raise ValueError("Attributes must be a list")

    summaries = {}
    for attribute in attributes:
        values = [row.get(attribute, None) for row in dataset_rows if attribute in row]
        values = [v for v in values if v is not None]  # Remove nulls

        all_examples = []
        counter = Counter()

        batches = chunk_list(values, batch_size=10)
        for batch in batches:
            counter.update(batch)
            all_examples.extend(batch)

        # Deduplicate and truncate to 10 representative examples
        unique_examples = []
        seen = set()
        for v in all_examples:
            if v not in seen:
                seen.add(v)
                unique_examples.append(v)
            if len(unique_examples) == 10:
                break

        # Final summary for the column
        summaries[attribute] = {
            "column_name": attribute,
            "examples": unique_examples,
            "unique_value_count": len(set(values)),
            "top_frequencies": dict(counter.most_common(5)),
        }

    # Save dataset summary
    output_dir = "./datasets"
    save_json_data(summaries, "00_dataset_summary.json", output_dir)

    # Return updated state with dataset_summary added
    updated_state = state.copy()
    updated_state["dataset_summary"] = summaries
    return updated_state


def sample_data(columns, sample_size):
    # Use main dataset
    import os

    df = pd.read_csv(DATASET_PATH)

    samples = {}
    for col in columns:
        if col in df.columns:
            n_samples = min(sample_size, len(df[col].dropna()))
            samples[col] = df[col].dropna().sample(n=n_samples).tolist()

    return samples


def execute_pandas_query_for_computation(
    query: str, ephemeral: bool = True
) -> Dict[str, Any]:
    """
    Execute pandas code and return the computed data + capture any generated charts

    Args:
        query: Pandas code to execute
        ephemeral: If True, compute data on-demand without persistent storage (saves memory)

    Returns:
        Dict containing computed data, chart path, and execution metadata
    """
    import gc
    import warnings

    import matplotlib
    import pandas as pd

    matplotlib.use("Agg")  # Use non-interactive backend
    warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive")
    import os
    import time

    import matplotlib.pyplot as plt
    import seaborn as sns

    # Load the dataset
    df = pd.read_csv(DATASET_PATH)

    # Create unique chart filename
    timestamp = str(int(time.time() * 1000))
    chart_path = f"visualizations/chart_{timestamp}.png"

    # Ensure visualizations directory exists
    os.makedirs("visualizations", exist_ok=True)

    # Create a local namespace with df and visualization libraries available
    local_namespace = {
        "df": df,
        "pd": pd,
        "plt": plt,
        "sns": sns,
        "chart_path": chart_path,
    }

    chart_generated = False
    result_data = None

    try:
        # Execute the pandas code (JIT computation happens here)
        exec(query, globals(), local_namespace)

        # Check if any plots were created
        if plt.get_fignums():
            # Save all figures
            for i, fig_num in enumerate(plt.get_fignums()):
                fig = plt.figure(fig_num)
                if i == 0:
                    fig.savefig(chart_path, dpi=150, bbox_inches="tight")
                    chart_generated = True
                else:
                    # Save additional figures with different names
                    additional_path = f"visualizations/chart_{timestamp}_{i}.png"
                    fig.savefig(additional_path, dpi=150, bbox_inches="tight")
                plt.close(fig)

        # Get the result variable (computed on-demand)
        if "result" in local_namespace:
            result = local_namespace["result"]

            if ephemeral:
                # For ephemeral mode: computation uses ALL data, but output can be sampled for efficiency
                if hasattr(result, "to_dict") and hasattr(result, "index"):
                    # This is a DataFrame - NOTE: computation already used all data
                    if len(result) > 100:
                        # Sample OUTPUT data for large results to save memory (computation was on full data)
                        sampled_result = (
                            result.head(50).append(result.tail(50))
                            if len(result) > 100
                            else result
                        )
                        result_data = {
                            "sampled_data": sampled_result.to_dict("records"),
                            "total_rows": len(result),
                            "note": f"Computation used all {len(result)} rows, output sampled for display efficiency",
                            "computation_complete": True,
                        }
                    else:
                        result_data = result.to_dict("records")
                elif hasattr(result, "tolist"):
                    # This is a Series or other pandas object
                    if hasattr(result, "__len__") and len(result) > 1000:
                        result_data = {
                            "sampled_data": result.head(1000).tolist(),
                            "total_length": len(result),
                            "note": f"Computation used all {len(result)} items, output sampled for display",
                            "computation_complete": True,
                        }
                    else:
                        result_data = result.tolist()
                else:
                    # This is a regular Python object (usually aggregated results)
                    result_data = result
            else:
                # Original behavior for backward compatibility
                if hasattr(result, "to_dict") and hasattr(result, "index"):
                    result_data = result.to_dict("records")
                elif hasattr(result, "tolist"):
                    result_data = result.tolist()
                else:
                    result_data = result
        else:
            result_data = {"error": "No 'result' variable found in executed code"}

        # Memory cleanup for ephemeral mode
        if ephemeral:
            # Clear large objects from local namespace
            if "result" in local_namespace and hasattr(
                local_namespace["result"], "memory_usage"
            ):
                del local_namespace["result"]
            # Force garbage collection
            gc.collect()

        # Return both data and chart info
        return {
            "data": result_data,
            "chart_path": chart_path if chart_generated else None,
            "has_chart": chart_generated,
            "ephemeral_mode": ephemeral,
            "execution_timestamp": timestamp,
        }

    except Exception as e:
        # Close any open figures in case of error
        plt.close("all")
        # Memory cleanup on error
        if ephemeral:
            gc.collect()
        return {"error": f"Error executing pandas code: {str(e)}"}


def execute_pandas_query_for_synthetic_dataset(
    dataset: pd.DataFrame, query: str
) -> pd.DataFrame:
    """
    Execute pandas code on the given dataset to add synthetic columns

    Args:
        dataset: DataFrame to modify (passed by reference, will be modified in-place)
        query: Pandas code to execute (should create new column(s) in df)

    Returns:
        pd.DataFrame: The modified dataset with new synthetic column(s)
    """
    import json

    import numpy as np
    import pandas as pd

    # Create execution environment with the passed dataset
    local_namespace = {"df": dataset, "pd": pd, "np": np, "json": json}

    try:
        # Execute the pandas code (modifies df in-place)
        exec(query, globals(), local_namespace)

        # Get the modified DataFrame
        result_df = local_namespace["df"]

        # Convert numpy types to avoid JSON serialization issues later
        for col in result_df.columns:
            if result_df[col].dtype == "int64":
                result_df[col] = result_df[col].astype("object")
            elif result_df[col].dtype == "float64":
                result_df[col] = result_df[col].astype("object")

        return result_df

    except Exception as e:
        print(f"Error executing pandas query: {str(e)}")
        print(f"Query was: {query}")
        # Return the dataset unchanged if execution fails
        return dataset
