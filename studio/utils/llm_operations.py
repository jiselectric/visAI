import json
import re
from typing import Any, Dict, Union, List

from helpers import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


def invoke_llm_with_prompt(
    system_content: str,
    prompt_template: str,
    replacements: Dict[str, str],
    temperature: float = 0,
    max_tokens: int = 4096,
) -> str:
    """Standardized LLM invocation with prompt template replacement."""
    # Replace template variables in prompt
    formatted_prompt = prompt_template
    for key, value in replacements.items():
        formatted_prompt = formatted_prompt.replace(key, value)

    llm = get_llm(temperature=temperature, max_tokens=max_tokens)

    response = llm.invoke(
        [
            SystemMessage(content=system_content),
            HumanMessage(content=formatted_prompt),
        ]
    )

    return getattr(response, "content", str(response))


def extract_json_from_response(
    response_content: str,
) -> Union[Dict[str, Any], List[Any]]:
    """Extract and parse JSON from LLM response with error handling."""
    try:
        # Try to find JSON in markdown code blocks first
        json_match = re.search(r"```json\s*(.*?)\s*```", response_content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try to find JSON array boundaries first
        json_match = re.search(r"\[.*\]", response_content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # Try to find JSON object boundaries
        json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # If no JSON found, return error structure
        return {
            "error": "Could not parse JSON response",
            "raw_response": response_content,
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON parsing failed: {e}",
            "raw_response": response_content,
        }
