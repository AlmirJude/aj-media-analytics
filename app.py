import streamlit as st

st.set_page_config(
    page_title="DTC Marketing Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DTC Fitness Supplements — Marketing Performance Analysis")
st.markdown("---")

st.markdown("""
### About This Assessment
This interactive report presents a full data analysis of 3 months of marketing performance data 
(January – March 2024) for a DTC (Direct-to-Consumer) fitness supplements brand running campaigns 
across Facebook, Google, and TikTok.

**Use the sidebar to navigate between sections.**
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall ROAS", "0.86", delta="-0.34 vs target 1.2", delta_color="inverse")
col2.metric("Total Spend", "$4.40M", delta="3 months")
col3.metric("Total Revenue", "$3.79M")
col4.metric("Total Purchases", "63,025")

st.markdown("---")
st.markdown("""
### Navigation Guide
| Page | Content |
|------|---------|
| Data Quality | Cleaning process, issues found, assumptions |
| Channel Analysis | Facebook vs Google vs TikTok with significance tests |
| Creative Analysis | Video, Image, Carousel, Search, Display |
| Product & Audience | Product category and audience segment ROAS |
| Regional Analysis | West, South, Northeast, Midwest performance |
| Trends & Events | Weekly trends, competitive event impact, frequency analysis |
| Recommendations | Actionable insights and strategic recommendations |
| Advanced Analytics | Predictive modeling, clustering, and advanced visualizations |
""")
