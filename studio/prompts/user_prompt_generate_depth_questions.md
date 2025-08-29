Based on the `dataset_profile_json`, generate exactly **{{self.config.depth}}** follow-up questions that deepen the parent question in unique, insightful ways.  

### Parent Context
* **Parent Question:** {{parent_question}}  
* **Category:** {{parent_question_category}}  

### Instructions
1. **Column Diversity Requirements:**
   - **Avoid parent question columns**: Minimize reusing the same columns from the parent question
   - **Explore dataset breadth**: Prioritize unused columns from the dataset profile to ensure comprehensive coverage
   - **Column type balance**: Include different data types (temporal, categorical, numeric, text) across follow-ups
   - **Create derived insights**: Use ratios, differences, or aggregations to create new analytical dimensions

2. **Depth Strategy Requirements:**  
   Each follow-up must extend the parent using diverse analytical approaches:  
   - **Segmentation**: Break down by different categorical variables than used in parent
   - **Normalization**: Create ratios, percentages, or per-unit metrics for comparison
   - **Temporal analysis**: Examine trends, stability, or change patterns over time  
   - **Contextual enrichment**: Add variables not present in the parent question
   - **Ranking/extremes**: Identify top/bottom performers, outliers, or anomalies
   - **Text/network analysis**: Explore text patterns, relationships, or frequency distributions
   - **Cross-validation**: Compare different measurement approaches or data sources

3. **Visualization Diversity Requirements:**  
   - **Minimum 3 different visualization types** across all follow-ups
   - **No parent repetition**: Avoid using the same visualization type as the parent question
   - **CRITICAL GLOBAL LIMIT**: Considering ALL questions in the entire report (breadth + depth), maximum 2 questions per visualization type (EXCEPT `word cloud` which has no limit)
   - **Strategic variety**: Ensure coverage of different chart families:
     * Relationship charts (`scatter plot`, `bubble plot`) - for 2+ numeric variables - MAX 2 total across report
     * Matrix/comparison charts (`heatmap`) - for categorical vs categorical/numeric - MAX 2 total across report
     * Distribution charts (`box plot`, `violin plot`, `histogram`) - for SINGLE variable distribution across categories - MAX 2 each type
     * Composition charts (`stacked area chart`, `stacked bar chart`, `treemap`) - for part-to-whole relationships - MAX 2 each type
     * Text analysis charts (`word cloud`) - for text frequency analysis - UNLIMITED uses
     * Temporal charts (`line chart`, `area chart`) - for time-based trends - MAX 2 each type

   **CRITICAL Chart Quality Rules:**
   - **Box plot restrictions**: Use ONLY for single variable distributions across categories. Never for comparing two related variables like ranges, start/end points, or min/max pairs.
   - **For related variable pairs**: Use scatter plots or create derived metrics (difference, ratio, range) instead of trying to show both variables in a box plot.
      - **Frequency analysis rule**: For ALL follow-up questions about frequency, occurrence, or "top/most" items, ALWAYS use `word cloud` where text size represents frequency:
     * "Most frequent keywords" → `word cloud`
     * "Top/most frequent authors" → `word cloud`
     * "Most frequent affiliations/institutions" → `word cloud`
     * "Which [entity] occurs most/highest" → `word cloud`
     * "Highest occurring [text values]" → `word cloud`
     Never use bar charts, ranking visualizations, or any traditional charts for frequency-based analysis.
   - **Avoid visualization confusion**: Don't create charts where multiple data series overlap confusingly or are hard to distinguish.

4. **Quality Requirements:**  
   - **Distinct insights**: Every follow-up must provide unique analytical value
   - **No duplicate patterns**: Avoid same analytical categories with identical column sets
   - **Clear derivations**: Explain any derived columns in the question text and list originals in `source_columns`
   - **Feasible scope**: Ensure questions can be answered with available data  

## Required Output Format
Your response must be a JSON array. Each object in the array must contain the following keys:
-   `question`: The full text of the follow-up question.
-   `category`: The analytical category (e.g., `temporal`, `ranking`, `distribution`).
-   `source_columns`: A list of the columns needed to answer the question.
-   `visualization`: The most appropriate chart type for the question.

# Example Research Questions and Follow-ups

## Temporal Analysis  
**Parent:**  
"How has the number of publications changed over time?"  

