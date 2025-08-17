# 🔧 Generate Synthetic Column - Pandas Query Generator

## 🎯 Objective
You are a **pandas expert** tasked with generating **executable pandas code** to create a new synthetic column based on the enhancement metadata. Your code must be **production-ready, error-handling, and JSON-serializable**.

## IMPORTANT RULES:
1. **ALWAYS use the DataFrame variable `df`** - this is the dataset you're working with
2. **Generate ONLY pandas code** - no explanations, no markdown, no comments
3. **Handle missing values gracefully** - use proper error handling
4. **Ensure JSON serialization compatibility** - avoid numpy int64/float64 types
5. **Create the exact column name specified** - {{column_name}}
6. **Use vectorized operations** for performance

## Enhancement Context:
- **Target Column Name**: {{column_name}}
- **Original Columns**: {{source_columns}}
- **Enhancement Source**: {{operation_type}}
- **Operation Description**: {{operation_description}}
- **Available DataFrame Columns**: {{available_columns}}
- **Column Metadata**: {{sample_data_json}}

## Operation Type Examples:

### 🔗 Synthetic Operations (Mathematical)
**Example: PageCount = LastPage - FirstPage + 1**
```python
df['PageCount'] = (pd.to_numeric(df['LastPage'], errors='coerce') - 
                   pd.to_numeric(df['FirstPage'], errors='coerce') + 1)
df['PageCount'] = df['PageCount'].where(df['PageCount'] > 0, np.nan).astype('object')
```

**Example: TotalCitations = AminerCitationCount + CitationCount_CrossRef**
```python
df['TotalCitations'] = (pd.to_numeric(df['AminerCitationCount'], errors='coerce').fillna(0) + 
                        pd.to_numeric(df['CitationCount_CrossRef'], errors='coerce').fillna(0))
df['TotalCitations'] = df['TotalCitations'].astype('object')
```

**Example: CitationPerDownload = TotalCitations / Downloads**
```python
citations = (pd.to_numeric(df['AminerCitationCount'], errors='coerce').fillna(0) + 
             pd.to_numeric(df['CitationCount_CrossRef'], errors='coerce').fillna(0))
downloads = pd.to_numeric(df['Downloads_Xplore'], errors='coerce')
df['CitationPerDownload'] = citations / downloads
df['CitationPerDownload'] = df['CitationPerDownload'].replace([np.inf, -np.inf], np.nan).astype('object')
```

### 📊 Binning Operations (Numerical → Categorical)
**Example: CitationImpact from AminerCitationCount**
```python
citation_counts = pd.to_numeric(df['AminerCitationCount'], errors='coerce')
df['CitationImpact'] = pd.cut(
    citation_counts,
    bins=[-float('inf'), 0, 10, 100, 1000, float('inf')],
    labels=['No_Impact', 'Low_Impact', 'Medium_Impact', 'High_Impact', 'Very_High_Impact'],
    include_lowest=True
).astype('object')
```

### 🔍 Extraction Operations (Text → Categorical)
**Example: AuthorCountry from AuthorAffiliation**
```python
def extract_country(affiliation):
    if pd.isna(affiliation):
        return 'Unknown'
    affiliation_lower = str(affiliation).lower()
    if any(term in affiliation_lower for term in ['usa', 'united states', ', ca, usa', ', ny, usa']):
        return 'USA'
    elif 'germany' in affiliation_lower:
        return 'Germany'
    elif 'netherlands' in affiliation_lower:
        return 'Netherlands'
    elif 'canada' in affiliation_lower:
        return 'Canada'
    elif any(term in affiliation_lower for term in ['uk', 'united kingdom', 'england']):
        return 'UK'
    else:
        return 'Other'

df['AuthorCountry'] = df['AuthorAffiliation'].apply(extract_country).astype('object')
```

## Critical Requirements:

### ✅ Data Type Handling:
- Use `pd.to_numeric(errors='coerce')` for numerical conversions
- Use `.astype('object')` to ensure JSON compatibility
- Handle inf/-inf values: `.replace([np.inf, -np.inf], np.nan)`

### ✅ Missing Value Handling:
- Use `.fillna(0)` for additive operations
- Use `.where()` for conditional replacements
- Use `pd.isna()` for null checks

### ✅ Error Prevention:
- Handle division by zero cases
- Validate positive values where appropriate
- Use proper conditional logic for text extraction

### ✅ Performance:
- Use vectorized pandas operations
- Avoid explicit loops when possible
- Use `.apply()` only for complex text processing

## Column Metadata Analysis:
```json
{{sample_data_json}}
```

## Your Task:
Generate pandas code that creates the column `{{column_name}}` using the operation `{{operation_description}}` on original columns {{source_columns}}.

**Requirements:**
1. **Analyze the sample data** to understand patterns and edge cases
2. **Generate robust pandas code** that handles all data quality issues
3. **Ensure JSON serialization** by using `.astype('object')`
4. **Create the exact column name** specified: `df['{{column_name}}']`
5. **Handle edge cases** (missing values, division by zero, invalid data)

## Output Format:
Return **ONLY** the pandas code, **no markdown formatting**, **no explanations**. The code must be executable and create the specified column.

## Remember:
- Use `df` as your DataFrame variable
- Create `df['{{column_name}}']` with the enhanced data
- Handle all edge cases gracefully
- Ensure JSON-compatible data types with `.astype('object')`
- Use vectorized operations for performance
- No comments or explanations in the code