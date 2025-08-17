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

## 📋 Dataset Analysis

Analyze the following dataset summary for binning opportunities:

```json
{{dataset_summary_json}}
```

## 📝 Output Format

⚠️ **IMPORTANT**: The examples below are for **INSPIRATION ONLY**. Analyze the actual dataset provided and create your own unique binning opportunities based the criteria provided above.

```json
[
  {
    "column_name": "AminerCitationCount",
    "current_cardinality": 397,
    "binning_strategy": "impact_levels",
    "proposed_bins": {
      "No_Impact": "0",
      "Low_Impact": "1-10", 
      "Medium_Impact": "11-100",
      "High_Impact": "101-1000",
      "Very_High_Impact": "1000+"
    },
    "bin_count": 5,
    "rationale": "Citation counts are highly skewed with most papers having low citations. Binning reveals impact tiers more clearly than raw counts.",
    "visualization_potential": "High - Bar charts of impact distribution, impact by conference/year",
    "domain_interpretability": "Excellent - Citation impact levels are standard in academic analysis",
    "information_loss": "Minimal - Preserves relative impact while reducing noise",
    "confidence_score": 0.9
  },
  {
    "column_name": "Downloads_Xplore",
    "current_cardinality": 1679,
    "binning_strategy": "popularity_tiers",
    "proposed_bins": {
      "Low_Popularity": "0-1000",
      "Medium_Popularity": "1001-10000", 
      "High_Popularity": "10001+"
    },
    "bin_count": 3,
    "rationale": "Download counts show exponential distribution. Binning into popularity tiers enables comparison of content reach.",
    "visualization_potential": "High - Popularity distribution charts, popularity by content type",
    "domain_interpretability": "Good - Popularity tiers are intuitive for content analysis",
    "information_loss": "Low - Maintains relative popularity ordering",
    "confidence_score": 0.8
  }
]
```

## 🎯 Focus Areas

Prioritize binning opportunities that:
1. **Dramatically reduce cardinality** (>100 unique → <10 categories)
2. **Create domain-meaningful categories** 
3. **Enable new visualization insights**
4. **Maintain interpretability** and actionability
5. **Work well with other categorical columns** for cross-analysis

**Return only the JSON array. No explanatory text.**