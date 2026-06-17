import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="Creative Analysis", layout="wide")
st.title("🎨 Task 2 — Creative Performance Analysis")
st.markdown("Video vs Image vs Carousel vs Search vs Display")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Marketing_Data_Cleaned.xlsx")
    return df

df = load_data()

COLORS = {
    'Video': '#3266ad', 'Image': '#1D9E75', 'Carousel': '#D85A30',
    'Search': '#8B5CF6', 'Display': '#F59E0B'
}

# ── SECTION 1: CREATIVE SUMMARY ───────────────────────────────────────────────
st.header("1. Creative Type Summary")

creative = df.groupby('Creative_Type').agg(
    Spend=('Spend','sum'), Revenue=('Revenue','sum'),
    Clicks=('Clicks','sum'), Purchases=('Purchases','sum'),
    Impressions=('Impressions','sum')
).round(2)
creative['ROAS'] = (creative['Revenue']/creative['Spend']).round(4)
creative['CTR']  = (creative['Clicks']/creative['Impressions']).round(4)
creative['CVR']  = (creative['Purchases']/creative['Clicks']).round(4)
creative['CPP']  = (creative['Spend']/creative['Purchases']).round(2)
creative['Spend_Share_%'] = (creative['Spend']/creative['Spend'].sum()*100).round(2)

# Fixed: use_container_width=True replaced with width='stretch'
st.dataframe(creative[['Spend','Revenue','ROAS','CTR','CVR','CPP','Spend_Share_%']],
             width='stretch')

# ── SECTION 2: ROAS BY CREATIVE ───────────────────────────────────────────────
st.header("2. ROAS by Creative Type")

creative_sorted = creative.sort_values('ROAS', ascending=False)
fig_roas = go.Figure(go.Bar(
    x=creative_sorted.index.tolist(),
    y=creative_sorted['ROAS'].tolist(),
    marker_color=[COLORS.get(c, '#636EFA') for c in creative_sorted.index], # Failsafe dictionary mapping
    text=[f"{v:.4f}" for v in creative_sorted['ROAS']],
    textposition='outside'
))
fig_roas.add_hline(y=1.2, line_dash="dash", line_color="red",
                   annotation_text="Target ROAS (1.2)")
fig_roas.add_hline(y=1.0, line_dash="dot", line_color="gray",
                   annotation_text="Break-even")
fig_roas.update_layout(
    title="ROAS by Creative Type",
    yaxis_title="ROAS",
    yaxis_range=[0, 1.7],
    height=400
)
# Fixed: width='stretch'
st.plotly_chart(fig_roas, width='stretch')

st.success("**Search is the only creative type exceeding the target ROAS (1.29 vs target 1.2).** It also has the lowest cost per purchase at $52.78.")
st.error("**Image has the worst ROAS (0.59) and highest cost per purchase ($101.16).** It should be significantly reduced or eliminated.")

# ── SECTION 3: MULTI-METRIC COMPARISON ───────────────────────────────────────
st.header("3. CTR, CVR, and CPP Comparison")

col1, col2 = st.columns(2)

with col1:
    fig_ctr = go.Figure(go.Bar(
        x=creative.index.tolist(),
        y=(creative['CTR']*100).tolist(),
        marker_color=[COLORS.get(c, '#636EFA') for c in creative.index],
        text=[f"{v:.2f}%" for v in (creative['CTR']*100)],
        textposition='outside'
    ))
    fig_ctr.update_layout(title="CTR (Click-Through Rate) %",
                          yaxis_title="CTR (%)", height=320)
    st.plotly_chart(fig_ctr, width='stretch')

with col2:
    fig_cpp = go.Figure(go.Bar(
        x=creative.index.tolist(),
        y=creative['CPP'].tolist(),
        marker_color=[COLORS.get(c, '#636EFA') for c in creative.index],
        text=[f"${v:.2f}" for v in creative['CPP']],
        textposition='outside'
    ))
    fig_cpp.add_hline(y=66.51, line_dash="dash", line_color="purple",
                      annotation_text="Avg Order Value ($66.51)")
    fig_cpp.update_layout(title="Cost per Purchase by Creative Type",
                          yaxis_title="Cost per Purchase ($)", height=320)
    st.plotly_chart(fig_cpp, width='stretch')

# ── SECTION 4: VCR vs CVR CORRELATION ────────────────────────────────────────
st.header("4. Video Completion Rate (VCR) vs Conversion Rate (CVR)")

