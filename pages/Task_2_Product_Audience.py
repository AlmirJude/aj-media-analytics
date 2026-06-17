import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="Product & Audience", layout="wide")
st.title("🎯 Task 2 — Product Category & Audience Analysis")
st.markdown("Which products and audiences deliver the best ROAS?")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Marketing_Data_Cleaned.xlsx")
    return df

df = load_data()

PRODUCT_COLORS  = {'Protein': '#3266ad', 'Diet': '#1D9E75', 'WeightLoss': '#D85A30', 'Preworkout': '#8B5CF6'}
AUDIENCE_COLORS = {'Athletes': '#3266ad', 'WeightLoss': '#1D9E75', 'FitnessEnth': '#D85A30'}

# ── SECTION 1: PRODUCT CATEGORY ───────────────────────────────────────────────
st.header("1. Product Category Performance")

product = df.groupby('Product_Category').agg(
    Spend=('Spend','sum'), Revenue=('Revenue','sum'),
    Purchases=('Purchases','sum'), Clicks=('Clicks','sum')
).round(2)
product['ROAS'] = (product['Revenue']/product['Spend']).round(4)
product['CPP']  = (product['Spend']/product['Purchases']).round(2)
product['CVR']  = (product['Purchases']/product['Clicks']).round(4)
product['Spend_Share_%'] = (product['Spend']/product['Spend'].sum()*100).round(2)

