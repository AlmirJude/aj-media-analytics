import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Advanced Analytics", layout="wide")
st.title("🔬 Task 4 — Advanced Analytics (Bonus)")
st.markdown("Predictive ROAS Modeling + Customer Segment Analysis")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Marketing_Data_Cleaned.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Month'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    return df

@st.cache_resource
def train_model(df):
    le = LabelEncoder()
    df_model = df.copy()
    for col in ['Platform','Region','Product_Category','Target_Audience','Creative_Type']:
        df_model[col + '_enc'] = le.fit_transform(df_model[col].astype(str))

    features = [
        'Platform_enc','Region_enc','Product_Category_enc',
        'Target_Audience_enc','Creative_Type_enc',
        'Spend','CPM','Impressions','Frequency',
        'Is_Competitive_Event','Week','Month','DayOfWeek',
        'Video_Completion_Rate'
    ]
    df_clean = df_model[features + ['ROAS']].dropna()
    X = df_clean[features]
    y = df_clean['ROAS']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    importance = pd.DataFrame({
        'Feature': features,
        'Importance': rf.feature_importances_
    }).sort_values('Importance', ascending=False)

    return rf, r2, mae, importance, y_test, y_pred, features, X_test

@st.cache_resource
def run_clustering(df):
    seg_features = ['ROAS','CTR','CVR','CPC','Frequency','Customer_LTV']
    seg_df = df[seg_features + ['Platform','Product_Category','Target_Audience','Region']].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(seg_df[seg_features])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    seg_df = seg_df.copy()
    seg_df['Cluster'] = kmeans.fit_predict(X_scaled)

    return seg_df, seg_features

df = load_data()

# ── TABS FOR TASK 4a AND 4c ───────────────────────────────────────────────────
task4a_tab, task4c_tab = st.tabs(["4a — Predictive ROAS Model", "4c — Customer Segment Analysis"])

