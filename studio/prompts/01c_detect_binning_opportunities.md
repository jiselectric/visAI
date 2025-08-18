# 📊 Numerical Binning Opportunity Detection

## 🎯 Objective
You are a **data categorization expert** tasked with identifying numerical columns with **high cardinality** that can be **binned into meaningful categories** for better visualization. Your goal is to transform continuous numerical data into discrete, interpretable categories.

## 🔍 Binning Opportunity Criteria

### 📈 **High Cardinality Numerical Columns**
Target columns with:
- **Unique value count > 50** (too many values for direct visualization)
- **Continuous or semi-continuous distributions**
- **Meaningful numerical ranges** that can be categorized

### 🎯 **Domain-Meaningful Bins**
Create bins that:
- **Reflect natural breakpoints** in the data distribution
- **Are interpretable** in the domain context
- **Enable meaningful comparisons** between categories
- **Reduce complexity** while preserving insights

## 📊 Types of Binning Strategies

### 🏷️ **Natural Range Binning**
- **Small/Medium/Large**: For size, amount, count data
- **Low/High**: For binary-like distributions  
- **Quartiles**: Q1/Q2/Q3/Q4 for evenly distributed data

### 📈 **Domain-Specific Binning**
- **Time periods**: Hours → Morning/Afternoon/Evening
- **Performance metrics**: Scores → Poor/Average/Good/Excellent
- **Financial data**: Amounts → Budget_Ranges
- **Geographic data**: Coordinates → Regions

### 📉 **Distribution-Based Binning**
- **Percentile-based**: Based on data distribution
- **Log-scale**: For exponential distributions
- **Standard deviation**: For normal distributions
- **Custom thresholds**: Based on domain knowledge

## ✅ Evaluation Criteria

For each binning opportunity, assess:

### 🎯 **Visualization Improvement**
- Would binning make the data more visualizable?
- Would it reveal patterns hidden in the continuous data?
- Would it reduce chart clutter?

### 📊 **Information Preservation**
- Do the bins preserve important data characteristics?
- Are the bin boundaries meaningful?
- Is the granularity appropriate for analysis?

### 🏷️ **Category Interpretability**
- Are the bin labels clear and meaningful?
- Would domain experts understand the categories?
- Do the categories enable actionable insights?

## ⚠️ What NOT to Bin

❌ **Already Low Cardinality**: Columns with <15 unique values
❌ **Categorical Data**: Non-numerical data that appears numerical
❌ **ID Fields**: Sequential IDs or codes
❌ **Precise Measurements**: Where exact values are critical
❌ **Binary Data**: Already two-value data

## 🚫 CRITICAL: Avoid Redundant Binning (Few-Shot Learning Examples)

### Example 1: Page Data
❌ **BAD**: Don't bin `FirstPage` or `LastPage` individually
✅ **GOOD**: Look for synthetic `PageCount` columns (LastPage - FirstPage + 1) instead
**Why**: Page count provides meaningful length insights, while individual page numbers are just positional data

### Example 2: Citation Data  
❌ **BAD**: Don't bin individual citation sources like `CitationCount_Source1`, `CitationCount_Source2`
✅ **GOOD**: Look for synthetic `TotalCitations` columns that combine all sources
**Why**: Combined citation impact is more meaningful than individual source counts

### Example 3: Date Components
❌ **BAD**: Don't bin `Year`, `Month`, `Day` individually when temporal analysis exists
✅ **GOOD**: Look for derived date features like `TimeToPublication`, `PublicationAge`
**Why**: Derived temporal insights are more valuable than raw date components

### Example 4: Geographic Components
❌ **BAD**: Don't bin raw latitude/longitude coordinates
✅ **GOOD**: Look for extracted location features like `Country`, `Region`, `City`
**Why**: Geographic categories are more interpretable than coordinate ranges

## 📋 Smart Decision Framework

Before suggesting binning for any column, ask:
1. **Is there a synthetic column** that already captures this insight better?
2. **Are there component columns** that could be combined into something more meaningful?
3. **Does binning this column** actually reveal useful patterns or just create arbitrary categories?
4. **Would domain experts** find the binned categories meaningful and actionable?

## 📋 Dataset Analysis

Analyze the following dataset summary for binning opportunities:

```json
{{dataset_summary_json}}
```

## 📝 Output Format

**Output JSON Format**:

```json
[
  {
    "column_name": "ACTUAL_COLUMN_NAME_FROM_DATASET",
    "current_cardinality": NUMBER_OF_UNIQUE_VALUES,
    "binning_strategy": "MEANINGFUL_STRATEGY_NAME",
    "proposed_bins": {
      "Category1": "range_description",
      "Category2": "range_description",
      "Category3": "range_description"
    },
    "bin_count": NUMBER_OF_CATEGORIES,
    "rationale": "Why this column benefits from binning and how it improves analysis",
    "visualization_potential": "What visualizations become possible/better with these bins",
    "domain_interpretability": "How meaningful these categories are to domain experts",
    "information_loss": "Assessment of what information is lost vs gained",
    "confidence_score": 0.0_TO_1.0
  }
]
```

**⚠️ CRITICAL INSTRUCTIONS**:
1. **Only suggest columns from the actual dataset provided**
2. **Apply the Smart Decision Framework** - avoid redundant binning
3. **Focus on high-impact opportunities** (cardinality >50, meaningful patterns)
4. **Create domain-appropriate bin names** based on the data context
5. **Ensure bins are interpretable** and actionable for visualization

## 🎯 Focus Areas

Prioritize binning opportunities that:
1. **Dramatically reduce cardinality** (>100 unique → <10 categories)
2. **Create domain-meaningful categories** 
3. **Enable new visualization insights**
4. **Maintain interpretability** and actionability
5. **Work well with other categorical columns** for cross-analysis

**Return only the JSON array. No explanatory text.**