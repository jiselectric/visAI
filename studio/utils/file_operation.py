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
    """Save data to JSON file with proper encoding."""
    os.makedirs(dataset_dir, exist_ok=True)
    full_path = os.path.join(dataset_dir, file_path)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_prompt_template(prompt_path: str, prompt_dir: str = "./prompts") -> str:
    """Load prompt template with proper encoding."""
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


def clean_pandas_query(llm_output: str) -> str:
    import re

    # Remove markdown code blocks (```python, ```, etc.)
    code_block_pattern = r"```(?:python)?\s*\n?(.*?)\n?```"
    code_match = re.search(code_block_pattern, llm_output, re.DOTALL)

    if code_match:
        # Extract code from code block
        code = code_match.group(1).strip()
    else:
        # If no code block found, try to extract lines that look like Python code
        lines = llm_output.split("\n")
        code_lines = []

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
                and "=" in line
                or "df." in line
                or "result" in line
            ):
                code_lines.append(line)

        code = "\n".join(code_lines)

    # Clean up any remaining markdown artifacts
    code = re.sub(r"\*\*.*?\*\*", "", code)  # Remove bold text
    code = re.sub(r"\*.*?\*", "", code)  # Remove italic text
    code = re.sub(r"`.*?`", "", code)  # Remove inline code

    # Remove any leading/trailing whitespace and empty lines
    code = "\n".join(line for line in code.split("\n") if line.strip())

    return code