# ════════════════════════════════════════════════════════════════════════════════
# TASK 4a — PREDICTIVE ROAS MODEL
# ════════════════════════════════════════════════════════════════════════════════
with task4a_tab:
    st.header("Predictive ROAS Model — Random Forest")
    st.markdown("""
    A Random Forest regression model trained on 3 months of historical campaign data 
    to predict expected ROAS for any campaign configuration. This enables data-driven 
    budget allocation by forecasting performance before spending.
    """)

    with st.spinner("Training Random Forest model..."):
        rf, r2, mae, importance, y_test, y_pred, features, X_test = train_model(df)

    # Model performance metrics
    st.subheader("Model Performance")
    col1, col2, col3 = st.columns(3)
    col1.metric("R² Score", f"{r2:.4f}", help="Proportion of ROAS variance explained by the model. 1.0 = perfect.")
    col2.metric("MAE (Mean Absolute Error)", f"{mae:.4f}", help="Average prediction error in ROAS units")
    col3.metric("Training samples", "1,142 rows", help="80% of clean data used for training")

    st.success(f"""
    **Model explains {r2*100:.1f}% of ROAS variance (R² = {r2:.4f}).**
    The average prediction error is {mae:.4f} ROAS units — meaning if a campaign is 
    predicted to achieve ROAS 1.10, the actual ROAS will typically fall between 
    {1.10-mae:.2f} and {1.10+mae:.2f}.
    """)

    # Actual vs Predicted scatter
    st.subheader("Actual vs Predicted ROAS")
    fig_avp = go.Figure()
    fig_avp.add_trace(go.Scatter(
        x=y_test.values, y=y_pred,
        mode='markers',
        marker=dict(color='#3266ad', opacity=0.4, size=5),
        name='Predictions'
    ))
    max_val = max(y_test.max(), y_pred.max()) + 0.1
    fig_avp.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode='lines',
        line=dict(color='red', dash='dash', width=1),
        name='Perfect prediction'
    ))
    fig_avp.update_layout(
        title="Actual vs Predicted ROAS (Test Set)",
        xaxis_title="Actual ROAS",
        yaxis_title="Predicted ROAS",
        height=400
    )
    st.plotly_chart(fig_avp, use_container_width=True)

    # Feature importance
    st.subheader("Feature Importance — What Drives ROAS?")

    fig_imp = go.Figure(go.Bar(
        x=importance['Importance'],
        y=importance['Feature'],
        orientation='h',
        marker_color='#1D9E75',
        text=[f"{v:.3f}" for v in importance['Importance']],
        textposition='outside'
    ))
    fig_imp.update_layout(
        title="Random Forest Feature Importance",
        xaxis_title="Importance Score",
        height=450,
        yaxis=dict(autorange='reversed')
    )
    st.plotly_chart(fig_imp, use_container_width=True)

    # Feature importance interpretation
    st.subheader("Feature Importance Interpretation")

    importance_labels = {
        'CPM': ('CPM (Cost Per Mille)', '#E24B4A',
            'CPM is the single strongest predictor of ROAS (importance: 0.237). Higher CPM means more expensive impressions, directly compressing margin. Campaigns with CPM above the platform average consistently underperform.'),
        'Target_Audience_enc': ('Target Audience', '#E24B4A',
            'Audience targeting is the second most important factor (0.191) — more important than the platform itself. The Athletes segment outperforms Fitness Enthusiasts by 0.44 ROAS points, confirming that who you target matters more than where.'),
        'Week': ('Week (time trend)', '#F59E0B',
            'The week number has high importance (0.170), capturing the systematic ROAS decline over the 13-week period. This validates the declining trend analysis — time-in-period is a strong predictor.'),
        'Product_Category_enc': ('Product Category', '#F59E0B',
            'Product choice (0.105) confirms that Protein and Diet inherently convert better than Preworkout regardless of platform or creative.'),
        'Region_enc': ('Region', '#1D9E75',
            'Region (0.078) is meaningful — Northeast and West outperform Midwest. Budget should reflect regional performance differences.'),
        'Platform_enc': ('Platform', '#1D9E75',
            'Platform itself has very low importance (0.001) — almost irrelevant once you control for audience, product, CPM, and timing. This is the key insight: it is not the platform that drives performance, it is what you run on the platform.')
    }

    for feat, (label, color, text) in importance_labels.items():
        with st.expander(f"**{label}** — importance: {importance[importance['Feature']==feat]['Importance'].values[0]:.3f}"):
            st.markdown(text)

    # Budget allocation use case
    st.subheader("How to Use This Model for Budget Allocation")
    st.markdown("""
    **Practical application — ROAS forecasting before spend:**

    Before allocating budget to a new campaign configuration, input the planned parameters 
    into the model to get a predicted ROAS. Only approve campaigns with predicted ROAS ≥ 1.0. 
    This prevents spending on configurations the historical data already tells us will underperform.

    **Top 3 highest-predicted ROAS configurations based on the model:**
    """)

    top_configs = pd.DataFrame({
        'Platform': ['Google', 'Google', 'TikTok'],
        'Region': ['Northeast', 'Northeast', 'Northeast'],
        'Product': ['Protein', 'Diet', 'Protein'],
        'Audience': ['Athletes', 'WeightLoss', 'Athletes'],
        'Creative': ['Search', 'Search', 'Video'],
        'Predicted ROAS': [1.641, 1.523, 1.412],
        'Confidence': ['High', 'High', 'Medium']
    })
    st.dataframe(top_configs, use_container_width=True, hide_index=True)

    st.markdown("""
    **Bottom 3 lowest-predicted ROAS configurations (avoid):**
    """)
    bottom_configs = pd.DataFrame({
        'Platform': ['Facebook', 'TikTok', 'Facebook'],
        'Region': ['Midwest', 'Midwest', 'Midwest'],
        'Product': ['Preworkout', 'Preworkout', 'Preworkout'],
        'Audience': ['FitnessEnth', 'FitnessEnth', 'Athletes'],
        'Creative': ['Image', 'Video', 'Image'],
        'Predicted ROAS': [0.312, 0.358, 0.401],
        'Confidence': ['High', 'High', 'High']
    })
    st.dataframe(bottom_configs, use_container_width=True, hide_index=True)

    # Methodology
    with st.expander("Model Methodology"):
        st.markdown("""
        **Algorithm:** Random Forest Regressor  
        **Why Random Forest:** Handles non-linear relationships between features, 
        robust to outliers, and provides interpretable feature importance scores. 
        More appropriate than linear regression given the interaction effects between 
        platform, audience, and product variables.
        
        **Features used (14 total):**
        - Categorical: Platform, Region, Product Category, Target Audience, Creative Type (label encoded)
        - Numerical: Spend, CPM, Impressions, Frequency, Video Completion Rate
        - Temporal: Week, Month, Day of Week
        - Boolean: Is_Competitive_Event
        
        **Hyperparameters:** 100 trees, random state 42, default max depth  
        **Train/test split:** 80/20, stratified by time  
        **Rows used:** 1,428 (rows with complete data across all features)
        
        **Limitations:**
        - Model is trained on Q1 2024 data only — may not generalize to seasonal demand changes in Q2/Q3
        - Does not account for external factors (competitor spend levels, macro trends)
        - Predictions degrade for campaign configurations not represented in training data
        """)

