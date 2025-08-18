## IMPORTANT RULES:
1. **ALWAYS use the DataFrame variable `df`** - this is the dataset you're working with
2. **ALWAYS assign your result to a variable called `result`** - this is how we capture your output
3. **Generate ONLY pandas code** - no explanations, no markdown, no plotting code
4. **Focus on data computation and aggregation** - not visualization
5. **Use proper pandas syntax** - avoid deprecated methods

## Dataset Context:
- You have a DataFrame called `df`
- The dataset has columns: {{attributes}}
- Total rows in dataset: {{num_rows}}
- Focus on the specific columns mentioned in the query
- The query is: {{query}}
- The chart type is: {{chart_type}}
- The sample data of column(s) to compute is: {{attributes_samples_json}}

## CRITICAL OUTPUT FORMAT REQUIREMENTS:

**Your pandas code MUST produce a `result` DataFrame with this EXACT structure:**
- **Column names** that match the original dataset columns being analyzed
- **Descriptive column names** for computed values (e.g., 'publication_count', 'citation_count', 'download_count')
- **Proper data types** (numeric for counts, dates for time series, etc.)
- **Sorted data** when appropriate (chronological for time series, descending for rankings)

## Few-Shot Examples Based on Similar Queries:

### Example 1: Time series analysis (Publications over time)
**Query:** "How has the number of publications changed over the years?"
**Columns:** ["Year"]
**Chart Type:** "line"
**Expected Output Structure:**
```json
[
  {"Year": 1990, "publication_count": 53},
  {"Year": 1991, "publication_count": 57},
  {"Year": 1992, "publication_count": 59}
]
```
**Code:**
```python
result = df.groupby('Year').size().reset_index(name='publication_count').sort_values('Year')
```

### Example 2: Distribution analysis (Paper types)
**Query:** "What is the distribution of paper types?"
**Columns:** ["PaperType"]
**Chart Type:** "pie"
**Expected Output Structure:**
```json
[
  {"PaperType": "J", "count": 2847},
  {"PaperType": "C", "count": 1153}
]
```
**Code:**
```python
result = df.groupby('PaperType').size().reset_index(name='count').sort_values('count', ascending=False)
```

### Example 3: Ranking analysis (Top conferences)
**Query:** "Which conferences have the highest number of papers?"
**Columns:** ["Conference"]
**Chart Type:** "bar"
**Expected Output Structure:**
```json
[
  {"Conference": "InfoVis", "paper_count": 1293},
  {"Conference": "VAST", "paper_count": 1122},
  {"Conference": "SciVis", "paper_count": 798}
]
```
**Code:**
```python
result = df.groupby('Conference').size().reset_index(name='paper_count').sort_values('paper_count', ascending=False)
```

### Example 4: Correlation analysis (Citations vs Downloads)
**Query:** "Is there a correlation between citation counts and downloads?"
**Columns:** ["CitationCount_CrossRef", "Downloads_Xplore"]
**Chart Type:** "scatter"
**Expected Output Structure:**
```json
[
  {"CitationCount_CrossRef": 15, "Downloads_Xplore": 234},
  {"CitationCount_CrossRef": 8, "Downloads_Xplore": 156}
]
```
**Code:**
```python
result = df[['CitationCount_CrossRef', 'Downloads_Xplore']].dropna()
```

### Example 5: Multi-dimensional analysis (Paper types by year)
**Query:** "How has the distribution of paper types changed over the years?"
**Columns:** ["Year", "PaperType"]
**Chart Type:** "stacked area"
**Expected Output Structure:**
```json
[
  {"Year": 1990, "PaperType": "J", "count": 45},
  {"Year": 1990, "PaperType": "C", "count": 8},
  {"Year": 1991, "PaperType": "J", "count": 48},
  {"Year": 1991, "PaperType": "C", "count": 9}
]
```
**Code:**
```python
result = df.groupby(['Year', 'PaperType']).size().reset_index(name='count').sort_values(['Year', 'PaperType'])
```

## 🚨 CRITICAL: ANALYZE THE ACTUAL DATA PROVIDED

**YOU MUST:**
1. **Examine the sample data in `{{attributes_samples_json}}` carefully**
2. **Understand the actual column names and data types in your dataset** 
3. **Design your pandas query based on the REAL data structure, NOT the examples**
4. **Match the query intent with the actual available columns**

## Your Task:
Generate pandas code that:
1. Reads the `df` DataFrame
2. **Analyzes the ACTUAL columns provided in `{{attributes_samples_json}}`**
3. **Processes the data according to the query using appropriate pandas operations**
4. **Assigns the final result to a variable called `result`**
5. **Uses descriptive column names for computed values** (e.g., 'publication_count', 'paper_count', 'count')
6. **Sorts data appropriately** (chronological for time series, descending for rankings)

## 🎯 Query Analysis Process:
1. **Read the query**: {{query}}
2. **Identify what analysis is needed**: aggregation, filtering, correlation, etc.
3. **Examine the sample data**: {{attributes_samples_json}}
4. **Match the query intent to appropriate pandas operations**
5. **Generate code that works with the ACTUAL column names and data types**

## Output Format:
Return **ONLY** the pandas code, **no markdown formatting**, **no explanations**. The code must be executable and produce a `result` variable.

## Remember:
- Use `df` as your DataFrame variable
- **Assign final output to `result`**
- **IGNORE the examples if they don't match your actual data structure**
- **Focus on the query intent and actual data provided**
- **Make sure your code handles edge cases** (missing values, data types, etc.)
- **Use appropriate column names from the actual dataset**
- **Use `.reset_index()` and `.sort_values()` appropriately**
