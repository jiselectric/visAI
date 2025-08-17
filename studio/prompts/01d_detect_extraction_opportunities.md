# 🔍 Text Extraction Opportunity Detection

## 🎯 Objective
You are a **text analysis expert** tasked with identifying text columns that contain **hidden categorical information** that can be extracted for visualization. Your goal is to unlock structured data patterns within unstructured text fields.

## 🔍 Types of Extractable Information

### 🌍 **Geographic Information**
Extract location data from addresses, affiliations, descriptions:
- **Countries**: "USA", "Germany", "Japan", "Other"
- **Regions**: "North America", "Europe", "Asia-Pacific", "Other"
- **Cities**: Major cities vs. "Other"
- **Institution Types**: "University", "Industry", "Government", "Non-profit"

### 🏢 **Organizational Information**
Extract organization types and characteristics:
- **Company Size**: "Large Corp", "Medium Business", "Startup", "Individual"
- **Industry Sector**: Technology, Finance, Healthcare, Education, etc.
- **Organization Type**: Academic, Commercial, Government, NGO

### 📊 **Content Classification**
Extract content categories from descriptions, titles, abstracts:
- **Topic Categories**: Based on keywords and themes
- **Content Type**: Research, Tutorial, Case Study, Review, etc.
- **Difficulty Level**: Beginner, Intermediate, Advanced
- **Format Type**: Technical, Business, Academic, Popular

### 🔢 **Embedded Numerical Categories**
Extract numerical patterns as categories:
- **Version Numbers**: v1.x, v2.x, v3.x+
- **Dates/Years**: Extract time periods from text
- **Quantities**: Small/Medium/Large based on embedded numbers
- **Ratings/Scores**: Extract quality indicators

### 🏷️ **Status and Classification Tags**
Extract status information:
- **Completion Status**: Complete, In Progress, Planned
- **Quality Indicators**: Premium, Standard, Basic
- **Priority Levels**: High, Medium, Low
- **Approval Status**: Approved, Pending, Rejected

## ✅ Evaluation Criteria

For each extraction opportunity, assess:

### 🎯 **Extraction Viability**
- Can patterns be reliably identified in the text?
- Would extraction yield consistent categories?
- Is the text quality sufficient for reliable parsing?

### 📊 **Visualization Value**
- Would extracted categories enable meaningful visualizations?
- Would they complement existing categorical columns?
- Would they reveal hidden patterns in the data?

### 🏷️ **Category Meaningfulness**
- Are the extracted categories domain-relevant?
- Would they be interpretable to stakeholders?
- Do they enable actionable insights?

### 📈 **Cardinality Appropriateness**
- Would extraction yield 3-15 meaningful categories?
- Would categories have sufficient data points each?
- Would distribution be balanced enough for visualization?

## ⚠️ What NOT to Extract

❌ **Highly Variable Text**: Free-form prose with no patterns
❌ **Personal Information**: Names, personal details, private data
❌ **Too Many Categories**: Extraction yielding >20 categories
❌ **Inconsistent Patterns**: Text with high variability and low structure
❌ **Short Text Fields**: Insufficient content for meaningful extraction

## 📋 Dataset Analysis

Analyze the following dataset summary for text extraction opportunities:

```json
{{dataset_summary_json}}
```

## 📝 Output Format

⚠️ **IMPORTANT**: The examples below are for **INSPIRATION ONLY**. Analyze the actual dataset provided and create your own unique extraction opportunities based the criteria provided above.

```json
[
  {
    "column_name": "AuthorAffiliation",
    "extraction_type": "geographic_and_institutional",
    "extractable_categories": {
      "Country": ["USA", "Germany", "Netherlands", "Canada", "Other"],
      "Institution_Type": ["University", "Industry", "Research_Lab", "Government"],
      "Geographic_Region": ["North_America", "Europe", "Asia", "Other"]
    },
    "extraction_method": "pattern_matching_and_keyword_analysis",
    "sample_extractions": {
      "Computer Science Department, Stanford University, Stanford, CA, USA": {
        "Country": "USA",
        "Institution_Type": "University", 
        "Geographic_Region": "North_America"
      },
      "IBM Thomas J. Watson Research Center, Yorktown Heights, NY, USA": {
        "Country": "USA",
        "Institution_Type": "Industry",
        "Geographic_Region": "North_America"
      }
    },
    "rationale": "Affiliation text contains structured geographic and institutional information that can be reliably extracted into meaningful categories",
    "expected_coverage": "85-90% of entries can be successfully categorized",
    "visualization_potential": "High - Geographic distribution maps, institution type analysis, regional collaboration patterns",
    "data_quality_impact": "Good - Pattern-based extraction with fallback to 'Other' category",
    "confidence_score": 0.8
  },
  {
    "column_name": "AuthorKeywords",
    "extraction_type": "topic_classification",
    "extractable_categories": {
      "Research_Area": ["Visualization", "Machine_Learning", "Data_Mining", "User_Interface", "Other"],
      "Method_Type": ["Quantitative", "Qualitative", "Mixed_Methods", "Theoretical"],
      "Application_Domain": ["Healthcare", "Finance", "Education", "General"]
    },
    "extraction_method": "keyword_clustering_and_domain_classification",
    "sample_extractions": {
      "Information visualization, user interfaces, toolkits, 2D graphics": {
        "Research_Area": "Visualization",
        "Method_Type": "Quantitative",
        "Application_Domain": "General"
      }
    },
    "rationale": "Keywords contain structured research classification information that can group papers by research themes",
    "expected_coverage": "70-80% of entries have sufficient keywords for classification",
    "visualization_potential": "Medium-High - Research area trends, methodology distributions, domain focus analysis",
    "data_quality_impact": "Fair - Some entries lack keywords, requiring handling of missing data",
    "confidence_score": 0.7
  }
]
```

## 🎯 Focus Areas

Prioritize extraction opportunities that:
1. **Have clear, identifiable patterns** in the text
2. **Yield interpretable categories** (3-15 categories)
3. **Complement existing data** for cross-analysis
4. **Enable geographic, temporal, or thematic analysis**
5. **Work reliably across most of the dataset** (>70% coverage)

**Return only the JSON array. No explanatory text.**