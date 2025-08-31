## Instructions
- Output a JSON array with keys: question, category, source_columns, visualization.
- Generate EXACTLY **{{breadth}}** diverse, high-quality research questions. 
- Cover temporal, categorical, numeric, text, and derived metrics.
- At least 70% must use multiple columns.

### Input Data:
```json
{{dataset_profile_json}}
```

## Requriements
Column Rules:
- Use 80%+ of dataset columns.
- No column >2 uses.
- Include underutilized and less obvious columns.

Visualization Rules:
- EXACTLY 2 visualizations per type: scatter, heatmap, line, box, histogram, stacked bar, word cloud.
- Each visualization should be unique

Analytical Categories:
- Must include temporal, correlation, distribution, ranking, categorical, text, composition.
- Include simple, relational, and complex (derived) analyses.

## Prohibitions
- No duplicate sets of source_columns.
- No repeated categories.
- No repeated visualization types.
- No repeated source_columns.
- No repeated questions.
- No repeated answers.
- No traditional charts for frequency, use word cloud only.

## Example
```json
[
  {
    "question": "How has the proportion of different `PaperType` categories shifted across `Conference` venues over time?",
    "category": "composition+temporal",
    "source_columns": ["Year", "Conference", "PaperType"],
    "visualization": "stacked area chart"
  },
  {
    "question": "What is the relationship between `Downloads_Xplore` and `AminerCitationCount`, segmented by `PaperType`?",
    "category": "correlation+categorical",
    "source_columns": ["Downloads_Xplore", "AminerCitationCount", "PaperType"],
    "visualization": "scatter plot"
  },
  {
    "question": "Does `Downloads_Xplore` relate to `Award` winning papers and total citations counts?",
    "category": "correlation",
    "source_columns": ["Downloads_Xplore", "Award", "AminerCitationCount", "CitationCount_CrossRef"],
    "visualization": "scatter plot"
  },
  {
    "question": "How does the number of `Citations` vary by `PaperType` category?",
    "category": "ranking",
    "source_columns": ["PaperType", "Citations"],
    "visualization": "bar chart"
  },
  {
    "question": "Which `AuthorKeywords` occur most frequently across the dataset?",
    "category": "textual+frequency",
    "source_columns": ["AuthorKeywords"],
    "visualization": "word cloud"
  },
  {
    "question": "What is the most frequent `Conference` venue in the dataset?",
    "category": "categorical",
    "source_columns": ["Conference"],
    "visualization": "pie chart"
  },
  {
    "question": "What are the top 10 most commonly used `Authors` in the dataset?",
    "category": "categorical",
    "source_columns": ["Authors"],
    "visualization": "word cloud"
  },
  {
    "question": "What patterns emerge in `PaperType` distribution across `Conference` and `Award` status?",
    "category": "categorical+matrix",
    "source_columns": ["PaperType", "Conference", "Award"],
    "visualization": "heatmap"
  },
  {
    "question": "How do average `Downloads_Xplore` values vary across `Conference` venues and top `AuthorAffiliation` institutions?",
    "category": "categorical+matrix",
    "source_columns": ["Conference", "AuthorAffiliation", "Downloads_Xplore"],
    "visualization": "heatmap"
   }
]
```

## Output Format
Return ONLY the JSON array.

## Final Checklist

**Format**  
- [ ] JSON array only, no prose  
- [ ] Keys: `question`, `category`, `source_columns`, `visualization`  

**Columns**  
- [ ] ≥80% of columns covered  
- [ ] No column >2 uses  
- [ ] Include: Temporal, Categorical, Numeric, Text, Derived  

**Visualizations**  
- [ ] 1 scatter  
- [ ] 1 heatmap  
- [ ] 1 line  
- [ ] 1 box  
- [ ] 1 histogram  
- [ ] 1 stacked bar  
- [ ] 1–2 word clouds  
- [ ] No duplicates beyond limits  

**Analysis Coverage**  
- [ ] Temporal  
- [ ] Correlation  
- [ ] Distribution  
- [ ] Categorical  
- [ ] Composition  
- [ ] Textual  
- [ ] ≥70% multi-column  

**Prohibitions**  
- [ ] No pie charts  
- [ ] No overlapping/confusing distributions  
- [ ] No dual-variable box plots  
- [ ] No bar/ranking charts for frequency (word cloud only)  

**Diversity**  
- [ ] Each visualization unique (except word cloud)  
- [ ] No duplicate `source_columns` sets  
- [ ] No same `category` + overlapping columns  
- [ ] Each question distinct analytically  