st.dataframe(product[['Spend','Revenue','ROAS','CVR','CPP','Spend_Share_%']],
             use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Protein ROAS", "1.27", delta="✅ Above target 1.2", delta_color="normal")
col2.metric("Diet ROAS", "1.07", delta="Near target")
col3.metric("Weight Loss ROAS", "0.76", delta="Below break-even", delta_color="inverse")
col4.metric("Preworkout ROAS", "0.60", delta="Worst performer", delta_color="inverse")

# ── SECTION 2: PRODUCT ROAS CHART ────────────────────────────────────────────
st.header("2. ROAS by Product Category")

product_sorted = product.sort_values('ROAS', ascending=False)

fig_prod = go.Figure(go.Bar(
    x=product_sorted.index.tolist(),
    y=product_sorted['ROAS'].tolist(),
    marker_color=[PRODUCT_COLORS.get(c, '#888') for c in product_sorted.index],
    text=[f"{v:.4f}" for v in product_sorted['ROAS']],
    textposition='outside'
))
fig_prod.add_hline(y=1.2, line_dash="dash", line_color="red",
                   annotation_text="Target ROAS (1.2)")
fig_prod.add_hline(y=1.0, line_dash="dot", line_color="gray",
                   annotation_text="Break-even")
fig_prod.update_layout(
    title="ROAS by Product Category",
    yaxis_title="ROAS",
    yaxis_range=[0, 1.6],
    height=400
)
st.plotly_chart(fig_prod, use_container_width=True)

# ── SECTION 3: PRODUCT COST PER PURCHASE ──────────────────────────────────────
st.header("3. Cost per Purchase by Product vs Average Order Value")

fig_cpp = go.Figure(go.Bar(
    x=product_sorted.index.tolist(),
    y=product_sorted['CPP'].tolist(),
    marker_color=[PRODUCT_COLORS.get(c, '#888') for c in product_sorted.index],
    text=[f"${v:.2f}" for v in product_sorted['CPP']],
    textposition='outside',
    orientation='v'
))
fig_cpp.add_hline(y=66.51, line_dash="dash", line_color="purple",
                  annotation_text="Avg Order Value ($66.51)")
fig_cpp.update_layout(
    title="Cost per Purchase by Product Category",
    yaxis_title="Cost per Purchase ($)",
    height=380
)
st.plotly_chart(fig_cpp, use_container_width=True)

st.error("""
**Preworkout's cost per purchase is $99.60 — nearly 50% above the average order value of $66.51.** 
Every Preworkout purchase costs $33 more to acquire than it generates in revenue. 
This category alone is a significant drain on overall profitability.
""")

# ── SECTION 4: PRODUCT STATISTICAL TESTS ─────────────────────────────────────
st.header("4. Statistical Significance — Product Categories")

products = df['Product_Category'].unique()
roas_by_product = {p: df[df['Product_Category']==p]['ROAS'].dropna() for p in products}

f_stat, p_anova = stats.f_oneway(*roas_by_product.values())
st.markdown(f"**ANOVA across all product categories:** F = {f_stat:.4f}, p = {p_anova:.6f} — {'✅ Significant' if p_anova < 0.05 else '❌ Not significant'}")

prod_list = list(products)
test_rows = []
for i in range(len(prod_list)):
    for j in range(i+1, len(prod_list)):
        p1, p2 = prod_list[i], prod_list[j]
        t, p = stats.ttest_ind(roas_by_product[p1], roas_by_product[p2])
        test_rows.append({
            'Comparison': f'{p1} vs {p2}',
            'p-value': round(p, 6),
            'Significant': '✅ YES' if p < 0.05 else '❌ NO'
        })

st.dataframe(pd.DataFrame(test_rows), use_container_width=True, hide_index=True)

# ── SECTION 5: AUDIENCE PERFORMANCE ──────────────────────────────────────────
st.header("5. Target Audience Performance")

audience = df.groupby('Target_Audience').agg(
    Spend=('Spend','sum'), Revenue=('Revenue','sum'),
    Purchases=('Purchases','sum'), Clicks=('Clicks','sum')
).round(2)
audience['ROAS'] = (audience['Revenue']/audience['Spend']).round(4)
audience['CPP']  = (audience['Spend']/audience['Purchases']).round(2)
audience['CVR']  = (audience['Purchases']/audience['Clicks']).round(4)
audience['Spend_Share_%'] = (audience['Spend']/audience['Spend'].sum()*100).round(2)

st.dataframe(audience[['Spend','Revenue','ROAS','CVR','CPP','Spend_Share_%']],
             use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("Athletes ROAS", "1.11", delta="Best audience", delta_color="normal")
col2.metric("Weight Loss ROAS", "1.07", delta="Good performer")
col3.metric("Fitness Enthusiasts ROAS", "0.67", delta="Worst performer", delta_color="inverse")

# ── SECTION 6: AUDIENCE ROAS CHART ───────────────────────────────────────────
st.header("6. ROAS by Target Audience")

audience_sorted = audience.sort_values('ROAS', ascending=False)

fig_aud = go.Figure(go.Bar(
    x=audience_sorted.index.tolist(),
    y=audience_sorted['ROAS'].tolist(),
    marker_color=[AUDIENCE_COLORS.get(c, '#888') for c in audience_sorted.index],
    text=[f"{v:.4f}" for v in audience_sorted['ROAS']],
    textposition='outside'
))
fig_aud.add_hline(y=1.2, line_dash="dash", line_color="red",
                  annotation_text="Target ROAS (1.2)")
fig_aud.add_hline(y=1.0, line_dash="dot", line_color="gray",
                  annotation_text="Break-even")
fig_aud.update_layout(
    title="ROAS by Target Audience",
    yaxis_title="ROAS",
    yaxis_range=[0, 1.5],
    height=380
)
st.plotly_chart(fig_aud, use_container_width=True)

st.warning("""
**Fitness Enthusiasts ROAS (0.67) is significantly below both Athletes (1.11) and 
Weight Loss (1.07).** Despite receiving 33% of budget, this audience is the least 
efficient. Budget should shift toward Athletes and Weight Loss segments.
""")

# ── SECTION 7: PRODUCT × AUDIENCE HEATMAP ────────────────────────────────────
st.header("7. Product Category × Audience ROAS Heatmap")

heatmap_data = df.groupby(['Product_Category','Target_Audience']).apply(
    lambda x: round(x['Revenue'].sum() / x['Spend'].sum(), 4)
).reset_index()
heatmap_data.columns = ['Product_Category','Target_Audience','ROAS']
heatmap_pivot = heatmap_data.pivot(
    index='Product_Category', columns='Target_Audience', values='ROAS'
)

fig_heat = px.imshow(
    heatmap_pivot,
    color_continuous_scale='RdYlGn',
    aspect='auto',
    title='ROAS Heatmap: Product Category × Target Audience',
    text_auto=True
)
fig_heat.update_layout(height=350)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("""
The heatmap pinpoints the highest-value combinations. 
Focus budget on the green cells — these are your most profitable product/audience pairs.
""")

# ── SECTION 8: LTV ANALYSIS ───────────────────────────────────────────────────
st.header("8. Customer LTV (Lifetime Value) by Platform")

ltv = df.groupby('Platform')['Customer_LTV'].mean().round(2)
ltv.index = ltv.index.map({'FB':'Facebook','Google':'Google','TT':'TikTok'})

fig_ltv = go.Figure(go.Bar(
    x=ltv.index.tolist(),
    y=ltv.values.tolist(),
    marker_color=['#3266ad','#1D9E75','#D85A30'],
    text=[f"${v:.2f}" for v in ltv.values],
    textposition='outside'
))
fig_ltv.update_layout(
    title="Average Customer LTV (Lifetime Value) by Platform",
    yaxis_title="Customer LTV ($)",
    height=350
)
st.plotly_chart(fig_ltv, use_container_width=True)

st.markdown("""
LTV analysis provides context beyond immediate ROAS. A platform with lower short-term ROAS 
but higher LTV customers may still be worth investing in for long-term profitability.
""")
