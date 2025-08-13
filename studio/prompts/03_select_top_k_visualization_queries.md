# 🤖 Prompt: Select Top-K Visualization Queries for Logical Research Flow

## 🎯 Objective

You are given a **comprehensive set of visualization queries** generated from a dataset summary. Your task is to **select exactly {{K}} queries** and **order them logically** to create a smooth, coherent research paper flow that tells a compelling data story.

**⚠️ ABSOLUTELY CRITICAL: You MUST select queries ONLY from the `visualization_queries` input provided below. Do NOT create new queries or copy from examples. Use ONLY the actual queries that exist in the input data.**

## 📋 Instructions

1. **Analyze all available queries** from the input and select exactly **{{K}} queries** that provide the most comprehensive insights
2. **Order the selected queries logically** to create a smooth narrative flow from introduction to conclusion
3. **Ensure each query is unique** and contributes distinct value to the research story
4. **Avoid redundancy** - each query must explore different aspects or relationships
5. **Create a logical progression** that builds understanding step by step

## 🚨 CRITICAL RULES - STRICT ENFORCEMENT:

### ✅ MUST DO:
1. **Select EXACTLY {{K}} queries** - no more, no less
2. **Each query must be UNIQUE** - no duplicate concepts, relationships, or insights
3. **Follow logical flow**: Start with overview → drill down → relationships → trends → insights → conclusions
4. **Ensure diversity**: Cover different chart types, data dimensions, and analytical approaches
5. **Build narrative**: Each query should naturally lead to the next

### ❌ ABSOLUTELY FORBIDDEN:
1. **Redundant queries** - even if they use different columns, if they ask the same analytical question
2. **Duplicate chart types** for similar analytical purposes
3. **Queries that explore the same relationship** from different angles
4. **Overlapping insights** that would produce similar visualizations
5. **Queries that don't contribute to the overall story flow**

## 🎭 Logical Flow Structure (Follow This Order):

### 1. **Introduction & Overview** (2-3 queries)
- Start with broad, high-level insights about the dataset
- Establish context and basic understanding
- Use simple charts: bar charts, pie charts, basic counts

### 2. **Distribution Analysis** (2-3 queries)
- Explore how data is distributed across key categories
- Identify patterns and concentrations
- Use: histograms, box plots, distribution charts

### 3. **Temporal Trends** (2-3 queries)
- Analyze changes over time
- Identify patterns, cycles, or anomalies
- Use: line charts, area charts, time series

### 4. **Relationship Analysis** (2-3 queries)
- Explore correlations and connections between variables
- Identify meaningful associations
- Use: scatter plots, correlation matrices, grouped charts

### 5. **Advanced Insights & Conclusions** (1-2 queries)
- Synthesize findings into actionable insights
- Identify outliers, anomalies, or special cases
- Use: combination charts, advanced visualizations

## 🔍 Input Analysis

Please analyze the following visualization queries and select the top 10 for logical research flow:

```json
{{visualization_queries}}
```

## 📝 Output Format

Your final output **must be a JSON object** with the following structure:

- **`selected_queries`**: An array of exactly {{K}} query objects, where each object contains:
  - **`order`**: Sequential number (1, 2, 3, ...)
  - **`query`**: The actual query text from the input `visualization_queries`
  - **`chart_type`**: The suggested chart type from the input `visualization_queries`
  - **`source_attribute`**: The attribute key from the input (e.g., "PaperType", "Year & Conference")
  - **`flow_stage`**: The logical flow stage this query belongs to
  - **`rationale`**: Why this query fits in this flow stage
- **`logical_flow`**: A brief explanation of the narrative flow
- **`flow_justification`**: Why this order creates a compelling story

**🚨 CRITICAL: The example below shows ONLY the JSON structure format. DO NOT copy the specific queries, chart types, or content. You MUST select queries ONLY from the actual `visualization_queries` input provided above.**

### Example Output

```json
{
  "selected_queries": [
    {
      "order": 1,
      "query": "EXAMPLE_QUERY_TEXT_FROM_INPUT",
      "chart_type": "EXAMPLE_CHART_TYPE_FROM_INPUT",
      "source_attribute": "EXAMPLE_ATTRIBUTE_FROM_INPUT",
      "flow_stage": "Introduction & Overview",
      "rationale": "EXAMPLE_RATIONALE_BASED_ON_ACTUAL_QUERY"
    },
    {
      "order": 2,
      "query": "EXAMPLE_QUERY_TEXT_FROM_INPUT",
      "chart_type": "EXAMPLE_CHART_TYPE_FROM_INPUT", 
      "source_attribute": "EXAMPLE_ATTRIBUTE_FROM_INPUT",
      "flow_stage": "Introduction & Overview",
      "rationale": "EXAMPLE_RATIONALE_BASED_ON_ACTUAL_QUERY"
    }
  ],
  "logical_flow": "EXAMPLE_FLOW_DESCRIPTION",
  "flow_justification": "EXAMPLE_JUSTIFICATION"
}
```

**⚠️ REMEMBER: Replace all "EXAMPLE_*" placeholders with actual content from your input data. The queries, chart types, and source attributes MUST come from the `visualization_queries` input, not from this example.**

## 🎯 Selection Criteria for Each Query:

1. **Uniqueness**: Must explore a different aspect, relationship, or insight
2. **Progression**: Should naturally follow from previous queries
3. **Insight Value**: Must contribute meaningful information to the story
4. **Visualization Diversity**: Should use different chart types appropriately
5. **Narrative Coherence**: Must fit the logical flow stage

## ⚠️ FINAL CHECKLIST:

Before submitting, verify:
- [ ] Exactly {{K}} queries selected
- [ ] No redundant or duplicate queries
- [ ] Logical progression from simple to complex
- [ ] Each query explores different aspects
- [ ] Output follows exact JSON format
- [ ] No markdown formatting or explanations outside JSON

**Return only the final JSON. Do not include commentary, explanations, or markdown formatting outside the JSON structure.**
