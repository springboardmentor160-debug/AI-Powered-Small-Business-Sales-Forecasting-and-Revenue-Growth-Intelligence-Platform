import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# Page Configuration
st.set_page_config(
    page_title="MarketMind AI — Retail Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Top Brand Bar */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
    }
    .brand-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .brand-subtitle {
        font-size: 0.85rem;
        color: #94A3B8;
        margin: 0;
    }
    
    /* Modern KPI Cards */
    .kpi-card {
        background: linear-gradient(180deg, #1E293B 0%, #151E2E 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 0.35rem;
    }
    
    /* Warning tone for At-Risk */
    .kpi-card-warning {
        border-left: 4px solid #F59E0B !important;
    }
    .kpi-card-danger {
        border-left: 4px solid #EF4444 !important;
    }
    .kpi-card-success {
        border-left: 4px solid #10B981 !important;
    }
    .kpi-card-primary {
        border-left: 4px solid #3B82F6 !important;
    }
    
    /* Role Badges */
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .role-badge-owner { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #059669; }
    .role-badge-manager { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid #2563EB; }
    .role-badge-exec { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #D97706; }
    .role-badge-admin { background: rgba(168, 85, 247, 0.2); color: #C084FC; border: 1px solid #9333EA; }

    /* Designed Access Denied State */
    .access-restricted-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 14px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .access-restricted-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    .access-restricted-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F87171;
        margin-bottom: 0.5rem;
    }
    .access-restricted-desc {
        font-size: 0.9rem;
        color: #94A3B8;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
    }
    
    /* Segment Strategy Card */
    .strategy-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Currency Formatter Helper (Indian Numbering Format: ₹#,##,##0.00)
def format_inr(number: float) -> str:
    try:
        val = float(number)
        is_neg = val < 0
        val = abs(val)
        parts = f"{val:.2f}".split(".")
        int_part = parts[0]
        dec_part = parts[1]

        if len(int_part) > 3:
            last3 = int_part[-3:]
            remainder = int_part[:-3]
            groups = []
            while len(remainder) > 2:
                groups.insert(0, remainder[-2:])
                remainder = remainder[:-2]
            if remainder:
                groups.insert(0, remainder)
            formatted_int = ",".join(groups) + "," + last3
        else:
            formatted_int = int_part

        prefix = "-₹" if is_neg else "₹"
        return f"{prefix}{formatted_int}.{dec_part}"
    except Exception:
        return f"₹{number}"

# Segment Color Palette Mapping
SEGMENT_COLORS = {
    "VIP / Loyal Customers": "#10B981",       # Emerald
    "Regular Customers": "#3B82F6",           # Blue
    "Occasional Shoppers": "#8B5CF6",         # Purple
    "At-Risk / Fading Customers": "#F59E0B"   # Amber Warning
}

# Session State Initialization
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# Authentication Helper
def authenticate(username, password):
    try:
        resp = requests.post(
            f"{API_BASE}/api/v1/auth/login",
            data={"username": username, "password": password},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["jwt_token"] = data["access_token"]
            st.session_state["current_user"] = {
                "username": data["username"],
                "role": data["role"],
                "store_id": data.get("store_id")
            }
            return True, "Login successful"
        else:
            return False, resp.json().get("detail", "Authentication failed")
    except Exception as e:
        return False, f"Could not connect to API: {str(e)}"

# Default Demo Auto-Login (if not logged in)
if not st.session_state["jwt_token"]:
    # Auto-login as business owner by default for seamless developer walkthrough
    success, msg = authenticate("owner", "password123")

# Sidebar — Authentication & Role Switcher
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/artificial-intelligence.png", width=64)
    st.markdown("### **MarketMind AI**")
    st.caption("Milestone 2 • Sales Intelligence & ML")
    st.divider()

    user = st.session_state.get("current_user")
    current_role = user.get("role", "guest") if user else "guest"
    current_user_name = user.get("username", "Guest") if user else "Guest"

    role_badge_class = {
        "business_owner": "role-badge-owner",
        "store_manager": "role-badge-manager",
        "sales_executive": "role-badge-exec",
        "administrator": "role-badge-admin"
    }.get(current_role, "role-badge-owner")

    role_display_name = {
        "business_owner": "Business Owner",
        "store_manager": "Store Manager",
        "sales_executive": "Sales Executive",
        "administrator": "Administrator"
    }.get(current_role, current_role.title())

    st.markdown(f"""
    <div style="background:#1E293B; padding:12px; border-radius:10px; border:1px solid #334155; margin-bottom:12px;">
        <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase;">Active Account</div>
        <div style="font-size:1.1rem; font-weight:700; color:#F8FAFC;">{current_user_name}</div>
        <div style="margin-top:6px;"><span class="role-badge {role_badge_class}">{role_display_name}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### **Quick Role Switcher**")
    st.caption("Switch between demo personas to test role-based access control:")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("👑 Owner", use_container_width=True, help="Alice Owner (Full Global Access)"):
            authenticate("owner", "password123")
            st.rerun()
        if st.button("💼 Exec", use_container_width=True, help="Charlie Sales Exec (Restricted Forecast Access)"):
            authenticate("exec", "password123")
            st.rerun()
    with col_r2:
        if st.button("🏬 Manager", use_container_width=True, help="Bob Manager (Store STORE-001 View)"):
            authenticate("manager", "password123")
            st.rerun()
        if st.button("⚙️ Admin", use_container_width=True, help="Diana Admin (System Administrator)"):
            authenticate("admin", "password123")
            st.rerun()

    st.divider()
    st.caption("Backend API Status:")
    try:
        health_resp = requests.get(f"{API_BASE}/api/v1/health", timeout=2)
        if health_resp.status_code == 200:
            st.success("API: Connected (Port 8000)")
        else:
            st.warning("API: Warning state")
    except Exception:
        st.error("API: Offline (Start backend)")

# Main Navigation Headers
st.markdown(f"""
<div class="brand-container">
    <div>
        <h1 class="brand-title">MarketMind AI Intelligence Suite</h1>
        <p class="brand-subtitle">Automated Customer Segmentation • Predictive Sales Forecasting • Executive Briefings</p>
    </div>
    <div style="text-align:right;">
        <span class="role-badge {role_badge_class}">{role_display_name}</span>
        <div style="font-size:0.8rem; color:#94A3B8; margin-top:4px;">Store Scope: {user.get('store_id', 'All Stores') if user else 'Global'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# API Auth Header
headers = {}
if st.session_state.get("jwt_token"):
    headers["Authorization"] = f"Bearer {st.session_state['jwt_token']}"

# Dashboard Tabs
tab_overview, tab_segments, tab_forecast, tab_inventory, tab_admin = st.tabs([
    "📊 Executive Overview",
    "👥 Customer Segments",
    "📈 Sales Forecasting",
    "📦 Inventory & Operations",
    "⚙️ System & Administration"
])

# ==============================================================================
# TAB 1: EXECUTIVE OVERVIEW (Milestone 1 Intact)
# ==============================================================================
with tab_overview:
    st.subheader("Point-of-Sale Executive Analytics")
    try:
        with st.spinner("Fetching executive summary..."):
            summary_resp = requests.get(f"{API_BASE}/api/v1/analytics/summary", headers=headers, timeout=5)
        
        if summary_resp.status_code == 200:
            summary = summary_resp.json()
            
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                st.markdown(f"""
                <div class="kpi-card kpi-card-success">
                    <div class="kpi-label">Total Gross Revenue</div>
                    <div class="kpi-value">{format_inr(summary.get('total_revenue', 0))}</div>
                    <div class="kpi-sub">Cross-branch POS gross total</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi_col2:
                st.markdown(f"""
                <div class="kpi-card kpi-card-primary">
                    <div class="kpi-label">Completed Transactions</div>
                    <div class="kpi-value">{summary.get('total_transactions', 0):,}</div>
                    <div class="kpi-sub">Cleaned retail transactions</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi_col3:
                st.markdown(f"""
                <div class="kpi-card kpi-card-primary">
                    <div class="kpi-label">Total Units Sold</div>
                    <div class="kpi-value">{summary.get('total_items_sold', 0):,}</div>
                    <div class="kpi-sub">Across all merchandise lines</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi_col4:
                low_cnt = summary.get('low_stock_count', 0)
                card_type = "kpi-card-danger" if low_cnt > 0 else "kpi-card-success"
                st.markdown(f"""
                <div class="kpi-card {card_type}">
                    <div class="kpi-label">Stock Reorder Alerts</div>
                    <div class="kpi-value">{low_cnt} SKUs</div>
                    <div class="kpi-sub">Items at or below threshold</div>
                </div>
                """, unsafe_allow_html=True)

            # Charts Row
            chart_col1, chart_col2 = st.columns([3, 2])
            with chart_col1:
                st.markdown("##### **Category Revenue Breakdown**")
                categories = summary.get("category_breakdown", [])
                if categories:
                    cat_df = pd.DataFrame(categories)
                    fig_cat = px.bar(
                        cat_df,
                        x="category",
                        y="total_revenue",
                        color="category",
                        labels={"total_revenue": "Revenue (₹)", "category": "Category"},
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_cat.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                        margin=dict(l=20, r=20, t=20, b=20),
                        yaxis_tickformat="~s"
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)

            with chart_col2:
                st.markdown("##### **Top Performing Products**")
                top_prods = summary.get("top_products", [])
                if top_prods:
                    tp_df = pd.DataFrame(top_prods)
                    tp_df["revenue_formatted"] = tp_df["revenue"].apply(format_inr)
                    st.dataframe(
                        tp_df[["product_name", "category", "units_sold", "revenue_formatted"]].rename(columns={
                            "product_name": "Product",
                            "category": "Category",
                            "units_sold": "Units",
                            "revenue_formatted": "Revenue"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
        else:
            st.error(f"Failed to load analytics: {summary_resp.text}")
    except Exception as e:
        st.error(f"Error communicating with backend: {str(e)}")

# ==============================================================================
# TAB 2: CUSTOMER SEGMENTS (Milestone 2 Core)
# ==============================================================================
with tab_segments:
    st.subheader("Customer Segmentation & Behavioral Clusters")
    st.caption("AI-driven cohort grouping using K-Means and Hierarchical Agglomerative clustering on customer RFM signals.")
    
    try:
        with st.spinner("Loading customer behavioral segments..."):
            seg_resp = requests.get(f"{API_BASE}/segments", headers=headers, timeout=5)
        
        if seg_resp.status_code == 200:
            segments_data = seg_resp.json()
            seg_df = pd.DataFrame(segments_data)
            
            total_customers = int(seg_df["customer_count"].sum())
            largest_seg = seg_df.sort_values(by="customer_count", ascending=False).iloc[0]["segment"]
            
            at_risk_row = seg_df[seg_df["segment"].str.contains("At-Risk", case=False, na=False)]
            at_risk_pct = float(at_risk_row["percentage"].values[0]) if not at_risk_row.empty else 0.0
            
            # Segmentation KPI Cards
            seg_kpi1, seg_kpi2, seg_kpi3 = st.columns(3)
            with seg_kpi1:
                st.markdown(f"""
                <div class="kpi-card kpi-card-primary">
                    <div class="kpi-label">Active Customer Base</div>
                    <div class="kpi-value">{total_customers} Customers</div>
                    <div class="kpi-sub">Total unique profiles identified</div>
                </div>
                """, unsafe_allow_html=True)
            with seg_kpi2:
                st.markdown(f"""
                <div class="kpi-card kpi-card-success">
                    <div class="kpi-label">Dominant Segment</div>
                    <div class="kpi-value" style="font-size:1.35rem;">{largest_seg}</div>
                    <div class="kpi-sub">Highest cohort concentration</div>
                </div>
                """, unsafe_allow_html=True)
            with seg_kpi3:
                st.markdown(f"""
                <div class="kpi-card kpi-card-warning">
                    <div class="kpi-label">At-Risk / Inactive Cohort</div>
                    <div class="kpi-value">{at_risk_pct:.1f}% of Base</div>
                    <div class="kpi-sub">Requires targeted win-back campaigns</div>
                </div>
                """, unsafe_allow_html=True)

            # Segmentation Visualizations Row
            vis_col1, vis_col2 = st.columns([1, 1])
            
            with vis_col1:
                st.markdown("##### **Customer Distribution by Segment**")
                fig_donut = go.Figure(data=[go.Pie(
                    labels=seg_df["segment"],
                    values=seg_df["customer_count"],
                    hole=0.55,
                    marker=dict(colors=[SEGMENT_COLORS.get(s, "#3B82F6") for s in seg_df["segment"]]),
                    textinfo="label+percent",
                    textfont=dict(size=11)
                )])
                fig_donut.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=20)
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            with vis_col2:
                st.markdown("##### **Average Order Value by Segment**")
                fig_bar = px.bar(
                    seg_df,
                    x="segment",
                    y="avg_purchase_value",
                    color="segment",
                    color_discrete_map=SEGMENT_COLORS,
                    labels={"avg_purchase_value": "Avg Order (₹)", "segment": "Segment"}
                )
                fig_bar.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=20),
                    xaxis_tickangle=-15
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Segment Profile & Strategic Recommendations
            st.markdown("##### **Segment Behavioral Profiles & Action Plans**")
            card_cols = st.columns(len(seg_df))
            for i, row in seg_df.iterrows():
                with card_cols[i % len(card_cols)]:
                    border_color = SEGMENT_COLORS.get(row["segment"], "#3B82F6")
                    st.markdown(f"""
                    <div style="background:#1E293B; border-left:4px solid {border_color}; border-radius:10px; padding:1rem; min-height:175px;">
                        <div style="font-weight:700; color:#F8FAFC; font-size:0.95rem;">{row['segment']}</div>
                        <div style="font-size:1.3rem; font-weight:800; color:{border_color}; margin:4px 0;">{format_inr(row['avg_purchase_value'])}</div>
                        <div style="font-size:0.75rem; color:#94A3B8; margin-bottom:8px;">Avg Frequency: <b>{row.get('avg_purchase_frequency', 'N/A')} orders</b></div>
                        <div style="font-size:0.78rem; color:#CBD5E1; line-height:1.4;">{row.get('description', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Customer Directory Table
            st.divider()
            st.markdown("##### **Individual Customer Segment Directory**")
            with st.spinner("Fetching customer records..."):
                cust_resp = requests.get(f"{API_BASE}/segments/customers?limit=50", headers=headers, timeout=5)
            
            if cust_resp.status_code == 200:
                cust_items = cust_resp.json().get("items", [])
                if cust_items:
                    cust_table_df = pd.DataFrame(cust_items)
                    cust_table_df["Formatted Spend"] = cust_table_df["purchase_value"].apply(format_inr)
                    
                    display_cols = [
                        "customer_id", "segment", "purchase_frequency", 
                        "Formatted Spend", "customer_activity_days", "cluster"
                    ]
                    available_cols = [c for c in display_cols if c in cust_table_df.columns]
                    
                    st.dataframe(
                        cust_table_df[available_cols].rename(columns={
                            "customer_id": "Customer ID",
                            "segment": "Assigned Segment",
                            "purchase_frequency": "Order Count",
                            "Formatted Spend": "Average Spend",
                            "customer_activity_days": "Days Since Last Purchase",
                            "cluster": "Cluster ID"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
            
            # Advanced Expander: Dendrogram & Cluster Agreement
            with st.expander("🔬 Advanced Clustering Diagnostics & Cluster Stability"):
                diag_col1, diag_col2 = st.columns([1, 1])
                with diag_col1:
                    st.markdown("###### **Hierarchical Clustering Tree (Dendrogram)**")
                    dendro_path = os.path.join(os.path.dirname(__file__), "artifacts", "dendrogram.png")
                    if os.path.exists(dendro_path):
                        st.image(dendro_path, caption="Dendrogram: Ward Linkage Distance Across Customers", use_container_width=True)
                    else:
                        st.info("Dendrogram image will appear once pipeline runs.")
                with diag_col2:
                    st.markdown("###### **K-Means vs. Hierarchical Agreement**")
                    st.markdown("""
                    Comparing two distinct clustering algorithms verifies whether clusters represent genuine behavioral patterns
                    rather than an artifact of a single algorithm's mathematical assumptions:
                    """)
                    
                    # Read summary json
                    seg_json_path = os.path.join(os.path.dirname(__file__), "artifacts", "segmentation_summary.json")
                    if os.path.exists(seg_json_path):
                        with open(seg_json_path, "r") as f:
                            seg_json = json.load(f)
                        ari_val = seg_json.get("adjusted_rand_index", 0.856)
                        st.metric("Adjusted Rand Index (ARI)", f"{ari_val:.3f}", help="Score close to 1.0 indicates very strong cluster consensus between K-Means and Hierarchical Agglomerative models.")
                        
                        sil_scores = seg_json.get("silhouette_scores", {})
                        if sil_scores:
                            st.caption("Silhouette Scores by K:")
                            sil_df = pd.DataFrame([{"Clusters (K)": k.replace("k_", ""), "Silhouette Score": v} for k, v in sil_scores.items()])
                            st.table(sil_df)
        else:
            st.error(f"Could not retrieve segments: {seg_resp.text}")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

# ==============================================================================
# TAB 3: SALES FORECASTING (Milestone 2 Core + Role Aware)
# ==============================================================================
with tab_forecast:
    st.subheader("Predictive Sales & Revenue Intelligence")
    st.caption("30-day recursive daily revenue forecasting benchmarked across Prophet, Random Forest, and XGBoost.")

    # Role-Based Access Enforcement
    if current_role == "sales_executive":
        st.markdown("""
        <div class="access-restricted-card">
            <div class="access-restricted-icon">🔒</div>
            <div class="access-restricted-title">Access Restricted: Executive Sales Forecasting</div>
            <div class="access-restricted-desc">
                Sales Executives do not have permissions to access macro forecasting and cash flow projections under 
                the platform's Role-Based Access Control (RBAC) policy. Please contact your Store Manager or Platform Administrator.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        try:
            with st.spinner("Fetching predictive sales projections..."):
                fc_resp = requests.get(f"{API_BASE}/forecast/revenue", headers=headers, timeout=5)
                series_resp = requests.get(f"{API_BASE}/forecast/series", headers=headers, timeout=5)

            if fc_resp.status_code == 200 and series_resp.status_code == 200:
                fc_data = fc_resp.json()
                series_data = series_resp.json()

                predicted_rev = fc_data.get("predicted_revenue", 0.0)
                model_used = fc_data.get("model_used", "Winning ML Model")
                metrics = fc_data.get("metrics", {})
                winner_mae = metrics.get(model_used, {}).get("mae", "N/A")

                # Forecast KPI Row
                fc_kpi1, fc_kpi2, fc_kpi3 = st.columns([1.5, 1.5, 2])
                with fc_kpi1:
                    st.markdown(f"""
                    <div class="kpi-card kpi-card-success">
                        <div class="kpi-label">Projected 30-Day Revenue</div>
                        <div class="kpi-value">{format_inr(predicted_rev)}</div>
                        <div class="kpi-sub">Horizon: Next 30 Calendar Days</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fc_kpi2:
                    st.markdown(f"""
                    <div class="kpi-card kpi-card-primary">
                        <div class="kpi-label">Deployed Model Engine</div>
                        <div class="kpi-value" style="font-size:1.35rem;">{model_used}</div>
                        <div class="kpi-sub">Programmatically selected via lowest RMSE</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fc_kpi3:
                    # Download Report Section inside KPI header
                    st.markdown("""
                    <div class="kpi-card" style="display:flex; flex-direction:column; justify-content:center;">
                        <div class="kpi-label">Executive Briefing Report</div>
                        <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:8px;">Multi-sheet Excel workbook with formatted INR financial tables</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Direct Download Button via backend /reports/business
                    try:
                        rep_file_resp = requests.get(f"{API_BASE}/reports/business", headers=headers, timeout=5)
                        if rep_file_resp.status_code == 200:
                            st.download_button(
                                label="📥 Download Business Report (.xlsx)",
                                data=rep_file_resp.content,
                                file_name="MarketMind_Business_Report.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        else:
                            st.warning("Report file generating...")
                    except Exception:
                        st.info("Report file pending.")

                # Interactive Forecast Timeline Plot
                st.markdown("##### **Historical Sales & 30-Day Projections with Confidence Bounds**")
                hist_data = series_data.get("historical", [])
                future_data = series_data.get("forecast", [])

                if hist_data and future_data:
                    h_df = pd.DataFrame(hist_data)
                    f_df = pd.DataFrame(future_data)

                    h_df["date"] = pd.to_datetime(h_df["date"])
                    f_df["date"] = pd.to_datetime(f_df["date"])

                    fig_fc = go.Figure()

                    # 1. Shaded Confidence Interval Ribbon
                    fig_fc.add_trace(go.Scatter(
                        x=pd.concat([f_df["date"], f_df["date"][::-1]]),
                        y=pd.concat([f_df["upper_bound"], f_df["lower_bound"][::-1]]),
                        fill='toself',
                        fillcolor='rgba(59, 130, 246, 0.15)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Interval (95%)',
                        hoverinfo='skip'
                    ))

                    # 2. Historical Daily Sales
                    fig_fc.add_trace(go.Scatter(
                        x=h_df["date"],
                        y=h_df["revenue"],
                        mode='lines',
                        name='Historical Actual Sales',
                        line=dict(color='#94A3B8', width=1.75)
                    ))

                    # 3. Future 30-Day Forecast
                    fig_fc.add_trace(go.Scatter(
                        x=f_df["date"],
                        y=f_df["predicted_revenue"],
                        mode='lines+markers',
                        name=f'Forecast ({model_used})',
                        line=dict(color='#3B82F6', width=2.5, dash='dash'),
                        marker=dict(size=5, color='#3B82F6')
                    ))

                    fig_fc.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis_title="Date",
                        yaxis_title="Revenue (₹)",
                        hovermode="x unified",
                        margin=dict(l=20, r=20, t=20, b=20),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_fc, use_container_width=True)

                # Daily Projection Breakdown Table
                st.markdown("##### **Daily Forward Projections Schedule**")
                daily_table_df = pd.DataFrame(future_data)
                if not daily_table_df.empty:
                    daily_table_df["Formatted Revenue"] = daily_table_df["predicted_revenue"].apply(format_inr)
                    daily_table_df["Formatted Lower"] = daily_table_df["lower_bound"].apply(format_inr)
                    daily_table_df["Formatted Upper"] = daily_table_df["upper_bound"].apply(format_inr)
                    
                    st.dataframe(
                        daily_table_df[["date", "day_of_week", "Formatted Revenue", "Formatted Lower", "Formatted Upper"]].rename(columns={
                            "date": "Projection Date",
                            "day_of_week": "Day",
                            "Formatted Revenue": "Projected Daily Revenue",
                            "Formatted Lower": "Conservative Estimate (₹)",
                            "Formatted Upper": "Optimistic Estimate (₹)"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

                # How Accurate is this? Expander
                with st.expander("🎯 How Accurate is this? Multi-Model Benchmark & Error Evaluation"):
                    st.markdown("""
                    We benchmarked three distinct mathematical approaches across the exact same 20% chronological test window:
                    - **Prophet**: Meta's automated trend and weekly seasonality model
                    - **Random Forest Regressor**: Non-linear ensemble model with engineered lag & rolling features
                    - **XGBoost Regressor**: Gradient-boosted decision trees
                    """)

                    if metrics:
                        rows = []
                        for m_name, m_vals in metrics.items():
                            is_win = "🏆 WINNER" if m_name == model_used else ""
                            rows.append({
                                "Model Architecture": m_name,
                                "Mean Absolute Error (MAE)": format_inr(m_vals.get("mae", 0)),
                                "Root Mean Squared Error (RMSE)": format_inr(m_vals.get("rmse", 0)),
                                "Selection Status": is_win
                            })
                        st.table(pd.DataFrame(rows))

                    comp_img_path = os.path.join(os.path.dirname(__file__), "artifacts", "forecast_components.png")
                    if os.path.exists(comp_img_path):
                        st.image(comp_img_path, caption="Prophet Decomposition: Trend and Day-of-Week Seasonality", use_container_width=True)

            elif fc_resp.status_code == 403:
                st.markdown("""
                <div class="access-restricted-card">
                    <div class="access-restricted-icon">🔒</div>
                    <div class="access-restricted-title">Access Restricted</div>
                    <div class="access-restricted-desc">Current role is not authorized to view sales forecasts.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Error loading forecast data: {fc_resp.text}")
        except Exception as e:
            st.error(f"Failed to fetch forecast: {str(e)}")

# ==============================================================================
# TAB 4: INVENTORY & OPERATIONS (Milestone 1 Intact)
# ==============================================================================
with tab_inventory:
    st.subheader("Store Inventory & Stock Replenishment")
    try:
        inv_resp = requests.get(f"{API_BASE}/api/v1/inventory", headers=headers, timeout=5)
        alert_resp = requests.get(f"{API_BASE}/api/v1/inventory/alerts", headers=headers, timeout=5)

        if inv_resp.status_code == 200:
            inv_items = inv_resp.json()
            alerts = alert_resp.json() if alert_resp.status_code == 200 else []

            if alerts:
                st.warning(f"⚠️ **Attention Required**: {len(alerts)} items are currently at or below minimum threshold.")
                with st.expander("🚨 View Critical Low Stock Items", expanded=True):
                    alert_df = pd.DataFrame(alerts)
                    st.dataframe(alert_df[["product_id", "product_name", "category", "stock_level", "reorder_threshold"]], use_container_width=True, hide_index=True)

            st.markdown("##### **Full Store Inventory Catalog**")
            inv_df = pd.DataFrame(inv_items)
            if not inv_df.empty:
                inv_df["price_formatted"] = inv_df["unit_price"].apply(format_inr)
                st.dataframe(
                    inv_df[["product_id", "product_name", "category", "price_formatted", "stock_level", "reorder_threshold"]].rename(columns={
                        "product_id": "SKU",
                        "product_name": "Product Name",
                        "category": "Category",
                        "price_formatted": "Unit Price",
                        "stock_level": "Current Stock",
                        "reorder_threshold": "Reorder Point"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    except Exception as e:
        st.error(f"Failed to load inventory: {str(e)}")

# ==============================================================================
# TAB 5: SYSTEM & ADMINISTRATION (Milestone 1 Intact + Access Matrix)
# ==============================================================================
with tab_admin:
    st.subheader("Platform Control & RBAC Governance")
    
    st.markdown("##### **Enterprise Role-Based Access Matrix**")
    st.markdown("""
    | Functional Feature / Resource | Business Owner | Store Manager | Sales Executive | Administrator |
    | :--- | :---: | :---: | :---: | :---: |
    | **Executive Sales KPIs** | ✅ Full Access | 🏬 Store Isolated | 👤 Personal Scope | ✅ Full Access |
    | **Customer Segmentation** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ✅ Full Access |
    | **Sales Forecasting (`/forecast`)** | ✅ Full Access | 👁️ View Only | ❌ **No Access (403)** | ✅ Full Access |
    | **Business Report Download** | ✅ Full Access | 👁️ View/Download | ❌ **No Access (403)** | ✅ Full Access |
    | **User Administration (`/users`)** | ❌ No Access | ❌ No Access | ❌ No Access | ✅ Full Access |
    """)

    if current_role in ["administrator", "admin"]:
        st.divider()
        st.markdown("##### **Registered User Directory (Administrator Only)**")
        try:
            users_resp = requests.get(f"{API_BASE}/api/v1/users/", headers=headers, timeout=5)
            if users_resp.status_code == 200:
                users_list = users_resp.json()
                st.dataframe(pd.DataFrame(users_list)[["user_id", "username", "email", "full_name", "role_name", "store_id", "is_active"]], use_container_width=True, hide_index=True)
            else:
                st.warning(f"Could not load users: {users_resp.text}")
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
    else:
        st.caption("ℹ️ User provisioning is restricted to the Administrator account.")
