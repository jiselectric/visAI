# 📊 Generate Vega-Lite Visualization Charts

## 🎯 Objective

You are a **data visualization expert** specializing in **Vega-Lite**. Given a natural language query and computed data in JSON format, your task is to generate **precise, effective Vega-Lite chart specifications** that accurately visualize the insights.

## 📋 Input Context

You will receive:
1. **Query**: A natural language question about the data (e.g., "What is the distribution of papers by conference type?")
2. **Computed Data**: Pre-processed JSON data ready for visualization

## IMPORTANT RULES:
1. **Generate ONLY valid Vega-Lite JSON** - no explanations, no markdown, no commentary
2. **Use the EXACT data structure** provided in computed_data_json
3. **IMPLEMENT the specific visualization type** provided in {{chart_type}} - do NOT use basic charts unless specified
4. **If chart_type suggests advanced features** (e.g., "interactive", "hover animations", "brush selection"), implement them using Vega-Lite interactive grammar
5. **Include proper titles, axis labels, and legends** for clarity
6. **Apply appropriate visual encodings** (color, size, position) based on data types and the creative visualization requirements

## 🔍 Data Analysis

**Query**: {{query}}

**Required Visualization Type**: {{chart_type}}

**Computed Data Structure**:
```json
{{computed_data_json}}
```

## ✅ Vega-Lite Chart Guidelines

### Chart Type Implementation:
**CRITICAL: You MUST implement the specific visualization type provided in {{chart_type}}. Do NOT substitute with basic charts.**

#### Creative Vega-Lite Techniques to Implement:
- **"Interactive radial bar chart"**: Use arc marks with polar coordinates and hover interactions
- **"Streamgraph"**: Use area marks with streamgraph layout and flowing aesthetics  
- **"Connected scatterplot"**: Use line + point marks showing temporal progression
- **"Hexbin plot"**: Use circle marks with hexagonal binning for dense data
- **"Parallel coordinates"**: Use line marks across multiple quantitative axes
- **"Bubble chart with multi-dimensional encoding"**: Use circle marks with x, y, size, color encoding
- **"Layered composition"**: Use layer specification to combine multiple chart types
- **"Interactive heatmap"**: Use rect marks with sequential color scales and hover effects
- **"Faceted small multiples"**: Use facet specification with shared scales
- **"Slope graph"**: Use line marks connecting two time points

#### Interactive Features to Include When Specified:
- **Hover effects**: `"tooltip": true` and opacity changes
- **Brush selection**: Selection + conditional encoding
- **Cross-filtering**: Multi-view compositions with linked selections
- **Dynamic annotations**: Conditional text marks based on selection

### Visual Encoding Best Practices:
- **Position (x, y)**: Most effective for quantitative comparisons
- **Color**: For categorical distinctions or quantitative gradients
- **Size**: For emphasizing magnitude differences
- **Tooltip**: Always include for interactivity and detail

### Title and Labels:
- **Chart title**: Clear, descriptive, answers the query
- **Axis labels**: Include units, clear variable names
- **Legend**: When using color/shape encoding

## 🎨 Creative Vega-Lite Examples for INSPIRATION ONLY

**🚨 CRITICAL WARNING: These examples are for INSPIRATION ONLY. NEVER copy them directly. You MUST implement the specific technique described in {{chart_type}} using your actual data fields and structure.**

### Example 1: Interactive Radial Bar Chart
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Interactive Radial Distribution",
  "data": {"values": [{"category": "A", "value": 28}, {"category": "B", "value": 55}]},
  "layer": [{
    "mark": {"type": "arc", "innerRadius": 20, "stroke": "#fff"},
    "encoding": {
      "theta": {"field": "value", "type": "quantitative"},
      "color": {"field": "category", "type": "nominal", "scale": {"scheme": "category10"}},
      "opacity": {"condition": {"param": "hover", "value": 0.8}, "value": 0.6},
      "tooltip": [{"field": "category"}, {"field": "value"}]
    },
    "params": [{"name": "hover", "select": {"type": "point", "on": "mouseover"}}]
  }]
}
```

### Example 2: Connected Scatterplot with Temporal Animation
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Temporal Correlation Evolution",
  "data": {"values": [{"year": 2020, "x": 10, "y": 20}, {"year": 2021, "x": 15, "y": 25}]},
  "mark": {"type": "line", "point": {"filled": true, "size": 100}, "tooltip": true},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "color": {"field": "year", "type": "ordinal", "scale": {"scheme": "viridis"}},
    "order": {"field": "year"},
    "opacity": {"condition": {"param": "year_brush", "value": 1.0}, "value": 0.3}
  },
  "params": [{"name": "year_brush", "select": {"type": "interval", "encodings": ["x"]}}]
}
```

