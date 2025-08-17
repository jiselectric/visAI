# 📊 Select Visualizable Dataset Columns

## 🎯 Objective

You are a **data visualization expert** tasked with selecting only the columns that can produce **meaningful, interpretable, and visually engaging charts** from a dataset. Your goal is to identify columns that work well together to tell compelling data stories.

## 🔍 Step 1: Identify Data Types

First, categorize each column into one of these types:

- **Categorical**: Conference name, product category, award type
- **Numerical**: Sales amount, temperature, citation count, download count  
- **Time/Date**: Year, month, timestamp
- **Text**: Titles, descriptions, keywords
- **Geospatial**: Latitude/longitude, country, city

## ✅ Step 2: Apply Visualization Suitability Rules

### 🟢 GOOD CANDIDATES - Include These:

#### **Categorical Variables with Low Cardinality**
- **Example**: Country, Conference, PaperType
- **Cardinality**: ≤ 15 unique values
- **Charts**: Bar charts, pie charts, stacked bars
- **Why**: Small number of categories for clear, readable visualization

#### **Time Series or Ordinal Data**
- **Example**: Year, Month, Quarter
- **Cardinality**: ≤ 50 unique values
- **Charts**: Line charts, area charts, time series
- **Why**: Natural ordering enables trend analysis

#### **Numerical Variables with Repeated Values**
- **Example**: Citation counts, download counts, page counts
- **Charts**: Histograms, box plots, scatter plots
- **Why**: Quantitative data enables statistical insights

#### **Paired Variables for Relationships**
- **Example**: Sales by Region, Citations by Year, Downloads by Conference
- **Charts**: Grouped/stacked bar charts, heatmaps, correlation plots
- **Why**: Relationships reveal deeper insights than single variables

### 🔴 POOR CANDIDATES - Exclude These:

#### **IDs or Unique Identifiers**
- **Example**: DOI, Link, Title, Abstract
- **Why**: No aggregation value, nearly all values unique
- **Result**: Unreadable charts with thousands of bars/points

#### **High-Cardinality Categoricals**
- **Example**: AuthorKeywords, AuthorNames, AuthorAffiliation
- **Why**: Too many unique values (> 15) create cluttered, unreadable charts
- **Result**: Visual noise instead of insights

#### **Free-Form Text**
- **Example**: Abstract, Description, Comments
- **Why**: Cannot be meaningfully aggregated or compared
- **Result**: No clear visualization pattern

#### **Sparse or Inconsistent Data**
- **Example**: Columns with >20% missing values, mixed formats
- **Why**: Missing data skews interpretation
- **Result**: Misleading or incomplete visualizations

#### **High-Discrete-Value Columns**
- **Example**: Citation counts as individual values (418.0, 407.0, 340.0...)
- **Why**: Too many unique values create visual noise and unreadable charts
- **Result**: Thousands of bars/points that show no meaningful pattern

## 📊 Step 3: Evaluate Data Quality

Only include columns where:

- ✅ **Values are clean and consistent** (no typos, mixed formats)
- ✅ **Missing data won't skew interpretation** (< 10% missing)
- ✅ **Units and formats are standardized** (same data type throughout)
- ✅ **Data makes logical sense** (years are reasonable, counts are positive)

## 🔗 Step 4: Pair Variables for Richer Insights

The best visualizations come from relationships:

- **Numerical vs. Time** → Trends over time
- **Categorical vs. Numerical** → Comparisons across groups  
- **Categorical vs. Categorical** → Heatmaps or stacked bars
- **Multiple numerical** → Correlation analysis

## ⚠️ CRITICAL: Data Structure Requirements

**The data MUST be aggregated/summarized, NOT individual data points:**

✅ **GOOD**: Conference counts, Year trends, PaperType distributions
❌ **BAD**: Individual citation counts (418.0, 407.0, 340.0...), raw data points

**If you see thousands of unique values, the data needs to be aggregated first.**

## 🚨 CRITICAL SELECTION CRITERIA:

### **MUST REJECT if:**
- **Unique value count > 15 for ANY DATA COLUMN** 
- **Columns with individual data points** instead of aggregated summaries
- **Any column that would create > 15 bars/points** in a chart
- **Numerical columns with > 100 unique values** (these need binning/aggregation first)
- **Text columns with high cardinality** (author names, titles, abstracts, keywords)
- > 10% missing data
- Mixed data types or inconsistent formats
- No clear aggregation or comparison value

### **MUST INCLUDE if:**
- **Aggregated numerical data** (e.g., "average citations by conference", NOT individual citation counts)
- **Summary statistics** (counts, averages, medians by category)
- **Clean, consistent data quality**

## 📋 Dataset Summary Analysis

Please analyze the following dataset summary and select ONLY the columns that meet the criteria above:

```json
{{dataset_summary_json}}
```

## 📝 Output Format

Return a filtered JSON object where each key is a retained column name and each value follows this format

⚠️ **IMPORTANT**: The examples below are for **INSPIRATION ONLY**. Analyze the actual dataset provided and create your own unique visualizable dataset based the criteria provided above.

```json
{
  "Conference": {
    "column_name": "Conference",
    "data_type": "Categorical",
    "unique_value_count": 4,
    "examples": ["InfoVis", "VAST", "SciVis", "Vis"],
    "top_frequencies": {
      "InfoVis": 1293,
      "VAST": 1122,
      "SciVis": 798,
      "Vis": 664
    },
    "visualization_suitability": "Excellent - Low cardinality, clean categories",
    "recommended_charts": [
      "Bar chart of papers per conference",
      "Pie chart of conference distribution",
      "Stacked bar with other categorical variables"
    ],
    "data_quality_score": "High - No missing data, consistent values"
  },
  "Year": {
    "column_name": "Year",
    "data_type": "Time/Date",
    "unique_value_count": 30,
    "examples": [1990, 1991, 1992, 1993],
    "top_frequencies": {
      "2011": 145,
      "2014": 132,
      "2007": 125,
      "2010": 120
    },
    "visualization_suitability": "Excellent - Natural time ordering, reasonable range",
    "recommended_charts": [
      "Line chart of publications over time",
      "Area chart of cumulative publications",
      "Time series analysis"
    ],
    "data_quality_score": "High - All values are valid 4-digit years"
  }
}
```

## ⚠️ FINAL CHECKLIST:

Before including any column, verify:
- [ ] **Unique values < 15** for **ANY** data column
- [ ] **Data is aggregated/summarized**, NOT individual data points
- [ ] **Missing data < 10%**
- [ ] **Clean, consistent data types**
- [ ] **Clear visualization potential**
- [ ] **Meaningful insights possible**

**🚨 FINAL WARNING: If a column has > 15 unique values, it will create an unreadable chart. REJECT IT.**

**Remember: Quality over quantity. It's better to have 5 meaningful visualizations than 20 unreadable ones.**

**Return only the final JSON. Do not include commentary, explanations, or markdown formatting.**