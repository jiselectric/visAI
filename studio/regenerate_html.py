#!/usr/bin/env python3
"""
Script to regenerate HTML with new styling using existing cached data
"""
import json
from agent import Agent

def main():
    # Load the cached Step 6 data
    with open('datasets/06_generated_vegalite_charts_with_narrative.json', 'r') as f:
        step6_data = json.load(f)
    
    # Create a mock research paper components structure
    research_paper_components = {
        "title": {"narrative": "# Visualization Analysis Report"},
        "abstract": {"narrative": "## Abstract\nThis report presents comprehensive visualizations and analysis of the research paper dataset."},
        "methodology": {"narrative": "## Methodology\nWe applied advanced data visualization techniques to reveal insights from the dataset."}
    }
    
    # Add all the visualizations from Step 6
    for key, value in step6_data.items():
        research_paper_components[key] = value
    
    # Add conclusion
    research_paper_components["conclusion"] = {"narrative": "## Conclusion\nThe visualizations reveal important patterns and trends in the research data."}
    
    # Create agent instance and generate HTML
    agent = Agent()
    agent.generate_research_paper_html_report(research_paper_components, "output.html")
    
    print("✅ HTML regenerated with new styling at: output.html")
    print("🌐 You can now view it at: http://localhost:8001/output.html")

if __name__ == "__main__":
    main()