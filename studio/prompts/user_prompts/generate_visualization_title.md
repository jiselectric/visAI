## Instructions

Craft a title that is both informative and engaging, accurately reflecting the scope of the analysis. The title should be a single sentence that captures the main finding or insight of the analysis.

## Input Data:
question: {{question}}
computed_data: {{computed_data}}

## Requirements
- The title should be a single sentence that captures the main finding or insight of the analysis.
- The title should be informative and engaging.
- The title should accurately reflect the scope of the analysis.

## Examples

### Example 1:
question: "What is the correlation between the number of Downloads_Xplore and the AminerCitationCount across different Conferences?"
category: "correlation"
computed_data:
```json
[
      {
        "Conference": "InfoVis",
        "Downloads_Xplore": 1453.282110091743,
        "AminerCitationCount": 117.7809633027523
      },
      {
        "Conference": "SciVis",
        "Downloads_Xplore": 890.9800664451827,
        "AminerCitationCount": 31.289036544850497
      },
      {
        "Conference": "VAST",
        "Downloads_Xplore": 1192.8279132791329,
        "AminerCitationCount": 54.38211382113821
      },
      {
        "Conference": "Vis",
        "Downloads_Xplore": 382.8345323741007,
        "AminerCitationCount": 78.54807063440157
      }
    ]
```

**Output:**
**Title: "Correlation between Downloads_Xplore and AminerCitationCount across different Conferences"**

### Example 2:
question: "How has the distribution of CitationCount_CrossRef changed over the years?"
category: "distribution"
computed_data:
```json
[
      {
        "Year": 1990,
        "count": 53.0,
        "mean": 18.867924528301888,
        "std": 58.228673129788326,
        "min": 0.0,
        "25%": 1.0,
        "50%": 5.0,
        "75%": 12.0,
        "max": 407.0
      },
      {
        "Year": 1991,
        "count": 57.0,
        "mean": 21.894736842105264,
        "std": 62.44617230935956,
        "min": 0.0,
        "25%": 1.0,
        "50%": 6.0,
        "75%": 11.0,
        "max": 418.0
      },
      {
        "Year": 1992,
        "count": 59.0,
        "mean": 12.016949152542374,
        "std": 16.356472435456634,
        "min": 0.0,
        "25%": 2.0,
        "50%": 7.0,
        "75%": 13.5,
        "max": 97.0
      },
      {
        "Year": 1993,
        "count": 55.0,
        "mean": 15.690909090909091,
        "std": 18.22581881234617,
        "min": 0.0,
        "25%": 2.0,
        "50%": 7.0,
        "75%": 22.0,
        "max": 76.0
      },
      {
        "Year": 1994,
        "count": 59.0,
        "mean": 17.033898305084747,
        "std": 28.906487818299198,
        "min": 0.0,
        "25%": 2.0,
        "50%": 6.0,
        "75%": 17.5,
        "max": 171.0
      },
      {
        "Year": 1995,
        "count": 53.0,
        "mean": 14.886792452830188,
        "std": 26.638528994511097,
        "min": 0.0,
        "25%": 2.0,
        "50%": 6.0,
        "75%": 13.0,
        "max": 144.0
      },
      {
        "Year": 1996,
        "count": 57.0,
        "mean": 16.63157894736842,
        "std": 25.86146051515286,
        "min": 0.0,
        "25%": 2.0,
        "50%": 7.0,
        "75%": 17.0,
        "max": 125.0
      },
      {
        "Year": 1997,
        "count": 56.0,
        "mean": 21.696428571428573,
        "std": 48.01602989182583,
        "min": 0.0,
        "25%": 2.0,
        "50%": 6.0,
        "75%": 20.0,
        "max": 305.0
      },
      {
        "Year": 1998,
        "count": 57.0,
        "mean": 18.157894736842106,
        "std": 21.033486550790937,
        "min": 0.0,
        "25%": 2.0,
        "50%": 9.0,
        "75%": 25.0,
        "max": 86.0
      },
      {
        "Year": 1999,
        "count": 56.0,
        "mean": 19.464285714285715,
        "std": 29.897850865809714,
        "min": 0.0,
        "25%": 2.0,
        "50%": 8.0,
        "75%": 23.5,
        "max": 158.0
      }
    ]
```

**Output:**
**Title: "Distribution of CitationCount_CrossRef across different Years"**


### Exmple 3:
question: "What are the most common keywords found in the `AuthorKeywords`?"
category: "textual"
computed_data:
```json
[
      {
        "Keyword": "",
        "Frequency": 240
      },
      {
        "Keyword": "visual analytics",
        "Frequency": 135
      },
      {
        "Keyword": "visualization",
        "Frequency": 127
      },
      {
        "Keyword": "Visualization",
        "Frequency": 100
      },
      {
        "Keyword": "information visualization",
        "Frequency": 99
      },
      {
        "Keyword": "volume rendering",
        "Frequency": 95
      },
      {
        "Keyword": "Visual Analytics",
        "Frequency": 72
      },
      {
        "Keyword": "Information visualization",
        "Frequency": 57
      },
      {
        "Keyword": "Visual analytics",
        "Frequency": 55
      },
      {
        "Keyword": "interaction",
        "Frequency": 47
      },
      {
        "Keyword": "flow visualization",
        "Frequency": 46
      }
    ]
```

**Output:**
**Title: "Most common keywords in AuthorKeywords"**

## Expected Output
- **Only** return the title text as a plain string (no quotes, no formatting).