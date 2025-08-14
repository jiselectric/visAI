# 🤖 Prompt: Generate Visualization Queries from Dataset Summary

## 🎯 Objective

You are given a **summary of a structured dataset**. Your task is to generate **natural language queries** that can help guide a second LLM to produce meaningful **visualizations** and insights from the dataset.

## 📋 Instructions

1. For **each column** in the dataset summary, generate **5 distinct queries** related to that attribute.
2. Additionally, generate at least **10 synthetic queries** that combine **two or more columns** (e.g., `"Year & PaperType"` or `"Award & Conference"`). These should uncover **relationships or comparisons across columns**.
3. For each query, include a **suggested chart type** (e.g., bar chart, pie chart, line chart, box plot, word cloud).
4. Make queries **concrete**, measurable, and based only on the data summary provided. Avoid vague, subjective, or open-ended questions.
5. Use **natural language** for the queries.

## IMPORTANT RULES:
1. **AVOID columns with excessive missing data** (>20% missing values)
2. **Focus on columns with clean, complete data**
3. **Generate queries that lead to meaningful insights**
4. **Consider data quality** when selecting columns to analyze

## CRITICAL REQUIREMENTS FOR INSIGHTFUL QUERIES:

### ✅ DO generate queries that reveal:
- **Statistical insights** (e.g., "What is the distribution of citation counts across quartiles?")
- **Trends over time** (e.g., "How has publication count changed over the years?")
- **Comparative analysis** (e.g., "Which journals have the highest median citation counts vs. outliers?")
- **Correlations and relationships** (e.g., "Is there a relationship between paper type and citation success?")
- **Aggregated insights with context** (e.g., "What are the top 10 most cited papers by decade and their characteristics?")
- **Performance metrics** (e.g., "Which conferences show the most consistent quality over time?")
- **Anomaly detection** (e.g., "Which years show unusual publication patterns?")

### ❌ DO NOT generate queries that result in:
- Raw data dumps (e.g., "Show me all download counts")
- Singular value counts (e.g., "Count every unique value")
- Unfiltered listings (e.g., "List all paper titles")
- Meaningless aggregations (e.g., "Count each individual value")
- Simple counts without insight (e.g., "How many papers are there per year?")

## Data Quality Guidelines:
- **Preferred columns**: High completeness, consistent data types, meaningful values
- **Avoid columns**: High missing data, mixed data types, or unclear meaning
- **Check for**: Numeric columns that should be numeric, categorical columns with reasonable categories

## Query Types to Generate:
1. **Distribution analysis**: How are values distributed across categories?
2. **Trend analysis**: How do values change over time?
3. **Relationship analysis**: How do two variables relate to each other?
4. **Comparison analysis**: How do different groups compare?
5. **Ranking analysis**: What are the top/bottom performers?

## 🔍 Dataset Summary Analysis

Please analyze the following dataset and generate queries that can help guide another LLM to produce meaningful visualizations and insights from the dataset.

```json
{{visualizable_dataset_json}}
```

## ✅ Output Format

Your final output **must be a JSON object** with the following structure:

- Each **key** is either a **single column name** (e.g., `"Conference"`) or a **combined key** of multiple columns (e.g., `"Year & PaperType"`) **STRICTLY** from {{attributes}}
- Each **value** is an object `queries` with **exactly 5 key-value pairs**, where:
  - The **key** is a query string.
  - The **value** is the suggested visualization type(s).

### Example Output

```json
{
  "Conference": {
    "queries": {
      "What is the distribution of papers by conference type?": "Bar chart or pie chart",
      "Which conference has the highest number of published papers?": "Bar chart",
      "How many papers were submitted for each conference?": "Bar chart",
      "What proportion of the total publications does each conference contribute?": "Pie chart",
      "Compare the number of papers across different conference types.": "Stacked bar chart"
    }
  },
  "Year & PaperType": {
    "queries": {
      "How has the distribution of paper types changed over the years?": "Stacked area chart",
      "Which type of paper was most commonly submitted each year?": "Line chart or stacked bar chart",
      "Rank the paper types by submission count per year.": "Grouped bar chart",
      "How many journal papers were submitted each year?": "Line chart",
      "Compare yearly trends across all paper types.": "Multi-line chart"
    }
  },
  "Year & PaperType & Citations": {
    "queries": {
      "How has the distribution of citation counts changed over the years?": "Stacked area chart",
      "Which type of paper had the highest median citation count each year?": "Line chart or stacked bar chart",
      "Rank the paper types by median citation count per year.": "Grouped bar chart",
      "How many journal papers had the highest median citation count each year?": "Line chart",
      "Compare yearly trends across all paper types with median citation counts.": "Multi-line chart"
    }
  }
}
