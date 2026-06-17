import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Data Quality", layout="wide")
st.title("📋 Task 1 — Data Quality & Exploration")
st.markdown("---")

@st.cache_data
def load_data():
    raw = pd.read_excel("data/Marketing_Data.xlsx")
    clean = pd.read_excel("data/Marketing_Data_Cleaned.xlsx")
    return raw, clean

raw, clean = load_data()

# ── SECTION 1: DATASET OVERVIEW ──────────────────────────────────────────────
st.header("1. Dataset Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Rows", f"{raw.shape[0]:,}")
col2.metric("Total Columns", f"{raw.shape[1]}")
col3.metric("Date Range", "Jan 1 – Mar 31, 2024")
col4.metric("Platforms", "Facebook, Google, TikTok")

st.markdown("""
The dataset contains **3,240 rows** of daily marketing performance data across 3 platforms, 
4 regions, 9 campaigns, and 5 creative types covering January through March 2024.
""")

# ── SECTION 2: MISSING VALUES ─────────────────────────────────────────────────
st.header("2. Missing Values Found")

missing = raw.isnull().sum().reset_index()
missing.columns = ['Column', 'Missing Count']
missing['Missing %'] = (missing['Missing Count'] / len(raw) * 100).round(2)
missing['Status'] = missing['Missing Count'].apply(
    lambda x: '🔴 Action required' if x > 0 else '✅ Complete'
)
missing = missing[missing['Missing Count'] > 0]

st.dataframe(missing, use_container_width=True, hide_index=True)

st.markdown("""
**Key observation:** The `Video_Completion_Rate` column appears to have 2,012 missing values, 
but 1,800 of these are non-video creative types (Image, Carousel, Search, Display) where 
a completion rate is simply not applicable — not truly missing. Only **212 rows** within 
actual Video creatives were genuinely missing.
""")

# ── SECTION 3: DATA ISSUES IDENTIFIED ────────────────────────────────────────
st.header("3. Data Issues Identified & How They Were Addressed")

issues = [
    {
        "Issue": "Missing Revenue (20 rows)",
        "Description": "Rows with Purchases recorded but no Revenue value",
        "Fix": "Imputed using average revenue-per-purchase grouped by Platform + Product Category",
        "Rows Affected": 20,
        "Severity": "🟡 Medium"
    },
    {
        "Issue": "Zero Clicks with Purchases (100 rows)",
        "Description": "Logically impossible — purchases recorded with zero clicks. Likely view-through attribution or tracking sync issue",
        "Fix": "Flagged with zero_clicks_flag. Excluded from CTR and CVR calculations only. Kept for Spend and ROAS.",
        "Rows Affected": 147,
        "Severity": "🔴 High"
    },
    {
        "Issue": "Spend Outliers (5 rows)",
        "Description": "Spend values of $60K–$119K vs campaign average of ~$1,400. Almost certainly data entry errors",
        "Fix": "Capped at campaign median × 3 using IQR method (winsorizing). Flagged with spend_outlier_flag",
        "Rows Affected": 5,
        "Severity": "🔴 High"
    },
    {
        "Issue": "Video Completion Rate — false nulls",
        "Description": "2,012 apparent nulls — but 1,800 are non-video rows where VCR is not applicable",
        "Fix": "Non-video rows left as NaN (correct). 212 genuinely missing video rows filled with median VCR (59.0%)",
        "Rows Affected": 212,
        "Severity": "🟡 Medium"
    },
    {
        "Issue": "CPM Inconsistency (5 rows)",
        "Description": "Reported CPM did not match the formula (Spend / Impressions) × 1,000",
        "Fix": "Recalculated entire CPM column from Spend and Impressions. Raw numbers trusted over derived field",
        "Rows Affected": 5,
        "Severity": "🟡 Medium"
    },
    {
        "Issue": "Zero Purchases with Revenue > 0 (47 rows)",
        "Description": "Revenue recorded but no purchase event — server-side tracking mismatch",
        "Fix": "Back-calculated Purchases using AOV (Average Order Value) of $66.51 from clean rows",
        "Rows Affected": 47,
        "Severity": "🟡 Medium"
    },
    {
        "Issue": "Duplicate Rows",
        "Description": "Checked for exact duplicate rows across all columns",
        "Fix": "None found — no action required",
        "Rows Affected": 0,
        "Severity": "✅ None"
    }
]

issues_df = pd.DataFrame(issues)
st.dataframe(issues_df, use_container_width=True, hide_index=True)

