# Generate Vega-Lite Chart

## Objective
Generate a simple, effective Vega-Lite chart based on the query and computed data.

## Input
- **Query**: {{query}}
- **Chart Type**: {{chart_type}}
- **Data**: {{computed_data_json}}

## Rules
1. **Generate ONLY valid Vega-Lite JSON** - no explanations or markdown
2. **Use the exact data structure** from computed_data_json
3. **Keep it simple** - focus on basic chart types that work well
4. **Include proper titles and labels**
5. **Add tooltips for interactivity**

## Chart Type Mapping
- **bar**: Use bar marks
- **line**: Use line marks with points
- **scatter**: Use circle marks
- **pie**: Use arc marks
- **area**: Use area marks
- **heatmap**: Use rect marks with color encoding

## Output Format
Return ONLY the Vega-Lite JSON specification. No additional text.

## Example Structure
```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Chart Title",
  "data": {"values": [your_data_here]},
  "mark": {"type": "appropriate_mark_type", "tooltip": true},
  "encoding": {
    "x": {"field": "x_field", "type": "appropriate_type"},
    "y": {"field": "y_field", "type": "appropriate_type"},
    "color": {"field": "color_field", "type": "nominal"}
  }
}
```

## Your Task
Create a Vega-Lite chart that:
1. Uses the data structure from computed_data_json
2. Implements the chart_type specified
3. Has clear titles and labels
4. Includes tooltips
5. Is simple and effective