**Follow-ups:**  
- {"question": "How has the distribution of Awards (e.g., HM, BP, TT) varied across different years?", "category": "temporal+categorical", "source_columns": ["Year", "Award"], "visualization": "stacked bar chart"}  
- {"question": "Which AuthorAffiliations contributed the most publications each year?", "category": "temporal+ranking", "source_columns": ["Year", "AuthorAffiliation"], "visualization": "line chart"}  
- {"question": "How has the use of specific AuthorKeywords evolved over time?", "category": "temporal+keyword", "source_columns": ["Year", "AuthorKeywords"], "visualization": "word cloud"}  

---

## Correlation Analysis  
**Parent:**  
"What is the relationship between paper length and publication attributes?"  

**Follow-ups:**  
- {"question": "Is there a correlation between paper length (LastPage - FirstPage) and the number of PubsCited_CrossRef?", "category": "correlation+numeric", "source_columns": ["FirstPage", "LastPage", "PubsCited_CrossRef"], "visualization": "scatter plot"}  
- {"question": "How does the number of InternalReferences relate to PubsCited_CrossRef?", "category": "correlation+numeric", "source_columns": ["InternalReferences", "PubsCited_CrossRef"], "visualization": "scatter plot"}  
- {"question": "Do papers with Awards show a different relationship between FirstPage and LastPage compared to non-award papers?", "category": "correlation+categorical", "source_columns": ["FirstPage", "LastPage", "Award"], "visualization": "scatter plot"}  

---

## Ranking Analysis  
**Parent:**  
"Which entities dominate in publication activity?"  

**Follow-ups:**  
- {"question": "Which AuthorNames-Deduped appear most frequently across the dataset?", "category": "ranking+authors", "source_columns": ["AuthorNames-Deduped"], "visualization": "bar chart"}  
- {"question": "Which AuthorAffiliations produced the highest number of papers per year?", "category": "ranking+institution", "source_columns": ["AuthorAffiliation", "Year"], "visualization": "line chart"}  
- {"question": "Which PaperType has the highest proportion of award-winning papers?", "category": "ranking+categorical", "source_columns": ["PaperType", "Award"], "visualization": "bar chart"}  

---

## Distribution Analysis  
**Parent:**  
"How do publication characteristics vary across categories?"  

**Follow-ups:**  
- {"question": "How does paper length (LastPage - FirstPage) differ across PaperTypes?", "category": "distribution+categorical", "source_columns": ["FirstPage", "LastPage", "PaperType"], "visualization": "box plot"}  
- {"question": "What is the distribution of publication counts across Conferences each year?", "category": "distribution+temporal+categorical", "source_columns": ["Conference", "Year"], "visualization": "heatmap"}  
- {"question": "How does the number of InternalReferences vary across different PaperTypes?", "category": "distribution+categorical", "source_columns": ["InternalReferences", "PaperType"], "visualization": "histogram"}  

---

## Text & Network Analysis  
**Parent:**  
"What are the most frequent text patterns in the dataset?"  

**Follow-ups:**  
- {"question": "Which AuthorKeywords tend to co-occur most frequently?", "category": "keyword+network", "source_columns": ["AuthorKeywords"], "visualization": "network graph"}  
- {"question": "How do common AuthorKeywords differ between award-winning and non-award-winning papers?", "category": "keyword+categorical", "source_columns": ["AuthorKeywords", "Award"], "visualization": "word cloud"}  
- {"question": "Which AuthorAffiliations most frequently collaborate across papers?", "category": "network+institutions", "source_columns": ["AuthorAffiliation"], "visualization": "network graph"}  

---

## Derived Metrics & Advanced Analysis  
**Parent:**  
"How can we derive deeper insights from publication metadata?"  

**Follow-ups:**  
- {"question": "What is the average number of pages (LastPage - FirstPage) for each Conference?", "category": "derived+length", "source_columns": ["FirstPage", "LastPage", "Conference"], "visualization": "bar chart"}  
- {"question": "Which AuthorAffiliations produce papers with the highest average number of InternalReferences?", "category": "derived+institution", "source_columns": ["InternalReferences", "AuthorAffiliation"], "visualization": "bar chart"}  
- {"question": "What is the trend of citation counts from CrossRef (CitationCount_CrossRef) compared to the number of publications each year?", "category": "derived+temporal", "source_columns": ["CitationCount_CrossRef", "Year"], "visualization": "line chart"}  

## Dataset Profile:
`{{dataset_profile_json}}`

***

**Final Note:** Return the JSON array **only**, with no additional prose or explanation.