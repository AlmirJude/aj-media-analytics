import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Strategic Recommendations", layout="wide")
st.title("💡 Task 3 — Strategic Recommendations")
st.markdown("Immediate optimizations, A/B tests, and long-term strategy")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Marketing_Data_Cleaned.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.isocalendar().week
    return df

df = load_data()

# ── SECTION 1: EXECUTIVE SUMMARY ─────────────────────────────────────────────
st.header("📄 Executive Summary")

st.markdown("""
> *Maximum 750 words — written for a non-technical marketing leadership audience*
""")

with st.expander("Read Full Executive Summary", expanded=True):
    st.markdown("""
    ### DTC Fitness Supplements — Marketing Optimization Executive Summary

    **Overview**

    Analysis of three months of marketing performance data (January–March 2024) across Facebook, 
    Google, and TikTok reveals a business spending $4.4M on advertising that generated only $3.79M 
    in revenue — an overall ROAS (Return on Ad Spend) of 0.86, significantly below the 1.2 target 
    and the industry benchmark of 1.4. Every dollar spent on advertising currently returns only 
    $0.86 in revenue before accounting for product costs or overhead.

    ---

    **5 Key Insights**

    **1. Google is underinvested; Facebook is overfunded.**
    Google achieves a ROAS of 1.10 at a cost per purchase of $60.32 — the only platform 
    near the target — yet receives only 28.6% of budget. Facebook achieves a ROAS of 0.80 
    with a cost per purchase of $83.25 (above the average order value of $66.51), meaning 
    Facebook literally loses money on every conversion. These differences are statistically 
    significant (p < 0.0001).

    **2. Search creative is the only format exceeding the ROAS target.**
    Search ads achieve ROAS 1.29, the only creative type above 1.2. Image (0.59) and 
    Display (0.64) are severely underperforming yet consuming $742K in combined spend. 
    Video consumes 49% of total creative budget but achieves only 0.98 ROAS.

    **3. Protein and Diet are profitable; Preworkout is destroying value.**
    Protein achieves ROAS 1.27 with a cost per purchase of $63.04. Preworkout achieves 
    ROAS 0.60 with a cost per purchase of $99.60 — spending $33 more per customer than 
    it generates in revenue. Preworkout alone consumes $1.24M (28% of total spend).

    **4. Performance is declining sharply across all channels.**
    ROAS fell from 1.49 in Week 1 to 0.48 in Week 13 — a 67% decline. The business 
    was profitable in January and loss-making by March. This systematic decline across 
    all platforms simultaneously suggests audience fatigue or market saturation rather 
    than a platform-specific issue.

    **5. The Midwest region and Fitness Enthusiasts audience are consistent underperformers.**
    Midwest ROAS (0.84) is significantly lower than all other regions (p < 0.0001). 
    Fitness Enthusiasts ROAS (0.67) is the worst audience segment despite receiving 
    33% of budget.

    ---

    **Prioritized Recommendations**

    | Priority | Action | Expected Impact |
    |----------|--------|-----------------|
    | 🔴 Immediate | Cut Facebook spend by 50% ($692K savings) | Redirect to Google; estimated +$138K revenue |
    | 🔴 Immediate | Eliminate Image and Display creative ($742K) | Reallocate to Search; estimated +$371K revenue |
    | 🔴 Immediate | Reduce Preworkout budget by 60% ($744K) | Stop $33/purchase loss on every conversion |
    | 🟡 30 days | Increase Google Search budget by 40% | Capitalize on 1.29 ROAS at scale |
    | 🟡 30 days | Reduce Midwest allocation by 30% | Reallocate to Northeast (ROAS 1.04) |
    | 🟢 60 days | Launch 3 A/B tests (detailed below) | Improve creative and audience efficiency |
    | 🟢 90 days | Implement competitive event bidding rules | Protect margins during high-competition periods |

    ---

    **Implementation Timeline**

    - **Week 1–2:** Execute budget cuts on Facebook, Image, Display, and Preworkout
    - **Week 3–4:** Increase Google Search and Protein/Diet budgets with reallocated funds
    - **Month 2:** Launch A/B tests on video creative length and audience targeting
    - **Month 3:** Review results, adjust regional allocation, build competitive event playbook

    ---

    **Risk Assessment**

    The primary risk of cutting Facebook spend is reduced reach and brand awareness, 
    particularly for top-of-funnel audiences. Mitigate by maintaining a minimal Facebook 
    brand awareness budget ($150K/month) while cutting performance campaigns aggressively. 
    The declining ROAS trend across all platforms may reflect seasonal demand reduction 
    in Q1 — monitor Q2 baseline before drawing permanent conclusions about channel viability.

    ---

    **Measurement Plan**

    Success will be measured weekly on: overall ROAS (target: improve from 0.86 to 1.0 within 
    60 days), cost per purchase (target: reduce from $70 blended to below $66.51 AOV), 
    and platform ROAS gap (target: reduce Facebook-Google gap from 0.31 to under 0.15).
    """)

