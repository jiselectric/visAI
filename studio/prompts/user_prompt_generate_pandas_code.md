Research Question: "{question}"
Parent Question Context: {parent_question}
Visualization Type: {visualization}
Category: {category}
Source Columns: {source_columns}

Sample Data for Source Columns:
{sample_data_result}

Examples:

Example 1:
Question: "How has the number of publications changed over time for each Conference?"
Source Columns: ["Year", "Conference"]
Code:
result = df.groupby(['Year', 'Conference']).size().reset_index(name='publication_count')

Example 2: 
Question: "What is the distribution of PaperType across Conferences?"
Source Columns: ["PaperType", "Conference"]
Code:
result = df.groupby(['Conference', 'PaperType']).size().reset_index(name='count')

Example 3:
Question: "Is there a correlation between Downloads_Xplore and AminerCitationCount?"
Source Columns: ["Downloads_Xplore", "AminerCitationCount"]
Code:
result = df[['Downloads_Xplore', 'AminerCitationCount']].dropna()

Example 4:
Question: "Which Authors have contributed the most papers overall?"
Source Columns: ["Authors"]
Code:
author_counts = df['Authors'].str.split(';').explode().str.strip().value_counts().head(20)
result = author_counts.reset_index()
result.columns = ['Author', 'paper_count']

Example 5:
Question: "How does the distribution of AminerCitationCount differ across Conferences?"
Source Columns: ["AminerCitationCount", "Conference"]
Code:
result = df[['Conference', 'AminerCitationCount']].dropna()

Example 6:
Question: "What is the year-over-year growth rate of publications for each Conference?"
Source Columns: ["Year", "Conference"]
Code:
yearly_counts = df.groupby(['Conference', 'Year']).size().reset_index(name='count')
yearly_counts = yearly_counts.sort_values(['Conference', 'Year'])
yearly_counts['growth_rate'] = yearly_counts.groupby('Conference')['count'].pct_change() * 100
result = yearly_counts.dropna()

Example 7:
Question: "Which Conferences have the highest average citations per paper across different paper types?"
Source Columns: ["Conference", "PaperType", "AminerCitationCount"]
Code:
avg_citations = df.groupby(['Conference', 'PaperType'])['AminerCitationCount'].agg(['mean', 'count']).reset_index()
avg_citations.columns = ['Conference', 'PaperType', 'avg_citations', 'paper_count']
result = avg_citations[avg_citations['paper_count'] >= 5].sort_values('avg_citations', ascending=False)

Example 8:
Question: "How do download patterns correlate with citation counts for papers published in different time periods?"
Source Columns: ["Year", "Downloads_Xplore", "AminerCitationCount"]
Code:
df_clean = df[['Year', 'Downloads_Xplore', 'AminerCitationCount']].dropna()
df_clean['period'] = pd.cut(df_clean['Year'], bins=[2005, 2010, 2015, 2020, 2025], labels=['2006-2010', '2011-2015', '2016-2020', '2021+'])
result = df_clean.groupby('period').agg({
    'Downloads_Xplore': ['mean', 'std'],
    'AminerCitationCount': ['mean', 'std']
}).round(2).reset_index()
result.columns = ['period', 'avg_downloads', 'std_downloads', 'avg_citations', 'std_citations']

Example 9:
Question: "What is the distribution of paper lengths and how does it vary by Conference and PaperType?"
Source Columns: ["FirstPage", "LastPage", "Conference", "PaperType"]
Code:
df_pages = df[['FirstPage', 'LastPage', 'Conference', 'PaperType']].dropna()
df_pages['page_length'] = df_pages['LastPage'] - df_pages['FirstPage'] + 1
df_pages = df_pages[df_pages['page_length'] > 0]  # Filter valid page lengths
result = df_pages.groupby(['Conference', 'PaperType'])['page_length'].agg(['mean', 'median', 'std', 'count']).round(2).reset_index()
result.columns = ['Conference', 'PaperType', 'avg_pages', 'median_pages', 'std_pages', 'paper_count']

Generate pandas code that computes the data needed to answer this research question. The code should:
- Use only the specified source columns
- Handle data cleaning/filtering as needed
- Compute aggregations, groupings, or transformations as required
- Return data suitable for the specified visualization type
- Store the final result in a variable named 'result'

Return ONLY the executable pandas code.