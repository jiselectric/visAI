"""
Column Enhancement Agents
Helper functions for multi-agent column selection with direct selection and advanced enhancements.
"""

import json
from .file_operation import load_prompt_template
from .llm_operations import extract_json_from_response, invoke_llm_with_prompt


def select_direct_visualizable_columns(dataset_summary_json: str) -> dict:
    """
    Agent 0: Direct column selection (foundation step)
    
    Selects obviously visualizable columns using the original logic.
    This ensures we capture all the easy wins before moving to advanced enhancements.
    
    Args:
        dataset_summary_json: JSON string of dataset summary
        
    Returns:
        dict: Directly visualizable columns following original selection criteria
    """
    
    sys_prompt = load_prompt_template("01_select_visualizable_dataset.md")
    
    response_content = invoke_llm_with_prompt(
        system_content="You are a data visualization expert. Given a JSON object that summarizes each column of a dataset (with fields like column_name, examples, unique_value_count, top_frequencies, etc.), select only the columns appropriate for visualization and output them in the specified JSON format.",
        prompt_template=sys_prompt,
        replacements={
            "{{dataset_summary_json}}": dataset_summary_json,
        },
    )
    
    return extract_json_from_response(response_content)


def detect_synthetic_opportunities(dataset_summary_json: str) -> dict:
    """
    Agent 1: Detect opportunities for synthetic column generation
    
    Identifies columns that can be mathematically or logically combined
    to create new, more visualizable columns.
    
    Args:
        dataset_summary_json: JSON string of dataset summary
        
    Returns:
        dict: Array of synthetic opportunities with operations and rationale
    """
    
    sys_prompt = load_prompt_template("01a_detect_synthetic_opportunities.md")
    
    response_content = invoke_llm_with_prompt(
        system_content="You are a data relationship expert. Analyze the dataset summary and identify columns that can be mathematically or logically combined to create new, more visualizable columns. Return only a JSON array of opportunities.",
        prompt_template=sys_prompt,
        replacements={
            "{{dataset_summary_json}}": dataset_summary_json,
        },
    )
    
    return extract_json_from_response(response_content)


def detect_binning_opportunities(dataset_summary_json: str) -> dict:
    """
    Agent 2: Detect opportunities for numerical binning
    
    Identifies numerical columns with high cardinality that can be binned 
    into meaningful categories for better visualization.
    
    Args:
        dataset_summary_json: JSON string of dataset summary
        
    Returns:
        dict: Array of binning opportunities with proposed bins and rationale
    """
    
    sys_prompt = load_prompt_template("01b_detect_binning_opportunities.md")
    
    response_content = invoke_llm_with_prompt(
        system_content="You are a data categorization expert. Analyze the dataset summary and identify numerical columns with high cardinality that can be binned into meaningful categories for better visualization. Return only a JSON array of opportunities.",
        prompt_template=sys_prompt,
        replacements={
            "{{dataset_summary_json}}": dataset_summary_json,
        },
    )
    
    return extract_json_from_response(response_content)


def detect_extraction_opportunities(dataset_summary_json: str) -> dict:
    """
    Agent 3: Detect opportunities for text extraction
    
    Identifies text columns that contain hidden categorical information 
    that can be extracted for visualization.
    
    Args:
        dataset_summary_json: JSON string of dataset summary
        
    Returns:
        dict: Array of extraction opportunities with categories and methods
    """
    
    sys_prompt = load_prompt_template("01c_detect_extraction_opportunities.md")
    
    response_content = invoke_llm_with_prompt(
        system_content="You are a text analysis expert. Analyze the dataset summary and identify text columns that contain hidden categorical information that can be extracted for visualization. Return only a JSON array of opportunities.",
        prompt_template=sys_prompt,
        replacements={
            "{{dataset_summary_json}}": dataset_summary_json,
        },
    )
    
    return extract_json_from_response(response_content)


def orchestrate_final_selection(
    dataset_summary_json: str,
    direct_columns: dict,
    synthetic_opportunities: dict, 
    binning_opportunities: dict, 
    extraction_opportunities: dict
) -> dict:
    """
    Agent 4: Final orchestrator - combine direct selection with advanced opportunities
    
    Combines directly selected columns with synthetic, binning, and extraction opportunities
    into a cohesive visualization dataset. Ensures no obvious visualizable columns are missed.
    
    Args:
        dataset_summary_json: JSON string of original dataset summary
        direct_columns: Results from direct column selection (foundation)
        synthetic_opportunities: Results from synthetic detection agent
        binning_opportunities: Results from binning detection agent  
        extraction_opportunities: Results from extraction detection agent
        
    Returns:
        dict: Final selected columns for visualization with enhanced metadata
    """
    
    sys_prompt = load_prompt_template("01d_orchestrate_final_selection.md")
    
    response_content = invoke_llm_with_prompt(
        system_content="You are the final decision-maker for selecting the optimal set of columns for visualization. Combine directly selected columns with synthetic, binning, and extraction opportunities into a cohesive visualization dataset. Prioritize keeping all direct columns and adding the best enhancements. Return only the final JSON object.",
        prompt_template=sys_prompt,
        replacements={
            "{{dataset_summary_json}}": dataset_summary_json,
            "{{direct_columns_json}}": json.dumps(direct_columns, indent=2),
            "{{synthetic_opportunities_json}}": json.dumps(synthetic_opportunities, indent=2),
            "{{binning_opportunities_json}}": json.dumps(binning_opportunities, indent=2),
            "{{extraction_opportunities_json}}": json.dumps(extraction_opportunities, indent=2),
        },
    )
    
    return extract_json_from_response(response_content)