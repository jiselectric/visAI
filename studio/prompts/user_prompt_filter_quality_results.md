Analyze these {num_results} research results and determine which ones should be included in the final report:

{results_summary}

Return a JSON array of indices (numbers) for results that should be INCLUDED in the final report.
Example: [0, 2, 5, 7, 9, 11]

Prioritize:
- Unique insights and questions
- Results with valid data (has_data: true)
- Results with visualization code (has_visualization: true)
- Diverse analytical categories

Remove:
- Duplicate or very similar questions
- Results with no data or visualization
- Low-value or redundant analyses