# Check if required video columns exist before tracking metrics
if 'Video_Completion_Rate' in df.columns and 'CVR' in df.columns:
    video_df = df[df['Creative_Type']=='Video'][['Video_Completion_Rate','CVR']].dropna()
    
    if len(video_df) > 1:
        corr, p_val = stats.pearsonr(video_df['Video_Completion_Rate'], video_df['CVR'])
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Pearson Correlation (r)", f"{corr:.4f}")
            st.metric("p-value", f"{p_val:.6f}")
            st.metric("Statistically Significant", "✅ YES" if p_val < 0.05 else "❌ NO")
            st.markdown(f"""
            **Interpretation:** r = {corr:.4f} indicates a **weak negative correlation** between 
            video completion rate and conversion rate. This is a surprising and counterintuitive finding — 
            videos watched to completion are not necessarily converting better. 
            This suggests ad creative quality and relevance matter more than video length or completion.
            """)

        with col2:
            fig_scatter = px.scatter(
                video_df,
                x='Video_Completion_Rate',
                y='CVR',
                opacity=0.4,
                trendline='ols',
                title='Video Completion Rate vs Conversion Rate',
                labels={
                    'Video_Completion_Rate': 'Video Completion Rate (VCR)',
                    'CVR': 'Conversion Rate (CVR)'
                },
                color_discrete_sequence=['#3266ad']
            )
            fig_scatter.update_layout(height=380)
            st.plotly_chart(fig_scatter, width='stretch')
    else:
        st.info("Not enough matching Video completion rate data to trace trends.")
else:
    st.error("Missing column variables 'Video_Completion_Rate' or 'CVR' in the datasheet.")

# ── SECTION 5: SPEND vs ROAS SCATTER ─────────────────────────────────────────
st.header("5. Spend Allocation vs ROAS — Are We Investing in the Right Creatives?")

fig_alloc = go.Figure()
spend_by_creative = creative['Spend'].tolist()
roas_by_creative  = creative['ROAS'].tolist()
names_creative    = creative.index.tolist()

for i, c in enumerate(names_creative):
    fig_alloc.add_trace(go.Scatter(
        x=[spend_by_creative[i]],
        y=[roas_by_creative[i]],
        mode='markers+text',
        name=c,
        text=[c],
        textposition='top center',
        marker=dict(size=20, color=COLORS.get(c, '#636EFA'))
    ))

fig_alloc.add_hline(y=1.0, line_dash="dot", line_color="gray",
                    annotation_text="Break-even")
fig_alloc.update_layout(
    title="Creative Type: Spend vs ROAS",
    xaxis_title="Total Spend ($)",
    yaxis_title="ROAS",
    height=430
)
st.plotly_chart(fig_alloc, width='stretch')

st.warning("""
**Budget misallocation alert:** Video receives by far the highest spend ($2.17M, 49% of total) 
yet only achieves ROAS of 0.98 — below break-even. Search achieves the best ROAS (1.29) 
but only gets $898K (20% of spend). Display and Image have the worst ROAS yet still 
consume significant budget.
""")

# ── SECTION 6: PLATFORM × CREATIVE HEATMAP ───────────────────────────────────
st.header("6. Platform × Creative Type ROAS Heatmap")

heatmap_data = df.groupby(['Platform','Creative_Type']).apply(
    lambda x: round(x['Revenue'].sum() / x['Spend'].sum(), 4),
    include_groups=False # Keeps compatibility cleaner for future pandas versions
).reset_index()
heatmap_data.columns = ['Platform','Creative_Type','ROAS']
heatmap_pivot = heatmap_data.pivot(index='Platform', columns='Creative_Type', values='ROAS')

# Map names securely using a failsafe fallback dictionary mapping
platform_map = {'FB':'Facebook','Google':'Google','TT':'TikTok'}
heatmap_pivot.index = [platform_map.get(idx, idx) for idx in heatmap_pivot.index]

fig_heat = px.imshow(
    heatmap_pivot,
    color_continuous_scale='RdYlGn',
    aspect='auto',
    title='ROAS Heatmap: Platform × Creative Type',
    text_auto=True
)
fig_heat.update_layout(height=320)
st.plotly_chart(fig_heat, width='stretch')

st.markdown("""
This heatmap shows which platform + creative combinations are working. 
Use this to guide creative strategy by platform — not every creative type 
works equally across all platforms.
""")
