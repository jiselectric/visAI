"""File operation utilities for caching and data persistence."""

import json
import os
from typing import Any, Dict, Optional


def load_cached_json(
    file_path: str, dataset_dir: str = "./datasets"
) -> Optional[Dict[str, Any]]:
    """Load cached JSON data if it exists."""
    full_path = os.path.join(dataset_dir, file_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json_data(
    data: Dict[str, Any], file_path: str, dataset_dir: str = "./datasets"
) -> None:
    """Save data to JSON file with proper encoding and numpy type conversion."""
    import numpy as np

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

    # Convert numpy types before saving
    clean_data = convert_numpy_types(data)

    os.makedirs(dataset_dir, exist_ok=True)
    full_path = os.path.join(dataset_dir, file_path)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)


def load_prompt_template(prompt_path: str) -> str:
    """Load prompt template with proper encoding."""
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(os.path.dirname((curr_dir)), "prompts")
    full_path = os.path.join(prompt_dir, prompt_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")


def read_csv_data(csv_path: str) -> Dict[str, Any]:
    """Read CSV data and return structured information."""
    import csv

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data_rows = list(reader)

        return {
            "headers": reader.fieldnames or [],
            "data": data_rows,
            "num_rows": len(data_rows),
        }


def clean_markdown_output(llm_output: str, output_type: str = "generic") -> str:
    """
    Clean markdown output from LLM and extract the relevant content.

    Args:
        llm_output: Raw output from LLM that may contain markdown, code blocks, etc.
        output_type: Type of output to extract ("pandas", "vegalite", "json", "generic")

    Returns:
        Clean content string without markdown formatting

    Examples:
        Input: "```python\nresult = df.groupby('Year').size()\n```"
        Output: "result = df.groupby('Year').size()"

        Input: "```json\n{\"$schema\": \"...\"}\n```"
        Output: "{\"$schema\": \"...\"}"
    """
    import re

    # Remove markdown code blocks (```python, ```json, ```, etc.)
    code_block_pattern = r"```(?:python|json|javascript|html|css)?\s*\n?(.*?)\n?```"
    code_match = re.search(code_block_pattern, llm_output, re.DOTALL)

    if code_match:
        # Extract code from code block
        content = code_match.group(1).strip()
    else:
        # If no code block found, try to extract relevant lines based on output type
        lines = llm_output.split("\n")
        content_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines, markdown formatting, and explanatory text
            if (
                line
                and not line.startswith("#")
                and not line.startswith("**")
                and not line.startswith("*")
                and not line.startswith("-")
                and not line.startswith("##")
                and not line.startswith("```")
                and not line.startswith(">")
                and not line.startswith("|")
            ):
                # For pandas queries, look for specific patterns
                if output_type == "pandas" and (
                    "=" in line or "df." in line or "result" in line
                ):
                    content_lines.append(line)
                # For Vega-Lite/JSON, look for JSON-like patterns
                elif output_type in ["vegalite", "json"] and (
                    "{" in line or "}" in line or '"' in line or ":" in line
                ):
                    content_lines.append(line)
                # For generic output, include lines that look like code/content
                elif output_type == "generic" and (
                    "=" in line
                    or "{" in line
                    or "}" in line
                    or "[" in line
                    or "]" in line
                ):
                    content_lines.append(line)
                # For generic output, also include lines that don't look like markdown
                elif output_type == "generic" and not any(
                    line.startswith(prefix)
                    for prefix in ["#", "**", "*", "-", "##", "```", ">", "|"]
                ):
                    content_lines.append(line)

        content = "\n".join(content_lines)

    # Clean up any remaining markdown artifacts
    content = re.sub(r"\*\*.*?\*\*", "", content)  # Remove bold text
    content = re.sub(r"\*.*?\*", "", content)  # Remove italic text
    content = re.sub(r"`.*?`", "", content)  # Remove inline code
    content = re.sub(r"\[.*?\]\(.*?\)", "", content)  # Remove links
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)  # Remove images

    # Remove any leading/trailing whitespace and empty lines
    content = "\n".join(line for line in content.split("\n") if line.strip())

    return content


def load_or_execute_cached_step(
    step_description: str, cache_filename: str, execute_func
):
    """
    Helper function to deduplicate caching logic in workflow steps.

    Args:
        step_description: Human-readable description for logging
        cache_filename: Name of the cache file to check/save
        execute_func: Function to execute if cache miss

    Returns:
        Result from cache or execution
    """
    print(f"  {step_description}...")

    # Try to load from cache
    cached_result = load_cached_json(cache_filename)
    if cached_result:
        print(f"    Using cached - {cache_filename}")
        return cached_result

    # Cache miss - execute the function
    result = execute_func()
    save_json_data(result, cache_filename)
    return result
