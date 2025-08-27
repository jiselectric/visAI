#!/usr/bin/env python3

"""
Debug script to check why question generation is failing
"""

import json
import sys

sys.path.append(".")

from Researcher import ResearchConfig, Researcher
from utils.file_operation import load_cached_json


def debug_question_generation():
    # Load dataset profile
    dataset_profile = load_cached_json("dataset_profile.json", "./datasets")

    if not dataset_profile:
        print("ERROR: Could not load dataset profile")
        return

    print(f"Dataset profile loaded with {len(dataset_profile)} columns")
    print("Sample columns:", list(dataset_profile.keys())[:5])

    # Test breadth question generation
    config = ResearchConfig(depth=2, breadth=2, max_workers=2, use_caching=False)
    researcher = Researcher(config, dataset_profile)

    # Test the LLM call directly
    print("\n=== Testing LLM call directly ===")

    dataset_summary = json.dumps(dataset_profile, indent=2)
    print(f"Dataset summary length: {len(dataset_summary)} characters")
    print(f"First 500 chars of dataset summary: {dataset_summary[:500]}...")

    system_prompt = """You are an expert data analyst and researcher. Your task is to generate insightful, 
    visualizable research questions that explore different aspects of the dataset comprehensively.
    
    Generate questions that:
    1. Cover wide-ranging aspects of the data (temporal, categorical, numerical, relational)
    2. Are highly visualizable and would produce compelling charts
    3. Expose meaningful insights about the dataset
    4. Are answerable using the available data columns
    5. Would be interesting to both technical and non-technical audiences"""

    user_prompt = f"""Based on this dataset profile:
    
    {dataset_summary[:2000]}...  
    
    Generate exactly 2 diverse research questions that cover different aspects of the data.
    Each question should be:
    - Specific and actionable
    - Visualizable (can be answered with charts/graphs)
    - Insightful (reveals meaningful patterns or trends)
    
    Return the response as a JSON array with objects containing:
    - "question": the research question
    - "category": the category/aspect it explores (e.g., "temporal", "categorical", "correlation", "distribution")
    - "visualizable": true
    
    Example format:
    [
      {{"question": "How has the number of publications changed over time for each conference?", "category": "temporal", "visualizable": true}},
      {{"question": "What is the distribution of paper types across different conferences?", "category": "categorical", "visualizable": true}}
    ]"""

    print(f"\nUser prompt length: {len(user_prompt)} characters")
    print(f"System prompt length: {len(system_prompt)} characters")

    # Test LLM call
    from utils.llm_operations import invoke_llm_with_prompt

    try:
        response = invoke_llm_with_prompt(
            system_content=system_prompt, prompt_template=user_prompt, replacements={}
        )
        print(f"\n=== LLM Response ===")
        print(f"Response type: {type(response)}")
        print(f"Response length: {len(str(response))}")
        print(f"Response content: '{response}'")

        if response:
            try:
                parsed = json.loads(response)
                print(f"Successfully parsed JSON with {len(parsed)} items")
                for i, item in enumerate(parsed):
                    print(f"  {i+1}. {item}")
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
        else:
            print("Empty response from LLM!")

    except Exception as e:
        print(f"Error calling LLM: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_question_generation()
