#!/usr/bin/env python3

"""
Simple test script to verify the workflow works step by step
"""

import os
import sys

sys.path.append(".")

from agent import Agent


def test_initialization():
    """Test agent initialization"""
    print("=== Testing Agent Initialization ===")
    agent = Agent()
    agent.initialize()

    state = agent.initialize_state_from_csv()
    print(
        f"Dataset loaded: {state['dataset_info']['num_rows']} rows, {len(state['dataset_info']['attributes'])} columns"
    )
    return agent, state


def test_step1(agent, state):
    """Test step 1 - research question generation"""
    print("\n=== Testing Step 1: Research Question Generation ===")

    # Import the step function
    from agent import step1_generate_research_questions

    result = step1_generate_research_questions(state)
    questions = result["research_questions"]

    print(f"Generated {len(questions)} research questions")
    for i, q in enumerate(questions[:5]):  # Show first 5
        print(
            f"  {i+1}. {q['question']} (Category: {q['category']}, Level: {q['level']})"
        )

    return {**state, **result}


def test_step2(agent, state):
    """Test step 2 - conduct research"""
    print("\n=== Testing Step 2: Conduct Research ===")

    # Import the step function
    from agent import step2_conduct_research

    # Limit to first 2 questions for testing
    limited_questions = state["research_questions"][:2]
    limited_state = {**state, "research_questions": limited_questions}

    result = step2_conduct_research(limited_state)
    research_results = result["research_results"]

    print(f"Completed research for {len(research_results)} questions")
    for i, r in enumerate(research_results):
        print(f"  {i+1}. {r['title']}")
        print(f"      Data points: {len(r.get('computed_data', []))}")
        print(
            f"      Has visualization code: {'Yes' if r.get('visualization_code') else 'No'}"
        )

    return {**limited_state, **result}


def test_step3(agent, state):
    """Test step 3 - arrange results"""
    print("\n=== Testing Step 3: Arrange Results ===")

    # Import the step function
    from agent import step3_arrange_results

    result = step3_arrange_results(state)
    final_arrangement = result["final_arrangement"]

    print(f"Final arrangement created:")
    print(f"  Title: {final_arrangement.get('title', 'N/A')}")
    print(f"  Results: {len(final_arrangement.get('results', []))}")
    print(
        f"  Has introduction: {'Yes' if final_arrangement.get('introduction') else 'No'}"
    )
    print(f"  Has conclusion: {'Yes' if final_arrangement.get('conclusion') else 'No'}")

    return {**state, **result}


def test_step4(agent, state):
    """Test step 4 - HTML generation"""
    print("\n=== Testing Step 4: HTML Generation ===")

    html_content = agent.decode_output(state)
    html_length = len(html_content)

    print(f"HTML generated: {html_length} characters")
    print("HTML file created: output.html")

    # Check if HTML contains expected elements
    has_title = "<h1>" in html_content
    has_charts = "data:image/png;base64," in html_content
    has_results = "Research Findings" in html_content

    print(f"  Has title: {has_title}")
    print(f"  Has charts: {has_charts}")
    print(f"  Has results section: {has_results}")


def main():
    """Run the step-by-step test"""
    try:
        # Test initialization
        agent, state = test_initialization()

        # Test Step 1
        state = test_step1(agent, state)

        # Test Step 2 (limited)
        state = test_step2(agent, state)

        # Test Step 3
        state = test_step3(agent, state)

        # Test Step 4
        test_step4(agent, state)

        print("\n=== All Tests Completed Successfully! ===")

    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
