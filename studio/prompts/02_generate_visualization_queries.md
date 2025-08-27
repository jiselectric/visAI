# 🎨 Generate Creative Visualization Queries Inspired by Vega-Lite Gallery

## 🎯 Objective

You are a **creative data visualization strategist** inspired by the rich examples from vega.github.io/vega-lite/examples/. Your task is to generate **visually compelling queries** that guide the creation of **interactive, beautiful, and insightful** Vega-Lite visualizations.

## 🌟 Creative Visualization Mission

1. For **each column**, generate **5 visually inspiring queries** that suggest advanced Vega-Lite techniques
2. Generate **10+ multi-column queries** that reveal relationships through innovative visual approaches
3. **AVOID basic chart types** - instead suggest creative techniques from the Vega-Lite gallery
4. Focus on **interactivity, aesthetics, and multi-dimensional encoding**
5. **Use examples below as INSPIRATION, not templates to copy**

## 🎨 Creative Vega-Lite Techniques (Inspired by vega.github.io/vega-lite/examples/)

### 🌈 Instead of Basic Charts, Suggest These Creative Approaches:

#### **For Categorical Distributions:**
- **"Interactive radial bar chart with hover animations"** (arc marks in polar coordinates)
- **"Layered bar chart with value annotations and gradient fills"** 
- **"Faceted small multiples with brushing and linking"**
- **"Bubble chart with categorical color encoding and size variations"**

#### **For Time Series & Trends:**
- **"Connected scatterplot showing correlation evolution over time"**
- **"Streamgraph with flowing, organic area fills"** 
- **"Multi-layer chart combining line trends with confidence intervals"**
- **"Interactive time series with brush selection and zooming"**

#### **For Correlations & Relationships:**
- **"Bubble chart with 3-4 dimensional encoding (x, y, size, color)"**
- **"Hexbin plot for dense data with aggregated hover details"**
- **"Scatterplot matrix with cross-filtering and highlighting"**
- **"Connected scatterplot showing temporal correlation patterns"**

#### **For Multi-dimensional Analysis:**
- **"Interactive heatmap with sequential color schemes and tooltips"**
- **"Layered composition combining multiple chart types"**
- **"Parallel coordinates plot for high-dimensional exploration"**
- **"Trellis plot (small multiples) with shared scales and brushing"**

#### **For Comparisons & Rankings:**
- **"Slope graph showing changes between two time points"**
- **"Grouped bar chart with interactive legend filtering"**
- **"Box plot with overlaid strip plot for distribution details"**
- **"Waterfall chart showing cumulative effects"**

## 🎯 Advanced Interactive Features to Incorporate:

### **Selection & Filtering:**
- **Brush selection** for zooming and filtering
- **Click selection** for highlighting and cross-filtering  
- **Legend interaction** for showing/hiding categories
- **Interval selection** for range-based filtering

### **Rich Tooltips & Hover Effects:**
- **Multi-field tooltips** with formatted values
- **Opacity changes** on hover for depth
- **Highlight effects** for related data points
- **Dynamic text annotations** showing insights

### **Sophisticated Color & Styling:**
- **Sequential color schemes** (viridis, plasma, blues)
- **Categorical palettes** (category10, set2, tableau10)
- **Gradient fills** and **opacity encoding**
- **Custom styling** with rounded corners and strokes

## CRITICAL RULES:
1. **NEVER suggest basic "bar chart", "pie chart", "line chart"**
2. **ALWAYS include interactive elements** (hover, selection, tooltips)
3. **ENCOURAGE multi-dimensional encoding** (size, color, opacity, shape)
4. **FOCUS on visual appeal AND insight**

## CRITICAL REQUIREMENTS FOR INSIGHTFUL QUERIES:

### ✅ DO generate queries that reveal:
- **Statistical insights** (e.g., "What is the distribution of citation counts across quartiles?")
- **Trends over time** (e.g., "How has publication count changed over the years?")
- **Comparative analysis** (e.g., "Which journals have the highest median citation counts vs. outliers?")
- **Correlations and relationships** (e.g., "Is there a relationship between paper type and citation success?")
- **Aggregated insights with context** (e.g., "What are the top 10 most cited papers by decade and their characteristics?")
- **Performance metrics** (e.g., "Which conferences show the most consistent quality over time?")
- **Anomaly detection** (e.g., "Which years show unusual publication patterns?")

