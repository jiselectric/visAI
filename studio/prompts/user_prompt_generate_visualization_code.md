Research Question: "{question}"
Suggested Visualization: {visualization}
Category: {category}

Computed Data: {full_data}

Examples:

Example 1 - Line Chart (Temporal + Categorical):
df = pd.DataFrame(data)
plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x='Year', y='publication_count', hue='Conference', marker='o')
plt.title('Publications Over Time by Conference')
plt.xlabel('Year')
plt.ylabel('Number of Publications')
plt.legend(title='Conference')
plt.tight_layout()

Example 2 - Bar Chart (Categorical):
df = pd.DataFrame(data)
plt.figure(figsize=(12, 8))
sns.barplot(data=df, x='Conference', y='count', hue='PaperType')
plt.title('Distribution of Paper Types by Conference')
plt.xlabel('Conference')
plt.ylabel('Count')
plt.legend(title='Paper Type')
plt.xticks(rotation=45)
plt.tight_layout()

Example 3 - Scatter Plot (Correlation):
df = pd.DataFrame(data)
plt.figure(figsize=(10, 8))
sns.scatterplot(data=df, x='Downloads_Xplore', y='AminerCitationCount', alpha=0.7, s=60)
plt.title('Downloads vs Citations Correlation')
plt.xlabel('Downloads')
plt.ylabel('Citations')
plt.tight_layout()

Example 4 - Horizontal Bar Chart (Ranking):
df = pd.DataFrame(data)
df = df.sort_values('paper_count', ascending=True)
plt.figure(figsize=(12, max(8, len(df) * 0.4)))
sns.barplot(data=df, y=df.columns[0], x=df.columns[1], orient='h')
plt.title(f'Top {len(df)} Items by Count')
plt.xlabel('Count')
plt.ylabel('')
plt.tight_layout()

Example 5 - Box Plot (Distribution):
df = pd.DataFrame(data)
plt.figure(figsize=(10, 8))
sns.boxplot(data=df, x='Conference', y='AminerCitationCount')
plt.title('Citation Distribution by Conference')
plt.xlabel('Conference')
plt.ylabel('Citation Count')
plt.xticks(rotation=45)
plt.tight_layout()

Example 6 - Histogram (Distribution):
df = pd.DataFrame(data)
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='AminerCitationCount', bins=20, kde=True)
plt.title('Distribution of Citation Counts')
plt.xlabel('Citation Count')
plt.ylabel('Frequency')
plt.tight_layout()

Example 7 - Heatmap (Correlation Matrix):
df = pd.DataFrame(data)
pivot_df = df.pivot_table(values='avg_citations', index='Conference', columns='PaperType', fill_value=0)
plt.figure(figsize=(10, 8))
sns.heatmap(pivot_df, annot=True, cmap='viridis', fmt='.1f')
plt.title('Average Citations by Conference and Paper Type')
plt.tight_layout()

Example 8 - Word Cloud (Text Frequency Analysis):
df = pd.DataFrame(data)
from wordcloud import WordCloud
import re

# Sort by frequency
df_sorted = df.sort_values('count', ascending=False).head(50)

# Prepare text data with frequency weighting
text_data = []
for _, row in df_sorted.iterrows():
    text = str(row.iloc[0]).strip()
    count = int(row['count'])
    
    # Clean text
    cleaned_text = re.sub(r'[^a-zA-Z0-9\\s]', ' ', text)
    cleaned_text = re.sub(r'\\s+', ' ', cleaned_text).strip()
    
    # Weight by frequency
    for _ in range(min(count, 20)):
        text_data.append(cleaned_text)

# Create word cloud
full_text = ' '.join(text_data)
plt.figure(figsize=(12, 8))
wordcloud = WordCloud(
    width=1200, height=800, background_color='white',
    colormap='viridis', max_words=50, relative_scaling=0.5,
    min_font_size=12, max_font_size=80
).generate(full_text)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud (Size Represents Frequency)')
plt.tight_layout()

Based on the research question, data structure, and suggested visualization type, generate the most appropriate Python matplotlib/seaborn code. The code should:
- Convert the data list to a pandas DataFrame
- Choose the most suitable chart type for the data and question
- Include proper titles, axis labels, and legends
- Handle data cleaning and formatting as needed
- Use appropriate figure sizes and styling
- DO NOT include plt.savefig() - this is handled automatically

Return ONLY the executable Python code.