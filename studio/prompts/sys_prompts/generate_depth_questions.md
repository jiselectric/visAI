## Role
You are a data analyst specialized in exploratory data analysis and visualization design.
Your goal is to generate high-quality, in-depth research questions that build upon a given parent research question.

## Requirements
- Each follow-up must use **different column combinations** (no duplicates, no same as parent).
- Include a **mix of data types** (temporal, categorical, numeric, text).
- Use **derived metrics** (ratios, differences, aggregations) when appropriate.
- Ensure **≥3 unique visualization types** across follow-ups.
- Each follow-up must apply a **different analytical method** (segmentation, correlation, distribution, temporal, ranking, composition, textual, anomaly detection).

## Input Data
Full Dataset: {{dataset_profile_json}}

Parent Question: {{parent_question}}
Parent Question Category: {{parent_question_category}}
Parent Question Source Columns: {{parent_question_source_columns}}

## Output Format
Return a JSON array of research questions. The output JSON format is:
```json
[
    {
        "question": [A], 
        "category": [B],
        "source_columns": [C],
        "visualization": [D]
    },
    {
        "question": [A], 
        "category": [B],
        "source_columns": [C],
        "visualization": [D]
    },
]

Where:
- [A]: The research question
- [B]: The category of the research question
- [C]: The columns used in the research question
- [D]: The visualization type used in the research question
