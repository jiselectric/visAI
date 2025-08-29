Based on the `dataset_profile_json`, generate exactly **{{self.config.breadth}}** diverse, high-quality research questions.  

### Instructions
1. **Output:** JSON array of objects with keys `question`, `category`, `source_columns`, and `visualization`.  

2. **MANDATORY Column Distribution Requirements:**
   - **Column Usage Limit**: No column may appear in more than 3 questions total
   - **Column Coverage**: Must use at least 80% of available columns from dataset profile
   - **Priority Columns**: Analyze the dataset profile to identify underutilized columns and ensure they are included:
     * Text columns beyond the most obvious ones (explore institutional, author, or content analysis)
     * Numeric columns that might be overlooked in favor of primary metrics
     * Categorical columns that provide segmentation opportunities
     * Derived metrics from existing columns (ratios, differences, aggregations)
   - **Column Type Balance**: Ensure representation across temporal, categorical, numeric, and text column types

3. **MANDATORY Visualization Diversity Requirements:**
   - **Minimum 6 different visualization types** across all questions
   - **CRITICAL LIMIT**: Maximum 2 questions per visualization type (EXCEPT `word cloud` which has no limit)
   - **Required types**: Must include at least one of each:
     * `scatter plot` (for numeric relationships between 2 variables) - MAX 2 uses
     * `heatmap` (for categorical/numeric matrix) - MAX 2 uses
     * `box plot` or `violin plot` (for distribution of ONE variable across categories) - MAX 2 uses total
     * `word cloud` (for text frequency analysis) - UNLIMITED uses
     * `stacked bar chart` or `stacked area chart` (for compositions) - MAX 2 uses total
     * `line chart` or `area chart` (for temporal trends) - MAX 2 uses total
     * `bubble plot` (for multi-dimensional analysis) - MAX 2 uses
     * `treemap` (for hierarchical data) - MAX 2 uses
     * `histogram` (for distribution analysis) - MAX 2 uses
     * `pie chart` (for proportional data) - MAX 2 uses

   **CRITICAL Visualization Quality Rules:**
   - **Box plot restrictions**: Only use for distribution of a SINGLE variable across categories. Never for comparing two related variables simultaneously.
   - **For related numeric pairs**: Use scatter plots or derive a single metric (e.g., range, ratio, difference) instead of dual-variable box plots.
   - **Frequency analysis rule**: For ALL questions about frequency, occurrence, or "top/most" items, ALWAYS use `word cloud` where text size represents frequency:
     * "Most frequent keywords" → `word cloud`
     * "Top authors" → `word cloud`
     * "Most frequent affiliations" → `word cloud`
     * "Which [entity] occurs most" → `word cloud`
     * "Highest occurring [text]" → `word cloud`
     Never use bar charts, ranking visualizations, or traditional charts for any frequency-based analysis.
   - **Avoid confusing overlaps**: Don't create charts with overlapping or hard-to-distinguish data series.
   - **Prefer derived metrics**: For related variables, create meaningful derived columns rather than plotting multiple raw variables together.

4. **Analysis Complexity Requirements:**
   - **Multi-column priority**: At least 70% of questions must use multiple columns
   - **Category balance**: Include temporal, correlation, distribution, ranking, categorical, keyword, composition, and network analysis
   - **Avoid repetitive patterns**: Limit similar column combinations to maintain diversity

5. **Creativity:** Questions must seek **insightful and compelling patterns**, not trivial counts. Aim for comparisons, trends, anomalies, relationships, and institutional/authorship analysis.  

### Example Output
```json
[
  {
    "question": "How has the proportion of different `PaperType` categories shifted across `Conference` venues over time?",
    "category": "composition+temporal",
    "source_columns": ["Year", "Conference", "PaperType"],
    "visualization": "stacked area chart"
  },
  {
    "question": "What is the relationship between paper length (derived from `LastPage` - `FirstPage`) and `AminerCitationCount`?",
    "category": "correlation",
    "source_columns": ["FirstPage", "LastPage", "AminerCitationCount"],
    "visualization": "scatter plot"
  }
]
```

### Dataset Profile:
{{dataset_profile_json}}

### Final Note: Return the JSON array only, with no additional prose or explanation.