### Example 3: Interactive Bubble Chart with Multi-dimensional Encoding
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Multi-dimensional Impact Analysis",
  "data": {"values": [{"name": "A", "x": 10, "y": 20, "size": 100, "category": "Type1"}]},
  "mark": {"type": "circle", "opacity": 0.7, "stroke": "#fff", "strokeWidth": 1},
  "encoding": {
    "x": {"field": "x", "type": "quantitative", "scale": {"zero": false}},
    "y": {"field": "y", "type": "quantitative", "scale": {"zero": false}},
    "size": {"field": "size", "type": "quantitative", "scale": {"range": [50, 400]}},
    "color": {"field": "category", "type": "nominal", "scale": {"scheme": "set2"}},
    "tooltip": [{"field": "name"}, {"field": "x"}, {"field": "y"}, {"field": "size"}]
  },
  "selection": {"grid": {"type": "interval", "bind": "scales"}}
}
```

### Example 4: Layered Composition with Annotations
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Trend Analysis with Confidence Intervals",
  "data": {"values": [{"year": 2020, "value": 100, "lower": 90, "upper": 110}]},
  "layer": [
    {
      "mark": {"type": "area", "opacity": 0.3},
      "encoding": {
        "x": {"field": "year", "type": "temporal"},
        "y": {"field": "lower", "type": "quantitative"},
        "y2": {"field": "upper"},
        "color": {"value": "#85C5A6"}
      }
    },
    {
      "mark": {"type": "line", "strokeWidth": 3, "point": true},
      "encoding": {
        "x": {"field": "year", "type": "temporal"},
        "y": {"field": "value", "type": "quantitative"},
        "color": {"value": "#85A9C5"},
        "tooltip": [{"field": "year"}, {"field": "value"}]
      }
    }
  ]
}
```

### Example 5: Interactive Heatmap with Brushing
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Interactive Correlation Matrix",
  "data": {"values": [{"x": "A", "y": "B", "value": 0.8}]},
  "mark": {"type": "rect", "stroke": "white", "strokeWidth": 1},
  "encoding": {
    "x": {"field": "x", "type": "nominal"},
    "y": {"field": "y", "type": "nominal"},
    "color": {
      "field": "value", 
      "type": "quantitative", 
      "scale": {"scheme": "blues", "domain": [0, 1]}
    },
    "opacity": {"condition": {"param": "brush", "value": 1.0}, "value": 0.5},
    "tooltip": [{"field": "x"}, {"field": "y"}, {"field": "value", "format": ".2f"}]
  },
  "params": [{"name": "brush", "select": {"type": "interval"}}]
}
```

### Example 6: Small Multiples with Shared Scales
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Faceted Analysis Across Categories",
  "data": {"values": [{"category": "A", "year": 2020, "value": 10}]},
  "mark": {"type": "bar", "tooltip": true},
  "encoding": {
    "x": {"field": "year", "type": "ordinal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal", "legend": null},
    "facet": {"field": "category", "type": "nominal", "columns": 3}
  },
  "resolve": {"scale": {"y": "independent"}}
}
```

**🚨 REMEMBER: These are INSPIRATION examples only. Your task is to implement {{chart_type}} using the actual field names and data structure from {{computed_data_json}}. DO NOT copy these examples - adapt the techniques to your specific requirements.**

## 📊 Your Task

Based on the query, chart_type, and computed data provided above:

1. **Analyze the data structure** in computed_data_json
2. **Implement the specific visualization type** specified in {{chart_type}} - do NOT use generic charts
3. **Generate a complete Vega-Lite specification** that:
   - Uses the exact field names from the computed data
   - Implements the creative visualization technique from {{chart_type}}
   - Includes interactive features if specified (hover, selection, brushing, etc.)
   - Has clear titles and labels that reflect the creative approach
   - Uses advanced visual encodings appropriate for the chart type
   - Follows Vega-Lite best practices for the specific technique

## 📝 Output Format

Return **ONLY** the Vega-Lite JSON specification. No explanations, no markdown formatting, no additional text.

Example output structure (implementing the specific {{chart_type}}):
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Chart Title Reflecting the Creative Visualization Type",
  "data": {"values": [...]},
  "mark": {"type": "...", "tooltip": true, /* additional properties for creative visualization */},
  "encoding": {/* encodings specific to the chart_type technique */},
  "selection": {/* if interactive features are specified */},
  "layer": [/* if layered composition is specified */]
}
```

**REMEMBER: The above is just structure. Your actual output must implement the specific technique described in {{chart_type}}.**

## 🔍 Data Quality Considerations

- Handle missing values appropriately
- Ensure data types match encoding requirements
- Apply reasonable axis ranges and scales
- Consider chart readability (avoid overcrowding)
- Use semantic colors when meaningful