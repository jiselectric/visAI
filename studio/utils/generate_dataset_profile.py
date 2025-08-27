from typing import Any, Dict, Union

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)


def extract_dtype_info(series: pd.Series) -> Dict[str, Any]:
    """
    Extract comprehensive dtype information from a pandas series.
    Handles edge cases and provides accurate type classification.
    """
    # Get the actual pandas dtype
    pandas_dtype = str(series.dtype)

    # Handle numpy dtypes and convert to readable format
    if "int" in pandas_dtype:
        d_type = "int"
    elif "float" in pandas_dtype:
        d_type = "float"
    elif "bool" in pandas_dtype:
        d_type = "bool"
    elif "datetime" in pandas_dtype or "time" in pandas_dtype:
        d_type = "datetime"
    elif "category" in pandas_dtype:
        d_type = "category"
    elif "object" in pandas_dtype:
        # Check if it's actually string data
        if series.dropna().apply(lambda x: isinstance(x, str)).all():
            d_type = "string"
        else:
            d_type = "object"
    else:
        d_type = "unknown"

    return {"d_type": d_type, "pandas_dtype": pandas_dtype}


def infer_data_type(series: pd.Series, d_type: str) -> str:
    """
    Infer the semantic type of the data for analysis purposes.
    """
    if d_type in ["int", "float"]:
        # Check if it's actually categorical despite being numeric
        unique_ratio = series.nunique() / len(series.dropna())
        if unique_ratio < 0.1:  # Less than 10% unique values
            return "categorical"
        elif d_type == "int" and series.min() >= 0 and series.max() <= 100:
            # Likely a percentage or score
            return "continuous"
        else:
            return "continuous"
    elif d_type == "datetime":
        return "temporal"
    elif d_type == "bool":
        return "categorical"
    elif d_type == "category":
        return "categorical"
    elif d_type == "string":
        # Check if it's text or categorical
        unique_ratio = series.nunique() / len(series.dropna())
        avg_length = series.dropna().str.len().mean()

        if unique_ratio < 0.3:  # Less than 30% unique values
            return "categorical"
        elif avg_length > 50:  # Long text
            return "text"
        else:
            return "categorical"
    elif d_type == "object":
        # Mixed types or complex objects
        return "mixed"
    else:
        return "unknown"


def get_numeric_stats(series: pd.Series) -> Dict[str, Any]:
    """
    Extract comprehensive numeric statistics for continuous variables.
    """
    # Remove infinite values for calculations
    clean_series = series.replace([np.inf, -np.inf], np.nan)

    stats = {}

    # Count infinite values
    infinite_mask = np.isinf(series)
    infinite_count = infinite_mask.sum()
    infinite_percentage = (infinite_count / len(series)) * 100

    stats.update(
        {
            "infinite_values": int(infinite_count),
            "infinite_values_percentage": round(infinite_percentage, 2),
        }
    )

    # Basic statistics (only on finite values)
    if len(clean_series.dropna()) > 0:
        stats.update(
            {
                "mean": float(clean_series.mean()),
                "median": float(clean_series.median()),
                "std": float(clean_series.std()),
                "min": float(clean_series.min()),
                "max": float(clean_series.max()),
                "q25": float(clean_series.quantile(0.25)),
                "q75": float(clean_series.quantile(0.75)),
            }
        )
    else:
        stats.update(
            {
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "q25": None,
                "q75": None,
            }
        )

    return stats


def generate_dataset_profile(
    df: pd.DataFrame, top_k: int = 10
) -> Dict[str, Dict[str, Any]]:
    """
    Generate comprehensive dataset profile for each column.

    Args:
        df: Input DataFrame
        top_k: Number of top frequencies and examples to include

    Returns:
        Dictionary with column names as keys and their profiles as values
    """
    profile = {}
    total_rows = len(df)

    for column in df.columns:
        series = df[column]

        # Basic counts
        missing_count = series.isnull().sum()
        missing_percentage = (missing_count / total_rows) * 100
        distinct_count = series.nunique(dropna=True)
        distinct_percentage = (
            (distinct_count / (total_rows - missing_count)) * 100
            if (total_rows - missing_count) > 0
            else 0
        )

        # Get dtype information
        dtype_info = extract_dtype_info(series)
        d_type = dtype_info["d_type"]

        # Infer semantic type
        type_inferred = infer_data_type(series, d_type)

        # Top frequencies (exclude NaN)
        top_freqs = series.value_counts(dropna=True).head(top_k).to_dict()

        # Examples (convert to strings, exclude NaN)
        examples = series.dropna().astype(str).unique()[:top_k].tolist()

        # Initialize column profile
        column_profile = {
            "total_rows": total_rows,
            "distinct_values": int(distinct_count),
            "distinct_values_percentage": round(distinct_percentage, 2),
            "missing_values": int(missing_count),
            "missing_values_percentage": round(missing_percentage, 2),
            "d_type": d_type,
            "type_inferred": type_inferred,
            "top_frequencies": top_freqs,
            "examples": examples,
        }

        # Add numeric statistics for continuous variables
        if type_inferred in ["continuous", "numeric"] and d_type in ["int", "float"]:
            numeric_stats = get_numeric_stats(series)
            column_profile.update(numeric_stats)

        profile[column] = column_profile

    return profile
