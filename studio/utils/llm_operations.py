import json
import re
from typing import Any, Dict, Union, List

from helpers import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


def invoke_llm_with_prompt(
    system_prompt: str,
    user_prompt: str,
    system_prompt_replacements: Dict[str, Any],
    user_prompt_replacements: Dict[str, Any],
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    """Standardized LLM invocation with prompt template replacement."""
    # Replace template variables in system prompt
    for key, value in system_prompt_replacements.items():
        system_prompt = system_prompt.replace(key, str(value))

    # Replace template variables in user prompt
    for key, value in user_prompt_replacements.items():
        user_prompt = user_prompt.replace(key, str(value))

    llm = get_llm(temperature=temperature, max_tokens=max_tokens)

    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
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