# ── SECTION 2: 30% SPEND CUT FRAMEWORK ───────────────────────────────────────
st.header("3a. Immediate Optimization — 30% Spend Cut Framework")

st.markdown("""
The 30% cut target is **$1,319,425** from a total spend base of $4,398,084.
Below is the framework for exactly where to cut and why.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Where to Cut")
    cuts = pd.DataFrame({
        'Area': ['Facebook (performance campaigns)', 'Image creative (all platforms)', 'Display creative (Google)', 'Preworkout product (60% cut)', 'Midwest region (30% cut)'],
        'Current Spend ($)': [1383515, 384729, 357224, 1240117, 975913],
        'Recommended Cut ($)': [691757, 384729, 357224, 744070, 292774],
        'ROAS': [0.7981, 0.5947, 0.6369, 0.6028, 0.8442],
        'Reason': [
            'CPP $83 > AOV $66 — losing money per conversion',
            'Worst ROAS (0.59) — no profitable use case found',
            'ROAS 0.64 — below break-even on all platforms',
            'CPP $99 — $33 loss per purchase',
            'Significantly underperforms all other regions'
        ]
    })
    st.dataframe(cuts, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Where to Reinvest")
    gains = pd.DataFrame({
        'Area': ['Google Search (increase 40%)', 'Protein product (increase 25%)', 'Northeast region (increase 20%)', 'Athletes audience (increase 15%)'],
        'Current Spend ($)': [898815, 1288668, 1166104, 1673397],
        'Recommended Add ($)': [359526, 322167, 233221, 251010],
        'ROAS': [1.2904, 1.2655, 1.0443, 1.1113],
        'Reason': [
            'Only creative above target ROAS (1.29)',
            'Only product above target ROAS (1.27)',
            'Best regional performer',
            'Best audience ROAS (1.11)'
        ]
    })
    st.dataframe(gains, use_container_width=True, hide_index=True)

# Waterfall chart
st.subheader("Budget Reallocation Waterfall")

fig_waterfall = go.Figure(go.Waterfall(
    name="Budget Flow",
    orientation="v",
    measure=["relative","relative","relative","relative","relative",
             "total",
             "relative","relative","relative","relative","total"],
    x=["Cut Facebook","Cut Image","Cut Display","Cut Preworkout","Cut Midwest",
       "Total Cuts",
       "Add Google Search","Add Protein","Add Northeast","Add Athletes",
       "Final Budget"],
    y=[-691757, -384729, -357224, -744070, -292774,
       0,
       359526, 322167, 233221, 251010,
       0],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "#E24B4A"}},
    increasing={"marker": {"color": "#1D9E75"}},
    totals={"marker": {"color": "#3266ad"}}
))
fig_waterfall.update_layout(
    title="Spend Cut and Reinvestment Plan",
    yaxis_title="Budget Change ($)",
    height=450
)
st.plotly_chart(fig_waterfall, use_container_width=True)

# ── SECTION 3: CAMPAIGN-LEVEL CUTS ───────────────────────────────────────────
st.header("Campaign-Level Cut Recommendations")

campaigns_data = pd.DataFrame({
    'Campaign': [
        'TT_FitnessEnth_Video_Preworkout_001',
        'FB_Athletes_Image_Preworkout_002',
        'Google_FitnessEnth_Display_Preworkout_001',
        'FB_FitnessEnth_Carousel_WeightLoss_001'
    ],
    'Platform': ['TikTok', 'Facebook', 'Google', 'Facebook'],
    'Spend ($)': [498164, 384729, 357224, 591993],
    'Revenue ($)': [291248, 228793, 227519, 450369],
    'ROAS': [0.5846, 0.5947, 0.6369, 0.7608],
    'Action': ['❌ Eliminate', '❌ Eliminate', '❌ Eliminate', '⚠️ Reduce 50%'],
    'Reason': [
        'Preworkout + Fitness Enthusiasts — worst combination',
        'Image creative + Preworkout — double underperformer',
        'Display on Google underperforms Search consistently',
        'WeightLoss product below break-even'
    ]
})
st.dataframe(campaigns_data, use_container_width=True, hide_index=True)

# ── SECTION 4: A/B TESTS ─────────────────────────────────────────────────────
st.header("3b. Testing Recommendations — 3 A/B Tests")

tab1, tab2, tab3 = st.tabs(["Test 1: Video Length", "Test 2: Audience Targeting", "Test 3: Competitive Bidding"])

with tab1:
    st.subheader("A/B Test 1 — Video Ad Length vs Conversion Rate")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Hypothesis**
        
        Video ads achieve ROAS 0.98 despite consuming 49% of budget. 
        The weak negative correlation between VCR (Video Completion Rate) and CVR 
        (Conversion Rate, r = -0.18) suggests longer videos that get high completion 
        rates are not converting better. We hypothesize that shorter videos 
        (under 15 seconds) with a strong call-to-action in the first 5 seconds 
        will outperform current longer-form video content.

        **Hypothesis statement:**  
        *Reducing video ad length from 30s to 15s will increase CVR by at least 15% 
        while maintaining or improving VCR.*
        """)
    with col2:
        st.markdown("""
        **Test Design**
        - **Control:** Current video creative (30s format), all platforms
        - **Variant:** New 15s video with CTA in first 5 seconds
        - **Split:** 50/50 traffic split per platform
        - **Duration:** 4 weeks minimum (to reach statistical significance)
        - **Budget:** $200K total ($100K per variant)
        - **Platforms:** TikTok and Facebook (highest video spend)
        
        **Success Metrics**
        - Primary: CVR (Conversion Rate) — target +15% lift
        - Secondary: ROAS — target improve from 0.98 to 1.10+
        - Guardrail: VCR must not drop below 50%
        
        **Statistical approach:** Two-sample t-test on daily CVR, α = 0.05, 
        minimum detectable effect = 0.003 (15% relative lift on 0.027 baseline)
        
        **Expected impact:** If successful, applying to full video budget 
        ($2.17M) at +15% CVR improvement would generate ~$320K additional revenue
        """)

