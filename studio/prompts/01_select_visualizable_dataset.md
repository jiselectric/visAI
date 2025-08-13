## 📊 Available Dataset Summary

The dataset summary contains the following information for each column:
- **column_name**: Name of the column
- **examples**: Sample values from the column
- **unique_value_count**: Number of distinct values
- **top_frequencies**: Most common values and their counts

## 🎯 Your Task

Based on the dataset summary provided, you need to **filter and select only the columns that are suitable for meaningful data visualization**.


## IMPORTANT RULES:
1. **AVOID columns with excessive missing data** (>10% missing values)
2. **PREFER columns with clean, complete data** for better insights
3. **Choose appropriate chart types** based on data characteristics
4. **Focus on meaningful relationships** that can tell a story

## Dataset Quality Assessment:
- **Good columns**: High data completeness, meaningful values, appropriate data types
- **Avoid columns**: High missing data, inconsistent formats, or unclear meaning
- **Preferred data types**: Numeric for quantitative analysis, categorical for grouping

## Chart Type Guidelines:
- **Bar charts**: For categorical data with counts/frequencies
- **Line charts**: For time series data (Year, Date columns)
- **Scatter plots**: For relationships between two numeric variables
- **Pie charts**: For proportions of categorical data (use sparingly)
- **Histograms**: For distribution of numeric variables

## 📋 Selection Criteria

### ✅ Columns to INCLUDE if:
- They are **categorical** with low-to-medium unique values (≤ 100), suitable for bar/pie charts
- They are **numerical** with repeated values, allowing histogram/scatter/correlation plots
- They are **ordinal** or **time-based** (e.g., Year)
- They contain **structured text** or **tags** (e.g., AuthorKeywords) useful for aggregation (e.g., word clouds)
- They denote **award categories**, **paper types**, or other clean labels
- They are **semantically meaningful** and relatively clean, as described

### ❌ Columns to EXCLUDE if:
- They are **identifiers** (e.g., DOI, Link, Title) — nearly all values are unique and non-aggregatable
- They are **freeform text** (e.g., Abstract, AuthorAffiliation) unless structured or aggregated
- They are very **sparse**, **inconsistent**, or noted as incomplete/unreliable
- They **duplicate** other cleaner columns (e.g., prefer AuthorNames-Deduped over AuthorNames if advised)

## 🔍 Dataset Summary Analysis

Please analyze the following dataset summary and select the visualizable columns:

```json
{{dataset_summary_json}}
```

## 📝 Output Format

Return a filtered JSON object where each key is a retained column name and each value follows this format:

```json
{
  "Conference": {
    "column_name": "Conference",
    "examples": ["InfoVis", "VAST", "SciVis", "Vis"],
    "unique_value_count": 4,
    "top_frequencies": {
      "InfoVis": 1293,
      "VAST": 1122,
      "SciVis": 798,
      "Vis": 664
    },
    "Data Quality Notes": "Clean categorical data. No observed typos or inconsistencies.",
    "Potential Visualizations": [
      "Bar chart of count per conference",
      "Pie chart of conference distribution",
      "Stacked bar chart with other categorical variables"
    ]
  },
  "Year": {
    "column_name": "Year",
    "examples": [2006, 2010, 2011, 2014],
    "unique_value_count": 30,
    "top_frequencies": {
      "2011": 145,
      "2014": 132,
      "2007": 125,
      "2010": 120
    },
    "Data Quality Notes": "All values are 4-digit years. Some years may have low or no entries.",
    "Potential Visualizations": [
      "Line chart of publications over time",
      "Histogram of year distribution",
      "Time series analysis"
    ]
  }
}
```

## 🎨 Visualization Types to Consider

- **Bar Chart**: For categorical comparisons
- **Line Chart**: For temporal trends
- **Scatter Plot**: For correlation analysis
- **Histogram**: For distribution analysis
- **Box Plot**: For statistical summaries
- **Word Cloud**: For text frequency
- **Heatmap**: For correlation matrices
- **Network Graph**: For relationship analysis
- **Stacked Bar Chart**: For multi-category analysis
- **Area Chart**: For cumulative data

**Choose appropriate Data Quality Notes and Potential Visualizations per column.** Use brief natural language for the notes, and visualization terms that align with best practices in data analysis.

**Return only the final JSON. Do not include commentary, explanations, or markdown formatting.**