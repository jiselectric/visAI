#!/usr/bin/env python3

"""
Test the fixed question generation
"""

import sys

sys.path.append(".")

from Researcher import ResearchConfig, Researcher
from utils.file_operation import load_cached_json


def test_fixed_questions():
    # Load dataset profile
    dataset_profile = load_cached_json("dataset_profile.json", "./datasets")

    if not dataset_profile:
        print("ERROR: Could not load dataset profile")
        return

    print(f"Dataset profile loaded with {len(dataset_profile)} columns")

    # Test with the fixed Researcher class
    config = ResearchConfig(depth=2, breadth=3, max_workers=2, use_caching=False)
    researcher = Researcher(config, dataset_profile)

    print("\n=== Testing fixed question generation ===")
    try:
        questions = researcher.step1_generate_research_questions()

        print(f"Successfully generated {len(questions)} questions!")

        # Show breadth questions
        breadth_qs = [q for q in questions if q.level == 0]
        print(f"\n=== {len(breadth_qs)} Breadth Questions ===")
        for i, q in enumerate(breadth_qs):
            print(f"  {i+1}. {q.question}")
            print(f"     Category: {q.category}")

        # Show depth questions
        depth_qs = [q for q in questions if q.level > 0]
        print(f"\n=== {len(depth_qs)} Depth Questions ===")
        for i, q in enumerate(depth_qs[:5]):  # Show first 5
            print(f"  {i+1}. {q.question}")
            print(f"     Parent: {q.parent_question}")
            print(f"     Level: {q.level}, Category: {q.category}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_fixed_questions()
