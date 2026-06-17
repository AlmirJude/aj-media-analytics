import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="Trends & Events", layout="wide")
st.title("📅 Task 2 — Trends, Competitive Events & Frequency Analysis")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Marketing_Data_Cleaned.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.isocalendar().week
    return df

df = load_data()

# ── SECTION 1: WEEKLY OVERALL TREND ──────────────────────────────────────────
st.header("1. Overall Weekly ROAS Trend")

weekly_overall = df.groupby('Week').apply(
    lambda x: x['Revenue'].sum() / x['Spend'].sum()
).reset_index()
weekly_overall.columns = ['Week','ROAS']

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=weekly_overall['Week'],
    y=weekly_overall['ROAS'],
    mode='lines+markers',
    line=dict(color='#3266ad', width=3),
    marker=dict(size=7),
    name='Overall ROAS',
    fill='tozeroy',
    fillcolor='rgba(50, 102, 173, 0.1)'
))
fig_trend.add_hline(y=1.2, line_dash="dash", line_color="red",
                    annotation_text="Target ROAS (1.2)")
fig_trend.add_hline(y=1.0, line_dash="dot", line_color="gray",
                    annotation_text="Break-even (1.0)")

fig_trend.update_layout(
    title="Overall Weekly ROAS — Jan to Mar 2024",
    xaxis_title="Week Number",
    yaxis_title="ROAS",
    height=430,
    xaxis=dict(tickmode='linear', tick0=1, dtick=1)
)
st.plotly_chart(fig_trend, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("Week 1 ROAS", "1.49", delta="Started above break-even")
col2.metric("Week 13 ROAS", "0.48", delta="-67% decline", delta_color="inverse")
col3.metric("Weeks above 1.0", "6 of 13", delta="Only first 6 weeks profitable")

st.error("""
**The overall ROAS declined from 1.49 in Week 1 to 0.48 in Week 13 — a 67% decline over 3 months.** 
The business was profitable in January but became increasingly loss-making through February 
and March. This sustained decline suggests a structural problem beyond just channel mix.
""")

# ── SECTION 2: WEEK OVER WEEK CHANGE ─────────────────────────────────────────
st.header("2. Week-over-Week ROAS Change")

weekly_overall['WoW_Change'] = weekly_overall['ROAS'].pct_change() * 100
weekly_overall['Color'] = weekly_overall['WoW_Change'].apply(
    lambda x: '#1D9E75' if x >= 0 else '#E24B4A'
)

fig_wow = go.Figure(go.Bar(
    x=weekly_overall['Week'][1:],
    y=weekly_overall['WoW_Change'][1:].round(2),
    marker_color=weekly_overall['Color'][1:].tolist(),
    text=[f"{v:.1f}%" for v in weekly_overall['WoW_Change'][1:]],
    textposition='outside'
))
fig_wow.add_hline(y=0, line_color="gray", line_width=1)
fig_wow.update_layout(
    title="Week-over-Week ROAS % Change",
    xaxis_title="Week",
    yaxis_title="WoW Change (%)",
    height=380
)
st.plotly_chart(fig_wow, use_container_width=True)

# ── SECTION 3: COMPETITIVE EVENTS ────────────────────────────────────────────
st.header("3. Impact of Competitive Events")

st.markdown("""
Competitive events are periods where competitor brands run major promotions 
(e.g. holiday sales, product launches), increasing auction competition and CPMs.
""")

comp_summary = df.groupby('Is_Competitive_Event').agg(
    Spend=('Spend','sum'), Revenue=('Revenue','sum'),
    Purchases=('Purchases','sum'), Rows=('Spend','count')
).round(2)
comp_summary['ROAS'] = (comp_summary['Revenue']/comp_summary['Spend']).round(4)
comp_summary['CPP']  = (comp_summary['Spend']/comp_summary['Purchases']).round(2)
comp_summary['Avg_CPM'] = df.groupby('Is_Competitive_Event')['CPM'].mean().round(2)
comp_summary.index = comp_summary.index.map({True: 'Competitive Event', False: 'Normal Period'})

st.dataframe(comp_summary[['Spend','Revenue','ROAS','CPP','Avg_CPM','Rows']],
             use_container_width=True)

ce_true  = df[df['Is_Competitive_Event']==True]['ROAS'].dropna()
ce_false = df[df['Is_Competitive_Event']==False]['ROAS'].dropna()
t, p = stats.ttest_ind(ce_true, ce_false)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Normal ROAS", f"{ce_false.mean():.4f}")
col2.metric("Competitive Event ROAS", f"{ce_true.mean():.4f}",
            delta=f"{ce_true.mean()-ce_false.mean():.4f}", delta_color="inverse")
col3.metric("t-statistic", f"{t:.4f}")
col4.metric("p-value", f"{p:.4f}", delta="✅ Significant" if p < 0.05 else "❌ Not significant")

fig_comp = go.Figure(go.Bar(
    x=['Normal Period', 'Competitive Event'],
    y=[ce_false.mean(), ce_true.mean()],
    marker_color=['#1D9E75', '#E24B4A'],
    text=[f"{ce_false.mean():.4f}", f"{ce_true.mean():.4f}"],
    textposition='outside'
))
fig_comp.add_hline(y=1.0, line_dash="dot", line_color="gray")
fig_comp.update_layout(
    title="Average ROAS: Normal vs Competitive Event Periods",
    yaxis_title="Mean ROAS",
    yaxis_range=[0, 1.2],
    height=360
)
st.plotly_chart(fig_comp, use_container_width=True)

st.warning("""
**ROAS drops significantly during competitive events (0.836 vs 0.959 in normal periods, p = 0.005).** 
The brand should consider reducing bids during competitive periods to protect margins, 
or shifting budget to lower-competition channels like Search during these windows.
""")

# ── SECTION 4: FREQUENCY vs CVR ──────────────────────────────────────────────
st.header("4. Ad Frequency vs Conversion Rate")

freq_cvr = df[['Frequency','CVR']].dropna()
corr_f, p_f = stats.pearsonr(freq_cvr['Frequency'], freq_cvr['CVR'])

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Pearson Correlation", f"{corr_f:.4f}")
    st.metric("p-value", f"{p_f:.4f}")
    st.metric("Significant", "❌ NO" if p_f >= 0.05 else "✅ YES")
    st.markdown(f"""
    **Interpretation:** r = {corr_f:.4f} is essentially zero — there is **no meaningful 
    relationship between how often users see the ad and whether they convert.** 
    This suggests that simply showing ads more frequently will not improve conversion rates. 
    Creative quality and targeting matter far more than frequency.
    """)

with col2:
    freq_bins = pd.cut(df['Frequency'], bins=[0,1,2,3,4,5,10,100],
                       labels=['0-1','1-2','2-3','3-4','4-5','5-10','10+'])
    freq_cvr_binned = df.groupby(freq_bins)['CVR'].mean().reset_index()
    freq_cvr_binned.columns = ['Frequency_Range','Avg_CVR']

    fig_freq = go.Figure(go.Bar(
        x=freq_cvr_binned['Frequency_Range'].astype(str),
        y=(freq_cvr_binned['Avg_CVR']*100).round(3),
        marker_color='#8B5CF6',
        text=[f"{v:.2f}%" for v in (freq_cvr_binned['Avg_CVR']*100)],
        textposition='outside'
    ))
    fig_freq.update_layout(
        title="Average CVR by Frequency Range",
        xaxis_title="Frequency (avg times user sees ad)",
        yaxis_title="Avg CVR (%)",
        height=380
    )
    st.plotly_chart(fig_freq, use_container_width=True)

# ── SECTION 5: DAILY SPEND & REVENUE ─────────────────────────────────────────
st.header("5. Daily Spend vs Revenue Over Time")

daily = df.groupby('Date').agg(
    Spend=('Spend','sum'),
    Revenue=('Revenue','sum')
).reset_index()

fig_daily = go.Figure()
fig_daily.add_trace(go.Scatter(
    x=daily['Date'], y=daily['Spend'],
    name='Daily Spend',
    line=dict(color='#E24B4A', width=1.5),
    fill='tozeroy',
    fillcolor='rgba(226,75,74,0.1)'
))
fig_daily.add_trace(go.Scatter(
    x=daily['Date'], y=daily['Revenue'],
    name='Daily Revenue',
    line=dict(color='#1D9E75', width=1.5),
    fill='tozeroy',
    fillcolor='rgba(29,158,117,0.1)'
))
fig_daily.update_layout(
    title="Daily Spend vs Revenue (Jan–Mar 2024)",
    xaxis_title="Date",
    yaxis_title="Amount ($)",
    height=420,
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
st.plotly_chart(fig_daily, use_container_width=True)

st.markdown("""
The gap between Spend (red) and Revenue (green) widens over time — confirming the 
declining efficiency trend. In January spend and revenue tracked closely. 
By March, spend consistently exceeds revenue, indicating a worsening loss position.
""")

# ── SECTION 6: SUMMARY TABLE ─────────────────────────────────────────────────
st.header("6. All Analyses Summary — Key Numbers")

summary = pd.DataFrame({
    'Analysis': [
        'Channel (Platform)',
        'Regional',
        'Creative Type',
        'Product Category',
        'Target Audience',
        'Competitive Events',
        'Frequency vs CVR',
        'VCR vs CVR'
    ],
    'Best Performer': [
        'Google (ROAS 1.10)',
        'Northeast (ROAS 1.04)',
        'Search (ROAS 1.29)',
        'Protein (ROAS 1.27)',
        'Athletes (ROAS 1.11)',
        'Normal periods (ROAS 0.96)',
        'No significant relationship',
        'Weak negative correlation'
    ],
    'Worst Performer': [
        'Facebook (ROAS 0.80)',
        'Midwest (ROAS 0.84)',
        'Image (ROAS 0.59)',
        'Preworkout (ROAS 0.60)',
        'Fitness Enthusiasts (ROAS 0.67)',
        'Competitive events (ROAS 0.84)',
        'N/A',
        'N/A'
    ],
    'Statistically Significant': [
        '✅ YES (p < 0.0001)',
        '✅ YES (p < 0.0001)',
        '✅ YES',
        '✅ YES',
        '✅ YES',
        '✅ YES (p = 0.005)',
        '❌ NO (p = 0.99)',
        '✅ YES (p < 0.0001)'
    ]
})
st.dataframe(summary, use_container_width=True, hide_index=True)