with tab2:
    st.subheader("A/B Test 2 — Fitness Enthusiasts vs Athletes Audience Targeting")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Hypothesis**
        
        Fitness Enthusiasts is the worst-performing audience segment (ROAS 0.67) 
        receiving 33% of total budget ($1.45M). Athletes achieve ROAS 1.11 on the 
        same products and platforms. We hypothesize that Fitness Enthusiast campaigns 
        are targeting too broad an audience and that shifting to lookalike audiences 
        modeled on the Athletes segment will improve conversion rates.
        
        **Hypothesis statement:**  
        *Replacing Fitness Enthusiast broad targeting with Athletes-lookalike audiences 
        will improve ROAS from 0.67 to at least 0.90 within 30 days.*
        """)
    with col2:
        st.markdown("""
        **Test Design**
        - **Control:** Current Fitness Enthusiast broad targeting on Facebook and TikTok
        - **Variant:** Custom lookalike audience built from Athletes converters (top 2%)
        - **Split:** 50/50 budget split within Fitness Enthusiast campaigns
        - **Duration:** 4 weeks (allow 1-week learning phase before measuring)
        - **Budget:** $150K total ($75K per variant)
        
        **Success Metrics**
        - Primary: ROAS — target improve from 0.67 to 0.90+
        - Secondary: CPP (Cost Per Purchase) — target reduce from $89.76 to under $75
        - Guardrail: Impressions must not drop below 70% of control (reach check)
        
        **Expected impact:** $1.45M Fitness Enthusiast budget at ROAS 0.90 
        (vs current 0.67) would recover approximately $333K in lost revenue
        """)

with tab3:
    st.subheader("A/B Test 3 — Competitive Event Bidding Strategy")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Hypothesis**
        
        ROAS drops significantly during competitive events (0.836 vs 0.959 normal, 
        p = 0.005). Currently the brand maintains normal bidding during these periods, 
        leading to overpaying for impressions in a crowded auction. We hypothesize 
        that reducing bids by 20-30% during identified competitive event windows 
        will protect margins while minimally impacting volume.
        
        **Hypothesis statement:**  
        *Reducing target CPA bids by 25% during competitive events will improve 
        ROAS from 0.836 to at least 0.90 without reducing monthly purchase volume 
        by more than 10%.*
        """)
    with col2:
        st.markdown("""
        **Test Design**
        - **Control:** Maintain current bidding strategy during next competitive event
        - **Variant:** Reduce target CPA bids by 25% for all campaigns during the event
        - **Split:** 50/50 campaign split (matched pairs by platform and product)
        - **Duration:** Full duration of the next competitive event window
        - **Budget:** Use existing budget — this is a bidding strategy test, not spend test
        
        **Success Metrics**
        - Primary: ROAS during event period — target 0.90+
        - Secondary: CPM (Cost Per Mille) — expect reduction due to lower bids
        - Guardrail: Total purchase volume must stay within 10% of control
        
        **Expected impact:** 4 competitive event days identified in the dataset. 
        Across $183K spent in these windows, recovering ROAS from 0.84 to 0.90 
        generates approximately $11K. More importantly, this builds a replicable 
        playbook for future competitive periods.
        """)