### ❌ DO NOT generate queries that result in:
- Raw data dumps (e.g., "Show me all download counts")
- Singular value counts (e.g., "Count every unique value")
- Unfiltered listings (e.g., "List all paper titles")
- Meaningless aggregations (e.g., "Count each individual value")
- Simple counts without insight (e.g., "How many papers are there per year?")

## Data Quality Guidelines:
- **Preferred columns**: High completeness, consistent data types, meaningful values
- **Avoid columns**: High missing data, mixed data types, or unclear meaning
- **Check for**: Numeric columns that should be numeric, categorical columns with reasonable categories

## Query Types to Generate:
1. **Distribution analysis**: How are values distributed across categories?
2. **Trend analysis**: How do values change over time?
3. **Relationship analysis**: How do two variables relate to each other?
4. **Comparison analysis**: How do different groups compare?
5. **Ranking analysis**: What are the top/bottom performers?

## 🔍 Dataset Summary Analysis

Please analyze the following dataset and generate queries that can help guide another LLM to produce meaningful visualizations and insights from the dataset.

```json
{{02_generate_visualization_queries}}
```

## ✅ Output Format

Your final output **must be a JSON object** with the following structure:

- Each **key** is either a **single column name** (e.g., `"Conference"`) or a **combined key** of multiple columns (e.g., `"Year & PaperType"`) **STRICTLY** from {{attributes}}
- Each **value** is an object `queries` with **exactly 5 key-value pairs**, where:
  - The **key** is a query string.
  - The **value** is the suggested visualization type(s).

**🚨 CRITICAL INSTRUCTION: Use the examples below as INSPIRATION ONLY. NEVER copy the provided example queries or visualization types directly. Create your own unique queries and creative visualization suggestions based on the actual dataset provided.**

### Example Output

```json
{
  "Conference": {
    "queries": {
      "What is the distribution of papers by conference with interactive hover details?": "Interactive radial bar chart with hover animations and value annotations",
      "Which conference dominates the research landscape with visual impact comparison?": "Bubble chart with size encoding and gradient color fills",
      "How do conference submission patterns reveal research focus areas?": "Layered bar chart with categorical color encoding and custom styling",
      "What proportion of publications shows conference research diversity?": "Arc chart with polar coordinates and sequential color scheme",
      "Compare conference impact through multi-dimensional visualization": "Faceted small multiples with brushing and cross-filtering"
    }
  },
  "Year & PaperType": {
    "queries": {
      "How has the evolution of paper types created dynamic research trends?": "Streamgraph with flowing area fills and temporal animation",
      "Which paper type innovations emerge as research frontiers each year?": "Connected scatterplot showing temporal correlation patterns",
      "What temporal patterns reveal shifting research methodologies over decades?": "Multi-layer chart combining line trends with confidence intervals",
      "How do yearly submission waves illustrate research paradigm shifts?": "Interactive time series with brush selection and dynamic zooming",
      "Compare research diversity through temporal multi-dimensional analysis": "Heatmap with sequential color schemes and rich hover tooltips"
    }
  },
  "Year & PaperType & Citations": {
    "queries": {
      "How do citation patterns reveal research impact evolution across time and types?": "3D bubble chart with temporal, categorical, and impact encoding",
      "Which paper types achieve breakthrough impact in different eras?": "Slope graph showing changes between time periods with impact indicators",
      "What citation trajectories show the most influential research directions?": "Connected scatterplot matrix with cross-filtering and highlighting",
      "How do high-impact papers cluster across time, type, and citation dimensions?": "Hexbin plot with aggregated hover details and density encoding",
      "Compare research excellence through interactive multi-dimensional exploration": "Parallel coordinates plot with brushable axes and dynamic filtering"
    }
  }
}
