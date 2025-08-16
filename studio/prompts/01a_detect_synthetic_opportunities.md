# 🔗 Synthetic Column Opportunity Detection

## 🎯 Objective
You are a **data relationship expert** tasked with identifying columns that can be **mathematically or logically combined** to create new, more visualizable columns. Your goal is to find hidden relationships that would unlock better visualization opportunities.

## 🔍 Types of Synthetic Opportunities to Detect

### 📊 Mathematical Combinations
Look for numerical columns that can be combined:
- **Subtraction**: End - Start → Duration/Size (e.g., EndDate - StartDate → Duration)
- **Addition**: Part1 + Part2 → Total (e.g., Sales_Q1 + Sales_Q2 → Sales_H1)
- **Division**: Value1 / Value2 → Ratio (e.g., Sales / Population → Per_Capita_Sales)
- **Multiplication**: Rate × Time → Total (e.g., Speed × Time → Distance)

### 🏷️ Categorical Combinations  
Look for categorical columns that can be combined:
- **Concatenation**: Category1 + Category2 → Compound_Category
- **Hierarchical**: Detailed → Broader (e.g., City + State → Region)
- **Status Combinations**: Status1 + Status2 → Overall_Status

### 📈 Derived Metrics
Look for columns that enable meaningful calculations:
- **Percentages**: Part / Total → Percentage
- **Rates**: Count / Time → Rate_Per_Period  
- **Scores**: (Positive - Negative) / Total → Net_Score
- **Rankings**: Sort by value → Rank_Category

## ✅ Evaluation Criteria

For each potential synthetic column, assess:

### 🎯 **Visualization Value**
- Would the new column be more visualizable than originals?
- Would it reduce cardinality while preserving meaning?
- Would it reveal patterns not visible in individual columns?

### 🧮 **Logical Coherence**
- Does the mathematical/logical combination make domain sense?
- Are the units compatible for the operation?
- Would the result be interpretable?

### 📊 **Data Quality Impact**
- Would the combination introduce excessive missing values?
- Would it maintain data distribution characteristics?
- Would outliers be appropriately handled?

## ⚠️ What NOT to Combine

❌ **Incompatible Data Types**: Text + Numbers (unless extracting numbers from text)
❌ **Unrelated Concepts**: Temperature + User_ID (no logical relationship)
❌ **High Missing Values**: Combinations that would lose >20% of data
❌ **ID Fields**: Unique identifiers rarely combine meaningfully

## 📋 Dataset Analysis

Analyze the following dataset summary for synthetic opportunities:

```json
{{dataset_summary_json}}
```

## 📝 Output Format

Return a JSON array of synthetic opportunities. For each opportunity:

```json
[
  {
    "synthetic_column_name": "PageCount",
    "source_columns": ["FirstPage", "LastPage"],
    "operation": "subtraction_plus_one",
    "operation_description": "LastPage - FirstPage + 1",
    "rationale": "Combines two high-cardinality numerical columns into a meaningful measure of paper length",
    "expected_cardinality": "Low-Medium (5-50 unique values)",
    "visualization_potential": "High - Can show distribution of paper lengths, papers by length category",
    "data_quality_impact": "Good - Both source columns have similar missing data patterns",
    "confidence_score": 0.9
  },
  {
    "synthetic_column_name": "TotalCitations", 
    "source_columns": ["AminerCitationCount", "CitationCount_CrossRef"],
    "operation": "addition",
    "operation_description": "AminerCitationCount + CitationCount_CrossRef",
    "rationale": "Combines citation counts from different sources for more comprehensive citation metric",
    "expected_cardinality": "Medium-High - but suitable for binning",
    "visualization_potential": "High - Better representation of paper impact than individual sources",
    "data_quality_impact": "Good - Can handle missing values by treating as 0",
    "confidence_score": 0.8
  }
]
```

## 🎯 Focus Areas

Prioritize opportunities that:
1. **Significantly reduce cardinality** while preserving meaning
2. **Create interpretable business/domain metrics**  
3. **Enable new visualization types** not possible with original columns
4. **Maintain or improve data quality**

**Return only the JSON array. No explanatory text.**