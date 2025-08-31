## Instructions
Generate executable pandas code to compute the data needed to answer the research question. The code should process a pandas DataFrame named `df` based on the specified parameters

## Input Data:
question: {{question}}
visualization: {{visualization}}
category: {{category}}
source_columns: {{source_columns}}
sampled_data: {{sampled_data}}

## Requirements
- Return ONLY the pandas code - no explanations, no markdown delimiters, no extra text
- The code must use ONLY the provided source columns - do not access or create arbitrary columns
- The code must be executable Python pandas code
- Use 'df' as the DataFrame variable name
- The final result should be stored in a variable that can be converted to records format
- Handle missing/null values appropriately

## Restrictions
- Use only the specified columns from the Source Columns list.
- The final output should be stored in a variable named result.
- The code must be executable pandas code.
- Handle data cleaning, filtering, and transformations as needed to prepare the data for the specified visualization.

## Examples
### Example 1: Publications Over Time
- Question: How has the number of publications changed over time for each Conference?
- Source: ["Year", "Conference"]
- Pandas Code: `result = df.groupby(['Year', 'Conference']).size().reset_index(name='publication_count')`

### Example 2: Paper Type Distribution Across Conferences
- Question: What is the distribution of PaperType across Conferences?
- Source: ["PaperType", "Conference"]
- Pandas Code: `result = df.groupby(['Conference', 'PaperType']).size().reset_index(name='count')`

### Example 3: Downloads vs Citations Correlation
- Question: Is there a correlation between Downloads_Xplore and AminerCitationCount?
- Source: ["Downloads_Xplore", "AminerCitationCount"]
- Pandas Code: `result = df[['Downloads_Xplore', 'AminerCitationCount']].dropna()`

### Example 4: Top Contributing Authors
- Question: Which Authors have contributed the most papers overall?
- Source: ["Authors"]
- Pandas Code: `author_counts = df['Authors'].str.split(';').explode().str.strip().value_counts().head(20); result = author_counts.reset_index(); result.columns = ['Author', 'paper_count']`

### Example 5: Citation Distribution by Conference
- Question: How does the distribution of AminerCitationCount differ across Conferences?
- Source: ["AminerCitationCount", "Conference"]
- Pandas Code: `result = df[['Conference', 'AminerCitationCount']].dropna()`

### Example 6: Year-over-Year Publication Growth
- Question: What is the year-over-year growth rate of publications for each Conference?
- Source: ["Year", "Conference"]
- Pandas Code: `yearly_counts = df.groupby(['Conference', 'Year']).size().reset_index(name='count'); yearly_counts = yearly_counts.sort_values(['Conference', 'Year']); yearly_counts['growth_rate'] = yearly_counts.groupby('Conference')['count'].pct_change() * 100; result = yearly_counts.dropna()`

### Example 7: Average Citations by Conference and Paper Type
- Question: Which Conferences have the highest average citations per paper across different paper types?
- Source: ["Conference", "PaperType", "AminerCitationCount"]
- Pandas Code: `avg_citations = df.groupby(['Conference', 'PaperType'])['AminerCitationCount'].agg(['mean', 'count']).reset_index(); avg_citations.columns = ['Conference', 'PaperType', 'avg_citations', 'paper_count']; result = avg_citations[avg_citations['paper_count'] >= 5].sort_values('avg_citations', ascending=False)`

### Example 8: Download-Citation Correlation by Time Period
- Question: How do download patterns correlate with citation counts for papers published in different time periods?
- Source: ["Year", "Downloads_Xplore", "AminerCitationCount"]
- Pandas Code: `df_clean = df[['Year', 'Downloads_Xplore', 'AminerCitationCount']].dropna(); df_clean['period'] = pd.cut(df_clean['Year'], bins=[2005, 2010, 2015, 2020, 2025], labels=['2006-2010', '2011-2015', '2016-2020', '2021+']); result = df_clean.groupby('period').agg({'Downloads_Xplore': ['mean', 'std'], 'AminerCitationCount': ['mean', 'std']}).round(2).reset_index(); result.columns = ['period', 'avg_downloads', 'std_downloads', 'avg_citations', 'std_citations']`

### Example 9: Paper Length Distribution by Conference and Type
- Question: What is the distribution of paper lengths and how does it vary by Conference and PaperType?
- Source: ["FirstPage", "LastPage", "Conference", "PaperType"]
- Pandas Code: `df_pages = df[['FirstPage', 'LastPage', 'Conference', 'PaperType']].dropna(); df_pages['page_length'] = df_pages['LastPage'] - df_pages['FirstPage'] + 1; df_pages = df_pages[df_pages['page_length'] > 0]; result = df_pages.groupby(['Conference', 'PaperType'])['page_length'].agg(['mean', 'median', 'std', 'count']).round(2).reset_index(); result.columns = ['Conference', 'PaperType', 'avg_pages', 'median_pages', 'std_pages', 'paper_count']`

## Output Format
Return **ONLY** the executable pandas code as a single code block.

## Final Checklist
- [ ] **ONLY** the executable pandas code as a single code block
- [ ] Use **`df`** as the DataFrame variable name
- [ ] The final result should be stored in a variable that can be converted to records format
- [ ] Handle missing/null values appropriately
- [ ] Use only the specified columns from the Source Columns list
- [ ] The code must be executable pandas code