# ── SECTION 4: BEFORE vs AFTER CLEANING ──────────────────────────────────────
st.header("4. Before vs After Cleaning")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Raw Data — Missing Values")
    raw_missing = raw.isnull().sum()
    raw_missing = raw_missing[raw_missing > 0]
    fig = px.bar(
        x=raw_missing.values,
        y=raw_missing.index,
        orientation='h',
        color_discrete_sequence=['#E24B4A'],
        labels={'x': 'Missing Count', 'y': 'Column'}
    )
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Cleaned Data — Missing Values")
    clean_missing = clean.isnull().sum()
    clean_missing = clean_missing[clean_missing > 0]
    fig2 = px.bar(
        x=clean_missing.values,
        y=clean_missing.index,
        orientation='h',
        color_discrete_sequence=['#1D9E75'],
        labels={'x': 'Missing Count', 'y': 'Column'}
    )
    fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig2, use_container_width=True)

st.caption("Remaining NaN values in Video_Completion_Rate are non-video rows — correct and expected.")

# ── SECTION 5: DERIVED METRICS ────────────────────────────────────────────────
st.header("5. Derived Metrics Added After Cleaning")

metrics_info = pd.DataFrame({
    "Metric": ["CTR (Click-Through Rate)", "CPC (Cost Per Click)", "CVR (Conversion Rate)", "ROAS (Return on Ad Spend)"],
    "Formula": ["Clicks ÷ Impressions", "Spend ÷ Clicks", "Purchases ÷ Clicks", "Revenue ÷ Spend"],
    "Purpose": [
        "Measures how compelling the ad is at generating clicks",
        "Measures how efficiently the campaign buys traffic",
        "Measures how well clicks convert into actual purchases",
        "Primary KPI — revenue generated per dollar spent"
    ],
    "Overall Value": [
        f"{(clean['Clicks'].sum() / clean['Impressions'].sum()):.4f}",
        f"${(clean['Spend'].sum() / clean['Clicks'].sum()):.2f}",
        f"{(clean['Purchases'].sum() / clean['Clicks'].sum()):.4f}",
        f"{(clean['Revenue'].sum() / clean['Spend'].sum()):.4f}"
    ]
})
st.dataframe(metrics_info, use_container_width=True, hide_index=True)

# ── SECTION 6: KEY ASSUMPTIONS ────────────────────────────────────────────────
st.header("6. Key Assumptions")

st.markdown("""
The following assumptions were made during the cleaning process and could impact recommendations:

1. **Revenue imputation** assumes that average revenue per purchase within the same Platform + 
   Product Category is a reliable estimate. If pricing changed significantly during the period, 
   this may introduce error.

2. **Spend outlier capping** at median × 3 assumes the 5 extreme values are data entry errors 
   rather than genuine large spend events (e.g. campaign launch bursts). These rows are flagged 
   so they can be excluded from analysis if needed.

3. **Zero clicks with purchases** are assumed to be view-through or server-side attribution events, 
   not genuine organic purchases. This is standard in Google Ads and Meta but may overstate 
   platform contribution.

4. **Purchase back-calculation** using a single AOV ($66.51) assumes consistent pricing across 
   all platforms and product categories, which may not hold for premium products like Protein 
   vs Diet supplements.

5. **Video Completion Rate** median fill (59.0%) assumes missing VCR rows are missing at random 
   within video campaigns, not systematically missing for low-performing videos.
""")

# ── SECTION 7: BASELINE METRICS ──────────────────────────────────────────────
st.header("7. Baseline Metrics Summary")

st.markdown("These are the starting point metrics before any optimization:")

base_cols = st.columns(5)
overall_roas = clean['Revenue'].sum() / clean['Spend'].sum()
overall_ctr = clean['Clicks'].sum() / clean['Impressions'].sum()
overall_cvr = clean['Purchases'].sum() / clean['Clicks'].sum()
overall_cpc = clean['Spend'].sum() / clean['Clicks'].sum()
overall_cpp = clean['Spend'].sum() / clean['Purchases'].sum()

base_cols[0].metric("Overall ROAS", f"{overall_roas:.2f}", delta=f"{overall_roas - 1.2:.2f} vs 1.2 target", delta_color="inverse")
base_cols[1].metric("Overall CTR", f"{overall_ctr:.2%}")
base_cols[2].metric("Overall CVR", f"{overall_cvr:.2%}")
base_cols[3].metric("Avg CPC", f"${overall_cpc:.2f}")
base_cols[4].metric("Avg Cost/Purchase", f"${overall_cpp:.2f}")

st.markdown("""
**Most concerning trend:** The overall ROAS of **0.86** means the brand is losing **$0.14 for every 
dollar spent on advertising** — before accounting for product costs, fulfillment, or overhead. 
This means the business is currently loss-making on a contribution margin basis from advertising alone.
""")
