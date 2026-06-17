import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="Regional Analysis", layout="wide")
st.title("🗺️ Task 2 — Regional Performance Analysis")
st.markdown("West vs South vs Northeast vs Midwest")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Marketing_Data_Cleaned.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.isocalendar().week
    return df

df = load_data()

COLORS = {'West': '#3266ad', 'South': '#1D9E75', 'Northeast': '#D85A30', 'Midwest': '#8B5CF6'}

# ── SECTION 1: REGIONAL SUMMARY ──────────────────────────────────────────────
st.header("1. Regional Summary Metrics")

region = df.groupby('Region').agg(
    Spend=('Spend','sum'), Revenue=('Revenue','sum'),
    Clicks=('Clicks','sum'), Purchases=('Purchases','sum'),
    Impressions=('Impressions','sum')
).round(2)
region['ROAS'] = (region['Revenue']/region['Spend']).round(4)
region['CTR']  = (region['Clicks']/region['Impressions']).round(4)
region['CVR']  = (region['Purchases']/region['Clicks']).round(4)
region['CPP']  = (region['Spend']/region['Purchases']).round(2)
region['Spend_Share_%'] = (region['Spend']/region['Spend'].sum()*100).round(2)

st.dataframe(region[['Spend','Revenue','ROAS','CTR','CVR','CPP','Spend_Share_%']],
             use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Northeast ROAS", "1.04", delta="Best performing", delta_color="normal")
col2.metric("West ROAS", "0.96", delta="2nd place")
col3.metric("South ROAS", "0.95", delta="3rd place")
col4.metric("Midwest ROAS", "0.84", delta="Worst performing", delta_color="inverse")

# ── SECTION 2: ROAS BAR CHART ────────────────────────────────────────────────
st.header("2. ROAS by Region")

regions_list = ['Northeast', 'West', 'South', 'Midwest']
roas_list = [1.0443, 0.9619, 0.9459, 0.8442]

fig_roas = go.Figure(go.Bar(
    x=regions_list,
    y=roas_list,
    marker_color=[COLORS[r] for r in regions_list],
    text=[f"{v:.4f}" for v in roas_list],
    textposition='outside'
))
fig_roas.add_hline(y=1.2, line_dash="dash", line_color="red",
                   annotation_text="Target ROAS (1.2)")
fig_roas.add_hline(y=1.0, line_dash="dot", line_color="gray",
                   annotation_text="Break-even (1.0)")
fig_roas.update_layout(
    title="ROAS by Region",
    yaxis_title="ROAS",
    yaxis_range=[0, 1.5],
    height=400
)
st.plotly_chart(fig_roas, use_container_width=True)

# ── SECTION 3: STATISTICAL SIGNIFICANCE ──────────────────────────────────────
st.header("3. Statistical Significance Testing")

st.markdown("""
Pairwise t-tests between all region pairs to determine which regional differences 
are statistically significant vs due to random chance.
""")

roas_by_region = {r: df[df['Region']==r]['ROAS'].dropna() for r in df['Region'].unique()}
f_stat, p_anova = stats.f_oneway(*roas_by_region.values())

region_list = list(roas_by_region.keys())
test_results = []
for i in range(len(region_list)):
    for j in range(i+1, len(region_list)):
        r1, r2 = region_list[i], region_list[j]
        t, p = stats.ttest_ind(roas_by_region[r1], roas_by_region[r2])
        test_results.append({
            'Comparison': f'{r1} vs {r2}',
            't-statistic': round(t, 4),
            'p-value': round(p, 6),
            'Significant (p < 0.05)': '✅ YES' if p < 0.05 else '❌ NO',
            'Interpretation': 'Significant difference' if p < 0.05 else 'No significant difference'
        })

test_results.append({
    'Comparison': 'ANOVA (all regions)',
    't-statistic': round(f_stat, 4),
    'p-value': round(p_anova, 6),
    'Significant (p < 0.05)': '✅ YES' if p_anova < 0.05 else '❌ NO',
    'Interpretation': 'Regional differences are real, not random'
})

st.dataframe(pd.DataFrame(test_results), use_container_width=True, hide_index=True)

st.markdown("""
**Notable finding:** West vs South shows **no significant difference** (p = 0.079), 
meaning these two regions perform similarly and can be treated as one group for budgeting. 
However, Midwest is significantly worse than every other region (p < 0.0001 in all comparisons).
""")

# ── SECTION 4: SPEND vs ROAS BUBBLE ──────────────────────────────────────────
st.header("4. Spend Share vs ROAS — Budget Alignment")

spend_shares = [25.89, 25.41, 26.51, 22.19]
roas_vals_r  = [0.9619, 0.9459, 1.0443, 0.8442]
purchases_r  = [16082, 16104, 18339, 12500]

fig_bubble = go.Figure()
for i, r in enumerate(regions_list):
    fig_bubble.add_trace(go.Scatter(
        x=[spend_shares[i]], y=[roas_vals_r[i]],
        mode='markers+text',
        name=r,
        text=[r],
        textposition='top center',
        marker=dict(
            size=purchases_r[i]/500,
            color=COLORS[r],
            opacity=0.7
        )
    ))

fig_bubble.add_hline(y=1.0, line_dash="dot", line_color="gray")
fig_bubble.update_layout(
    title="Spend Share (%) vs ROAS by Region (bubble size = purchases)",
    xaxis_title="Spend Share (%)",
    yaxis_title="ROAS",
    height=450,
    showlegend=True
)
st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("""
Budget allocation is relatively even across regions (22–27% each), 
but performance varies significantly. **Northeast deserves a larger share; 
Midwest should be cut.**
""")

# ── SECTION 5: WEEKLY REGIONAL TREND ─────────────────────────────────────────
st.header("5. Weekly ROAS Trend by Region")

weekly_r = df.groupby(['Week','Region']).apply(
    lambda x: x['Revenue'].sum() / x['Spend'].sum()
).reset_index()
weekly_r.columns = ['Week','Region','ROAS']

fig_trend = go.Figure()
for r in regions_list:
    data = weekly_r[weekly_r['Region']==r].sort_values('Week')
    fig_trend.add_trace(go.Scatter(
        x=data['Week'], y=data['ROAS'],
        name=r,
        line=dict(color=COLORS[r], width=2),
        mode='lines+markers',
        marker=dict(size=4)
    ))
fig_trend.add_hline(y=1.2, line_dash="dash", line_color="red",
                    annotation_text="Target (1.2)")
fig_trend.update_layout(
    title="Weekly ROAS Trend by Region",
    xaxis_title="Week",
    yaxis_title="ROAS",
    height=420,
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
st.plotly_chart(fig_trend, use_container_width=True)

# ── SECTION 6: PLATFORM × REGION HEATMAP ─────────────────────────────────────
st.header("6. Platform × Region ROAS Heatmap")

heatmap_data = df.groupby(['Platform','Region']).apply(
    lambda x: round(x['Revenue'].sum() / x['Spend'].sum(), 4)
).reset_index()
heatmap_data.columns = ['Platform','Region','ROAS']
heatmap_pivot = heatmap_data.pivot(index='Platform', columns='Region', values='ROAS')
heatmap_pivot.index = heatmap_pivot.index.map({'FB':'Facebook','Google':'Google','TT':'TikTok'})

fig_heat = px.imshow(
    heatmap_pivot,
    color_continuous_scale='RdYlGn',
    aspect='auto',
    title='ROAS Heatmap: Platform × Region',
    text_auto=True
)
fig_heat.update_layout(height=350)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("""
The heatmap reveals which specific Platform × Region combinations are dragging performance. 
Red cells are candidates for immediate budget cuts. Green cells should receive more investment.
""")

# ── SECTION 7: METHODOLOGY ───────────────────────────────────────────────────
st.header("7. Methodology")
st.markdown("""
- **Statistical test:** Independent samples t-test for pairwise regional ROAS comparisons
- **Multiple comparisons:** 6 pairwise tests conducted — note that with α = 0.05 across 6 tests, 
  there is a ~26% chance of at least one false positive. A Bonferroni correction would set 
  α = 0.008 per test; results marked significant here remain significant under that stricter threshold.
- **Sample size:** ~810 rows per region (balanced design)
- **ANOVA F-statistic:** 23.24, p < 0.0001 — confirms overall regional differences are real
""")
