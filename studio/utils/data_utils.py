from typing import Any, Counter, Dict, List

import pandas as pd
import numpy as np
from utils.file_operation import save_json_data


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
    # Use synthetic dataset if it exists, otherwise fall back to original
    import os

    if os.path.exists("synthetic_dataset.csv"):
        df = pd.read_csv("synthetic_dataset.csv")
    else:
        df = pd.read_csv("dataset.csv")

    samples = {}
    for col in columns:
        if col in df.columns:
            n_samples = min(sample_size, len(df[col].dropna()))
            samples[col] = df[col].dropna().sample(n=n_samples).tolist()

    return samples


def execute_pandas_query_for_computation(query: str) -> Dict[str, Any]:
    """Execute pandas code and return the computed data in the correct format"""
    import pandas as pd

    # Load the dataset
    df = pd.read_csv("synthetic_dataset.csv")

    # Create a local namespace with df available
    local_namespace = {"df": df, "pd": pd}

    try:
        # Execute the pandas code
        exec(query, globals(), local_namespace)

        # Get the result variable
        if "result" in local_namespace:
            result = local_namespace["result"]

            # Convert pandas DataFrame to the expected format
            if hasattr(result, "to_dict") and hasattr(result, "index"):
                # This is a DataFrame - convert to records format (list of dicts)
                if hasattr(result, "to_dict"):
                    # Use 'records' orientation to get list of dicts
                    return result.to_dict("records")
                else:
                    return result.to_dict()
            elif hasattr(result, "tolist"):
                # This is a Series or other pandas object
                return result.tolist()
            else:
                # This is a regular Python object
                return result
        else:
            return {"error": "No 'result' variable found in executed code"}

    except Exception as e:
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
    import pandas as pd
    import numpy as np
    import json

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
