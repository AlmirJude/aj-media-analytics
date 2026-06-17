# DTC Fitness Supplements — Marketing Performance Analysis

An interactive Streamlit app presenting a full data analyst technical assessment 
for a DTC fitness supplements brand running campaigns across Facebook, Google, and TikTok.

## Pages

| Page | Description |
|------|-------------|
| 📋 Data Quality | Task 1 — Cleaning process, issues found, assumptions |
| 📈 Channel Analysis | Task 2 — Facebook vs Google vs TikTok with t-tests and ANOVA |
| 🗺️ Regional Analysis | Task 2 — West, South, Northeast, Midwest with significance testing |
| 🎨 Creative Analysis | Task 2 — Video, Image, Carousel, Search, Display + VCR vs CVR |
| 🎯 Product & Audience | Task 2 — Product category and audience ROAS comparison |
| 📅 Trends & Events | Task 2 — Weekly trends, competitive events, frequency analysis |

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data

Place the following files in the `data/` folder:
- `Marketing_Data.xlsx` (raw data)
- `Marketing_Data_Cleaned.xlsx` (cleaned data)

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- Scipy
