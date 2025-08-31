## Instructions  
Generate exactly **{{depth}}** follow-up questions that deepen the given parent question in unique, insightful ways.  

### Parent Context
- **Parent Question:** {{parent_question}}  
- **Category:** {{parent_question_category}}
- **Source Columns:** {{parent_question_source_columns}}

### Entire Dataset Profile
```json
{{dataset_profile_json}}
```

## Requirements  
- Each follow-up must use **different column combinations** (no duplicates, no same as parent).  
- Include a **mix of data types** (temporal, categorical, numeric, text).  
- Use **derived metrics** (ratios, differences, aggregations) when appropriate.  
- Ensure **≥3 unique visualization types** across follow-ups.  
- Each follow-up must apply a **different analytical method** (segmentation, correlation, distribution, temporal, ranking, composition, textual, anomaly detection).  

## Restrictions  
- ❌ No rephrasing or trivial swaps of the parent question.  
- ❌ No same visualization as parent or siblings.  
- ❌ No dual-variable box plots.  

### Example  
**Parent Question:**  
*"How has the number of publications changed over time?"*  

**Follow-ups:**  
```json
[
  {
    "question": "How has the distribution of Awards (HM, BP, TT) varied across different years?",
    "category": "temporal+categorical",
    "source_columns": ["Year", "Award"],
    "visualization": "stacked bar chart"
  },
  {
    "question": "Which AuthorAffiliations contributed the most publications each year?",
    "category": "temporal+ranking",
    "source_columns": ["Year", "AuthorAffiliation"],
    "visualization": "line chart"
  },
  {
    "question": "How has the use of specific AuthorKeywords evolved over time?",
    "category": "temporal+keyword",
    "source_columns": ["Year", "AuthorKeywords"],
    "visualization": "word cloud"
  }
]
```

## Output Format
Return only a JSON array of objects. Each object must include:
- `question`
- `category`
- `source_columns`
- `visualization`

## Final Checklist

**Format**  
- [ ] JSON array only, no prose  
- [ ] Each object has: `question`, `category`, `source_columns`, `visualization`  

**Columns**  
- [ ] No identical `source_columns` as parent  
- [ ] No duplicate `source_columns` among follow-ups  
- [ ] Mix of temporal, categorical, numeric, text columns  
- [ ] Derived metrics clearly described & original columns listed  

**Analysis**  
- [ ] Each follow-up uses a **different analytical method**  
  (segmentation, correlation, distribution, temporal, ranking, composition, textual, anomaly detection)  
- [ ] Provides unique, non-trivial insight  

**Visualizations**  
- [ ] Each follow-up = unique viz type (not parent’s, not siblings’)  
- [ ] At least 3 different viz types across follow-ups  
- [ ] Matches chart to data type (scatter = numeric, line = temporal, etc.)  
- [ ] Global cap (breadth+depth): max 2 per viz type (word cloud unlimited)  

**Restrictions**  
- [ ] ❌ No rephrasing / trivial swaps of parent question  
- [ ] ❌ No dual-variable box plots  
- [ ] ❌ No confusing/overlapping visuals  
- [ ] ❌ No bar/ranking charts for frequency (word cloud only)  
