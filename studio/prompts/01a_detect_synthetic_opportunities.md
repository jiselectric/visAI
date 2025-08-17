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

⚠️ **IMPORTANT**: The examples below are for **INSPIRATION ONLY**. Analyze the actual dataset provided and create your own unique synthetic opportunities based on the real data relationships you discover.

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
   },
   {
     "synthetic_column_name": "TotalCitationScore", 
     "source_columns": ["AminerCitationCount", "CitationCount_CrossRef", "PubsCited_CrossRef"],
     "operation": "addition",
     "operation_description": "AminerCitationCount + CitationCount_CrossRef + PubsCited_CrossRef",
     "rationale": "Combines citation counts from multiple sources for comprehensive citation impact measure",
     "expected_cardinality": "Medium-High - but suitable for binning into impact categories",
     "visualization_potential": "High - Can show comprehensive citation impact distributions and identify highly cited papers",
     "data_quality_impact": "Good - Can handle missing values by treating as 0",
     "confidence_score": 0.8
   },
   {
     "synthetic_column_name": "CitationPerDownload", 
     "source_columns": ["AminerCitationCount", "CitationCount_CrossRef", "PubsCited_CrossRef", "Downloads_Xplore"],
     "operation": "ratio_calculation",
     "operation_description": "(AminerCitationCount + CitationCount_CrossRef + PubsCited_CrossRef) / Downloads_Xplore",
     "rationale": "Measures citation efficiency - how many citations a paper receives per download, indicating research impact relative to accessibility",
     "expected_cardinality": "High - continuous ratio values suitable for binning into efficiency categories",
     "visualization_potential": "High - Can show impact efficiency distributions, identify high-performing papers after binning into Low/Medium/High efficiency categories",
     "data_quality_impact": "Good - Handles division by zero cases (Downloads_Xplore = 0) by setting to null or infinity",
     "confidence_score": 0.8
   },
]
```

## 🎯 Focus Areas

Prioritize opportunities that:
1. **Significantly reduce cardinality** while preserving meaning
2. **Create interpretable business/domain metrics**  
3. **Enable new visualization types** not possible with original columns
4. **Maintain or improve data quality**

**Return only the JSON array. No explanatory text.**