# ── SECTION 5: LONG-TERM STRATEGY ────────────────────────────────────────────
st.header("3c. Long-Term Strategy")

st.subheader("Regional Budget Allocation")

col1, col2 = st.columns(2)

with col1:
    regions = ['Northeast', 'West', 'South', 'Midwest']
    current_share = [26.51, 25.89, 25.41, 22.19]
    recommended_share = [32, 27, 24, 17]

    fig_region = go.Figure(data=[
        go.Bar(name='Current %', x=regions, y=current_share,
               marker_color='#3266ad', text=[f"{v}%" for v in current_share], textposition='outside'),
        go.Bar(name='Recommended %', x=regions, y=recommended_share,
               marker_color='#1D9E75', text=[f"{v}%" for v in recommended_share], textposition='outside')
    ])
    fig_region.update_layout(
        title="Regional Budget: Current vs Recommended",
        barmode='group', yaxis_title="Budget Share (%)",
        height=380
    )
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.markdown("""
    **Regional strategy rationale:**
    
    **Northeast (+5.5pp):** Best ROAS (1.04), only region above break-even consistently. 
    Increase from 26.5% to 32% of budget.
    
    **West (+1.1pp):** Second best ROAS (0.96), stable performer. 
    Slight increase from 25.9% to 27%.
    
    **South (-1.4pp):** Similar ROAS to West (0.95) but no significant difference. 
    Maintain near current level, reduce slightly from 25.4% to 24%.
    
    **Midwest (-5.2pp):** Significantly underperforms all regions (ROAS 0.84, p < 0.0001). 
    Reduce from 22.2% to 17%. Saved budget redirected to Northeast.
    """)

st.subheader("Creative Strategy by Platform")
creative_strategy = pd.DataFrame({
    'Platform': ['Facebook', 'Google', 'TikTok'],
    'Primary Creative': ['Video (15s)', 'Search', 'Video (15s)'],
    'Secondary Creative': ['Carousel', 'Display (reduced)', 'Carousel'],
    'Eliminate': ['Image', 'Image', 'Display'],
    'Rationale': [
        'Facebook users respond to visual storytelling; Search not available. Carousel for retargeting.',
        'Search dominates ROAS (1.29). Display underperforms across all regions.',
        'TikTok is a native video platform — short-form video is the format. Carousel as secondary.'
    ]
})
st.dataframe(creative_strategy, use_container_width=True, hide_index=True)

st.subheader("Audience and Product Targeting Priorities")
priority_matrix = pd.DataFrame({
    'Priority': ['🟢 Scale Up', '🟢 Scale Up', '🟡 Maintain', '🟡 Test & Learn', '🔴 Reduce', '🔴 Reduce'],
    'Segment': ['Protein + Athletes', 'Diet + Weight Loss audience', 'Protein + Weight Loss audience', 'Diet + Athletes', 'Preworkout (all audiences)', 'All products + Fitness Enthusiasts'],
    'Current ROAS': ['1.27 / 1.11', '1.07 / 1.07', '1.27 / 1.07', '1.07 / 1.11', '0.60', '0.67'],
    'Action': [
        'Increase budget 25-30%; best ROAS combination',
        'Strong profitability; scale carefully',
        'Near target; optimize creative before scaling',
        'Emerging combination; test with controlled budget',
        'Cut 60% immediately; $99 CPP is unsustainable',
        'Audience delivers 0.67 ROAS on every product — restructure targeting'
    ]
})
st.dataframe(priority_matrix, use_container_width=True, hide_index=True)

st.subheader("Quarterly Planning Approach with Competitive Events")
st.markdown("""
**Q2 Planning Framework:**

1. **Competitive event calendar:** Map known competitor promotion windows (holidays, product launches) 
   and pre-set bid reduction rules (25% CPA bid reduction) 2 weeks in advance.

2. **Weekly ROAS gates:** If weekly ROAS drops below 0.80 for any platform, trigger automatic 
   15% spend reduction on that platform. If ROAS exceeds 1.1, approve 10% spend increase.

3. **Monthly creative refresh:** Replace bottom 20% performing creatives monthly to combat 
   audience fatigue — the key driver of the 67% ROAS decline seen in Q1.

4. **Quarterly budget review:** Reallocate based on trailing 4-week ROAS by platform, region, 
   product, and audience. No budget remains locked to a segment that falls below ROAS 0.85 
   for 2 consecutive weeks.

5. **LTV (Lifetime Value) weighting:** Incorporate Customer LTV into bidding decisions — 
   Google acquires customers with higher LTV which may justify a lower short-term ROAS threshold.
""")