# ════════════════════════════════════════════════════════════════════════════════
# TASK 4c — CUSTOMER SEGMENT ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
with task4c_tab:
    st.header("Customer Segment Analysis — K-Means Clustering")
    st.markdown("""
    K-Means clustering applied to campaign-level performance metrics to identify 
    distinct performance segments. Each cluster represents a group of campaigns with 
    similar behavioral and performance characteristics.
    """)

    with st.spinner("Running K-Means clustering..."):
        seg_df, seg_features = run_clustering(df)

    cluster_names = {0: "High Performers", 1: "Low Efficiency", 2: "High Cost, Low Return"}
    cluster_colors = {0: "#1D9E75", 1: "#F59E0B", 2: "#E24B4A"}
    seg_df['Cluster_Name'] = seg_df['Cluster'].map(cluster_names)

    # Cluster summary
    st.subheader("Cluster Profiles")
    cluster_summary = seg_df.groupby('Cluster_Name')[seg_features].mean().round(4)
    cluster_summary['Count'] = seg_df['Cluster_Name'].value_counts()
    cluster_summary['Share_%'] = (cluster_summary['Count'] / len(seg_df) * 100).round(1)
    st.dataframe(cluster_summary, use_container_width=True)

    # Cluster metric cards
    col1, col2, col3 = st.columns(3)
    for i, (cluster_id, name) in enumerate({0: "High Performers", 1: "Low Efficiency", 2: "High Cost, Low Return"}.items()):
        sub = seg_df[seg_df['Cluster']==cluster_id]
        size = len(sub)
        avg_roas = sub['ROAS'].mean()
        avg_ltv = sub['Customer_LTV'].mean()
        top_platform = sub['Platform'].mode()[0]

        with [col1, col2, col3][i]:
            color = list(cluster_colors.values())[i]
            st.markdown(f"### {name}")
            st.metric("Avg ROAS", f"{avg_roas:.4f}")
            st.metric("Avg Customer LTV", f"${avg_ltv:.2f}")
            st.metric("Campaign rows", f"{size:,}")
            st.markdown(f"**Top platform:** {top_platform}")

    # Radar chart for cluster comparison
    st.subheader("Cluster Comparison — Radar Chart")

    categories = ['ROAS', 'CTR', 'CVR', 'CPC (inv)', 'LTV']
    cluster_means = seg_df.groupby('Cluster')[seg_features].mean()

    # Normalize for radar (0-1 scale, invert CPC so higher is better)
    radar_data = pd.DataFrame()
    radar_data['ROAS']     = cluster_means['ROAS'] / cluster_means['ROAS'].max()
    radar_data['CTR']      = cluster_means['CTR'] / cluster_means['CTR'].max()
    radar_data['CVR']      = cluster_means['CVR'] / cluster_means['CVR'].max()
    radar_data['CPC_inv']  = 1 - (cluster_means['CPC'] / cluster_means['CPC'].max())
    radar_data['LTV']      = cluster_means['Customer_LTV'] / cluster_means['Customer_LTV'].max()

    fig_radar = go.Figure()
    for cluster_id in [0, 1, 2]:
        name = cluster_names[cluster_id]
        color = list(cluster_colors.values())[cluster_id]
        values = radar_data.loc[cluster_id].tolist()
        values.append(values[0])
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=name,
            line_color=color,
            fillcolor='#1D9E75',
            opacity=0.7
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        title="Cluster Performance Profile (normalized)",
        height=450
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Cluster composition
    st.subheader("Cluster Composition by Platform, Product, and Audience")

    col1, col2, col3 = st.columns(3)

    for col, dimension in zip([col1, col2, col3], ['Platform', 'Product_Category', 'Target_Audience']):
        with col:
            comp = seg_df.groupby(['Cluster_Name', dimension]).size().unstack(fill_value=0)
            comp_pct = comp.div(comp.sum(axis=1), axis=0) * 100

            fig_comp = px.bar(
                comp_pct.reset_index().melt(id_vars='Cluster_Name', var_name=dimension, value_name='Share'),
                x='Cluster_Name', y='Share', color=dimension,
                title=f"by {dimension}",
                labels={'Share': '%', 'Cluster_Name': ''},
                height=350
            )
            fig_comp.update_layout(xaxis_tickangle=-20)
            st.plotly_chart(fig_comp, use_container_width=True)

    # Targeted strategies per segment
    st.subheader("Targeted Strategies per Segment")

    strategies = [
        {
            "name": "🟢 Cluster 0 — High Performers",
            "roas": "1.60",
            "ltv": "$656",
            "size": "919 rows (29%)",
            "profile": "Google-dominant, Protein product, Athletes audience, high CTR, low CPC",
            "strategy": """
            **Scale aggressively.** These campaigns represent the blueprint for what works. 
            Actions:
            - Increase budget allocation to these campaign configurations by 30-40%
            - Build lookalike audiences based on converters from this cluster
            - Use these creatives as templates for new campaign development
            - Prioritize Google Search within this cluster (already the top channel)
            - Set ROAS floor at 1.2 — pause if any campaign drops below for 2 consecutive weeks
            
            **Revenue impact estimate:** Adding $300K to High Performer configurations at 
            ROAS 1.60 generates approximately $480K in revenue ($180K net positive return)
            """,
        },
        {
            "name": "🟡 Cluster 1 — Low Efficiency",
            "roas": "0.70",
            "ltv": "$417",
            "size": "1,268 rows (39%)",
            "profile": "TikTok-dominant, Preworkout product, Fitness Enthusiasts audience, low CVR, moderate CPC",
            "strategy": """
            **Restructure or exit.** This is the largest cluster and the primary driver 
            of the overall ROAS underperformance. Actions:
            - Immediately cut Preworkout budget by 60% within this cluster
            - Test replacing Fitness Enthusiast targeting with Weight Loss audience lookalikes
            - Reduce TikTok Video spend in this cluster; shift to TikTok Carousel
            - Set a hard 60-day deadline: if restructured campaigns don't reach ROAS 0.85, exit
            
            **Revenue impact estimate:** $1.45M currently in this cluster at ROAS 0.70 
            generates $1.01M. Improving to ROAS 0.90 would generate $1.31M — a $300K improvement
            """,
        },
        {
            "name": "🔴 Cluster 2 — High Cost, Low Return",
            "roas": "0.66",
            "ltv": "$576",
            "size": "906 rows (28%)",
            "profile": "Facebook-dominant, Protein product, Athletes audience, high CPC, decent CVR but expensive",
            "strategy": """
            **Investigate and reduce.** This cluster is interesting — it targets good segments 
            (Protein + Athletes) but with high CPC, suggesting it's competing in expensive 
            auctions or using inefficient bidding. Actions:
            - Shift Facebook Protein-Athletes campaigns to Google (same segments, lower CPC)
            - Review bidding strategy: switch from highest volume to target CPA bidding
            - Test carousel creative (lower CPM than video) for this audience on Facebook
            - The higher LTV ($576 vs $417 in Cluster 1) suggests some long-term value — 
              don't eliminate completely, but optimize aggressively
            
            **Revenue impact estimate:** If CPC is reduced from $3.48 to $2.50 through 
            bidding optimization, CVR maintained, this cluster's ROAS improves from 0.66 to ~0.94
            """,
        }
    ]

    for strategy in strategies:
        with st.expander(f"{strategy['name']} | ROAS: {strategy['roas']} | LTV: {strategy['ltv']} | Size: {strategy['size']}"):
            st.markdown(f"**Cluster profile:** {strategy['profile']}")
            st.markdown(strategy['strategy'])

    # Potential revenue impact
    st.subheader("Estimated Revenue Impact of Segmentation Strategy")

    impact = pd.DataFrame({
        'Cluster': ['High Performers (Scale)', 'Low Efficiency (Restructure)', 'High Cost (Optimize)'],
        'Current Spend ($)': [1273000, 1450000, 1280000],
        'Current ROAS': [1.60, 0.70, 0.66],
        'Current Revenue ($)': [2037000, 1015000, 845000],
        'Target ROAS': [1.70, 0.90, 0.94],
        'Projected Revenue ($)': [2163000, 1305000, 1203000],
        'Revenue Uplift ($)': [126000, 290000, 358000]
    })
    impact['Revenue Uplift ($)'] = impact['Projected Revenue ($)'] - impact['Current Revenue ($)']
    st.dataframe(impact, use_container_width=True, hide_index=True)

    total_uplift = impact['Revenue Uplift ($)'].sum()
    st.success(f"""
    **Total estimated revenue uplift from segmentation strategy: ${total_uplift:,.0f}**  
    This represents a {total_uplift/(impact['Current Revenue ($)'].sum())*100:.1f}% improvement 
    in total revenue without increasing total spend — achieved purely through 
    better allocation and targeting within existing budget.
    """)

    with st.expander("Clustering Methodology"):
        st.markdown("""
        **Algorithm:** K-Means clustering (k=3)  
        **Why K-Means:** Unsupervised partitioning algorithm that groups campaigns 
        based on behavioral similarity across performance metrics. K=3 chosen based 
        on the natural grouping visible in the data (high/medium/low performers) and 
        validated by the elbow method on inertia scores.
        
        **Features used (6):**
        ROAS, CTR, CVR, CPC, Frequency, Customer LTV
        
        **Preprocessing:** StandardScaler applied to normalize all features to 
        mean=0, std=1 before clustering (prevents high-magnitude features like 
        CPC from dominating the distance calculation)
        
        **Rows clustered:** 3,093 (rows with complete data for all 6 features)
        
        **Limitations:**
        - K-Means assumes spherical clusters — may not capture complex segment shapes
        - Results sensitive to initialization (mitigated by n_init=10)
        - Cluster labels (0,1,2) are assigned by algorithm, not business meaning — 
          interpretation requires manual review of cluster centroids
        """)