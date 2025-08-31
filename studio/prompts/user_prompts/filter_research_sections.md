## Instructions
As a senior research analyst, your task is to evaluate and filter research results to identify the most compelling and significant findings for inclusion in a final research report. You must select results that demonstrate strong analytical insights, statistical significance, and meaningful contributions to the field.

## Data to Evaluate
```json
{{research_results}}
```

## Requirements
- **Analytical Depth**: Prioritize results that show complex relationships, patterns, or insights beyond simple descriptive statistics
- **Statistical Significance**: Include results with clear statistical evidence, meaningful sample sizes, and reliable data
- **Field Relevance**: Select findings that contribute meaningfully to the research domain and advance understanding
- **Visualization Quality**: Choose results with clear, interpretable visualizations that effectively communicate insights
- **Narrative Strength**: Prefer results with compelling narratives that tell a coherent story about the data
- **Diversity**: Ensure a balanced representation across different types of analysis (temporal, correlation, distribution, etc.)

## Restrictions
- **Avoid Redundancy**: Do not include multiple results that analyze the same relationship or pattern
- **Quality Threshold**: Exclude results with poor data quality, insufficient sample sizes, or unclear visualizations
- **Relevance Filter**: Reject findings that are not directly relevant to the research question or field
- **Complexity Minimum**: Avoid overly simplistic analyses that only provide basic descriptive statistics
- **Narrative Coherence**: Exclude results with weak or unclear narrative explanations

## Examples

### Example 1:
**Research Results**:
```json
[
  {
    "index": 0,
    "question": "What is the correlation between Downloads_Xplore and AminerCitationCount across different Conferences?",
    "category": "correlation",
    "visualization": "scatter plot",
    "narrative": "An examination of the symbiotic relationship between content dissemination and scholarly impact reveals a compelling disassociation across prominent conferences...",
    "statistical_significance": "high",
    "sample_size": 1250,
    "data_quality": "excellent"
  },
  {
    "index": 1,
    "question": "How does the relationship between Downloads_Xplore and AminerCitationCount vary by Conference?",
    "category": "correlation",
    "visualization": "scatter plot",
    "narrative": "Analysis shows that Downloads_Xplore and AminerCitationCount have different correlation patterns across conferences...",
    "statistical_significance": "medium",
    "sample_size": 1250,
    "data_quality": "good"
  },
  {
    "index": 2,
    "question": "What is the distribution of paper lengths across different PaperTypes?",
    "category": "distribution",
    "visualization": "box plot",
    "narrative": "Analysis reveals significant variation in paper length distributions across different paper types...",
    "statistical_significance": "medium",
    "sample_size": 1200,
    "data_quality": "good"
  }
]
```

**Output**: `[0, 2]`

**Reasoning**: Result 0 provides the most comprehensive analysis of the Downloads_Xplore and AminerCitationCount relationship with high statistical significance. Result 1 is excluded as it's redundant - it analyzes the same relationship but with lower significance and less compelling narrative. Result 2 provides unique distribution analysis with medium significance.

### Example 2:
**Research Results**:
```json
[
  {
    "index": 0,
    "question": "How has the number of publications changed over time for each Conference?",
    "category": "temporal",
    "visualization": "line chart",
    "narrative": "Temporal analysis reveals distinct growth patterns across conferences, with InfoVis showing exponential growth...",
    "statistical_significance": "medium",
    "sample_size": 1250,
    "data_quality": "good"
  },
  {
    "index": 1,
    "question": "What is the publication trend over years for each Conference?",
    "category": "temporal",
    "visualization": "line chart",
    "narrative": "The publication trends show varying growth rates across conferences over time...",
    "statistical_significance": "high",
    "sample_size": 1250,
    "data_quality": "excellent"
  },
  {
    "index": 2,
    "question": "Which conferences have the highest citation impact factors?",
    "category": "ranking",
    "visualization": "horizontal bar chart",
    "narrative": "Citation impact analysis reveals that InfoVis leads with an average of 45 citations per paper...",
    "statistical_significance": "medium",
    "sample_size": 1250,
    "data_quality": "good"
  }
]
```

**Output**: `[1, 2]`

**Reasoning**: Result 1 provides the most comprehensive temporal analysis with high significance and detailed growth pattern insights. Result 0 is excluded as it's redundant - it analyzes the same temporal relationship but with lower significance and less detailed narrative. Result 2 provides unique ranking analysis with medium significance.

### Example 3:
**Research Results**:
```json
[
  {
    "index": 0,
    "question": "What are the most common keywords in AuthorKeywords?",
    "category": "textual",
    "visualization": "word cloud",
    "narrative": "Lexical analysis reveals the evolution of visualization research themes, with 'visual analytics' emerging as dominant...",
    "statistical_significance": "medium",
    "sample_size": 1250,
    "data_quality": "good"
  },
  {
    "index": 1,
    "question": "What are the top keywords used in AuthorKeywords?",
    "category": "textual",
    "visualization": "bar chart",
    "narrative": "The most frequently used keywords in the dataset are 'visual analytics' and 'visualization'...",
    "statistical_significance": "medium",
    "sample_size": 1250,
    "data_quality": "good"
  },
  {
    "index": 2,
    "question": "Is there a relationship between paper length and citation count?",
    "category": "correlation",
    "visualization": "scatter plot",
    "narrative": "Analysis reveals a weak positive correlation (r=0.23) between paper length and citations...",
    "statistical_significance": "low",
    "sample_size": 1200,
    "data_quality": "good"
  }
]
```

**Output**: `[0, 1]`

**Reasoning**: Result 0 provides comprehensive textual analysis with medium significance and detailed thematic insights. Result 1 provides complementary keyword analysis with similar significance but different visualization approach. Result 2 is excluded as it has low statistical significance despite being a unique correlation analysis.

## Expected Output
Return a JSON array of indices (numbers) for results that should be INCLUDED in the final report.

## Final Checklist
- [ ] Selected results demonstrate analytical depth beyond simple descriptions
- [ ] Included findings have meaningful statistical significance
- [ ] Results contribute valuable insights to the research domain
- [ ] Visualizations are clear and interpretable
- [ ] Narratives are compelling and well-articulated
- [ ] Selection provides balanced coverage across analysis types
- [ ] Avoided redundant or overlapping results
- [ ] Excluded low-quality or irrelevant findings