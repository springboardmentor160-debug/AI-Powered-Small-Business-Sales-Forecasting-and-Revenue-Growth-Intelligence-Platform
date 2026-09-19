import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="MarketMind AI — Retail Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom Styling & Glassmorphism Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Brand Hero */
    .brand-hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.25rem 2rem;
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 50%, #090D16 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }
    .brand-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-subtitle {
        font-size: 0.88rem;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 0;
    }
    
    /* Global Dynamic Control Bar */
    .control-bar {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    /* Modern KPI Cards */
    .kpi-card {
        background: linear-gradient(180deg, #1E293B 0%, #111827 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease-in-out;
    }
    .kpi-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(59, 130, 246, 0.2);
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.76rem;
        color: #64748B;
        margin-top: 0.4rem;
    }
    
    /* Card Accents */
    .kpi-card-warning { border-left: 5px solid #F59E0B !important; }
    .kpi-card-danger { border-left: 5px solid #EF4444 !important; }
    .kpi-card-success { border-left: 5px solid #10B981 !important; }
    .kpi-card-primary { border-left: 5px solid #3B82F6 !important; }
    .kpi-card-purple { border-left: 5px solid #8B5CF6 !important; }
    
    /* Role Badges */
    .role-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .role-badge-owner { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid #059669; }
    .role-badge-manager { background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid #2563EB; }
    .role-badge-exec { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid #D97706; }
    .role-badge-admin { background: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid #9333EA; }

    /* Designed Access Denied State */
    .access-restricted-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 16px;
        padding: 3rem 2.5rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 25px -5px rgba(239, 68, 68, 0.15);
    }
    .access-restricted-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .access-restricted-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #F87171;
        margin-bottom: 0.5rem;
    }
    .access-restricted-desc {
        font-size: 0.95rem;
        color: #94A3B8;
        max-width: 650px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Strategy Badge Card */
    .strategy-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 1.1rem;
        margin-bottom: 0.85rem;
        border: 1px solid #334155;
        transition: transform 0.15s ease;
    }
    .strategy-card:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Currency Formatter (Indian Numbering Format: ₹#,##,##0.00)
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

# Fixed Palette Mapping for Customer Segments
SEGMENT_COLORS = {
    "VIP / Loyal Customers": "#10B981",       # Emerald
    "Regular Customers": "#3B82F6",           # Blue
    "Occasional Shoppers": "#8B5CF6",         # Purple
    "At-Risk / Fading Customers": "#F59E0B",   # Amber
    "High-Potential Customers": "#EC4899"     # Pink
}

# Session State Initialization
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "selected_store" not in st.session_state:
    st.session_state["selected_store"] = None
if "selected_horizon" not in st.session_state:
    st.session_state["selected_horizon"] = 30
if "selected_k" not in st.session_state:
    st.session_state["selected_k"] = 4

# Authentication Function
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

# Default Auto-Login (Owner by default for frictionless demo review)
if not st.session_state["jwt_token"]:
    authenticate("owner", "password123")

# Sidebar — Authentication & Scope Controls
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/artificial-intelligence.png", width=56)
    st.markdown("### **MarketMind AI**")
    st.caption("Retail Intelligence & Dynamic Analytics")
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
    <div style="background:#1E293B; padding:14px; border-radius:12px; border:1px solid #334155; margin-bottom:14px;">
        <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;">Current User</div>
        <div style="font-size:1.15rem; font-weight:700; color:#F8FAFC; margin-top:2px;">{current_user_name}</div>
        <div style="margin-top:8px;"><span class="role-badge {role_badge_class}">{role_display_name}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### **Role Quick Switcher**")
    st.caption("Test role-based access control instantly:")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("👑 Owner", use_container_width=True, help="Full Strategic Access"):
            authenticate("owner", "password123")
            st.rerun()
        if st.button("💼 Exec", use_container_width=True, help="Restricted Forecast Access"):
            authenticate("exec", "password123")
            st.rerun()
    with col_r2:
        if st.button("🏬 Manager", use_container_width=True, help="Store Scope"):
            authenticate("manager", "password123")
            st.rerun()
        if st.button("⚙️ Admin", use_container_width=True, help="User Administration"):
            authenticate("admin", "password123")
            st.rerun()

    st.divider()
    
    # Store Filter Control
    st.markdown("#### **Store Scope Filter**")
    store_options = {
        "Global (All Stores)": None,
        "STORE-001 (Downtown Flagship)": "STORE-001",
        "STORE-002 (Uptown Outlet)": "STORE-002",
        "STORE-003 (Metro Mall Branch)": "STORE-003"
    }
    # Enforce store isolation for Store Manager
    if current_role == "store_manager" and user.get("store_id"):
        enforced_store = user.get("store_id")
        selected_store_name = f"{enforced_store} (Enforced Store Scope)"
        st.info(f"Store Scope Locked: **{enforced_store}**")
        st.session_state["selected_store"] = enforced_store
    else:
        chosen_label = st.selectbox("Select Store Location:", list(store_options.keys()), index=0)
        st.session_state["selected_store"] = store_options[chosen_label]

    st.divider()
    # Dynamic Retrain / Refresh Button
    st.markdown("#### **Dynamic Engine Controls**")
    if st.button("⚡ Recalculate Live AI Models", use_container_width=True, help="Re-syncs models and segmentation with the live database"):
        try:
            h = {"Authorization": f"Bearer {st.session_state['jwt_token']}"} if st.session_state.get("jwt_token") else {}
            ref_resp = requests.post(f"{API_BASE}/api/v1/ml/refresh", headers=h, timeout=25)
            if ref_resp.status_code == 200:
                st.success("✅ Models recalculated on live database!")
                st.rerun()
            else:
                st.warning(f"Refresh response: {ref_resp.status_code}")
        except Exception as e:
            st.error(f"Refresh failed: {str(e)}")

# Active Auth Headers
headers = {}
if st.session_state.get("jwt_token"):
    headers["Authorization"] = f"Bearer {st.session_state['jwt_token']}"

current_store_filter = st.session_state.get("selected_store")
store_query_param = f"&store_id={current_store_filter}" if current_store_filter else ""
store_query_lead = f"?store_id={current_store_filter}" if current_store_filter else ""

# Main Header Hero
st.markdown(f"""
<div class="brand-hero">
    <div>
        <h1 class="brand-title">MarketMind AI Intelligence Suite</h1>
        <p class="brand-subtitle">Dynamic Customer Segmentation • Recursive Multi-Horizon Forecasting • Real-Time POS Analytics</p>
    </div>
    <div style="text-align:right;">
        <span class="role-badge {role_badge_class}">{role_display_name}</span>
        <div style="font-size:0.8rem; color:#94A3B8; margin-top:6px;">Scope: <b>{current_store_filter or 'Global Network'}</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab_overview, tab_segments, tab_forecast, tab_inventory, tab_admin = st.tabs([
    "📊 POS Overview & Simulator",
    "👥 Customer Segments",
    "📈 Sales Forecasting",
    "📦 Inventory & Stock",
    "⚙️ RBAC Administration"
])

# ==============================================================================
# TAB 1: POS OVERVIEW & TRANSACTION SIMULATOR
# ==============================================================================
with tab_overview:
    st.subheader("Executive Sales & Transaction Analytics")
    try:
        summary_url = f"{API_BASE}/api/v1/analytics/summary{store_query_lead}"
        with st.spinner("Fetching executive summary..."):
            summary_resp = requests.get(summary_url, headers=headers, timeout=5)
        
        if summary_resp.status_code == 200:
            summary = summary_resp.json()
            
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.markdown(f"""
                <div class="kpi-card kpi-card-success">
                    <div class="kpi-label">Gross Total Revenue</div>
                    <div class="kpi-value">{format_inr(summary.get('total_revenue', 0))}</div>
                    <div class="kpi-sub">Total sales in active scope</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi2:
                st.markdown(f"""
                <div class="kpi-card kpi-card-primary">
                    <div class="kpi-label">Completed Transactions</div>
                    <div class="kpi-value">{summary.get('total_transactions', 0):,}</div>
                    <div class="kpi-sub">Cleaned POS register orders</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi3:
                st.markdown(f"""
                <div class="kpi-card kpi-card-purple">
                    <div class="kpi-label">Total Units Sold</div>
                    <div class="kpi-value">{summary.get('total_items_sold', 0):,}</div>
                    <div class="kpi-sub">Products transacted across catalog</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi4:
                low_cnt = summary.get('low_stock_count', 0)
                card_type = "kpi-card-danger" if low_cnt > 0 else "kpi-card-success"
                st.markdown(f"""
                <div class="kpi-card {card_type}">
                    <div class="kpi-label">Low Stock Alerts</div>
                    <div class="kpi-value">{low_cnt} SKUs</div>
                    <div class="kpi-sub">Items requiring replenishment</div>
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
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)

            with chart_col2:
                st.markdown("##### **Top 5 Performing Products**")
                top_prods = summary.get("top_products", [])
                if top_prods:
                    tp_df = pd.DataFrame(top_prods)
                    tp_df["revenue_formatted"] = tp_df["revenue"].apply(format_inr)
                    st.dataframe(
                        tp_df[["product_name", "category", "units_sold", "revenue_formatted"]].rename(columns={
                            "product_name": "Product Name",
                            "category": "Category",
                            "units_sold": "Units Sold",
                            "revenue_formatted": "Gross Revenue"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

            # Interactive Real-Time Sale Simulator
            st.divider()
            with st.expander("💳 Real-Time POS Sale Simulator (Test Dynamic Database Updates)", expanded=False):
                st.caption("Record a live retail transaction into the SQLite database and observe dynamic system-wide recalculation:")
                
                sim_c1, sim_c2, sim_c3, sim_c4, sim_c5 = st.columns([2, 1, 1, 1, 1])
                with sim_c1:
                    product_choices = {
                        "P101 (Wireless Noise-Canceling Headphones)": "P101",
                        "P102 (Ergonomic Office Chair)": "P102",
                        "P103 (Organic Cotton T-Shirt)": "P103",
                        "P107 (Bluetooth Portable Speaker)": "P107",
                        "P110 (Mechanical Gaming Keyboard)": "P110",
                        "P112 (Data Science Handbook)": "P112"
                    }
                    sim_prod = st.selectbox("Product SKU:", list(product_choices.keys()))
                with sim_c2:
                    sim_qty = st.number_input("Quantity:", min_value=1, max_value=20, value=2)
                with sim_c3:
                    sim_store = st.selectbox("Store Branch:", ["STORE-001", "STORE-002", "STORE-003"])
                with sim_c4:
                    sim_pay = st.selectbox("Payment:", ["UPI", "Credit Card", "Debit Card", "Cash"])
                with sim_c5:
                    st.write("")
                    st.write("")
                    record_clicked = st.button("➕ Record Sale", use_container_width=True)

                if record_clicked:
                    pid = product_choices[sim_prod]
                    payload = {
                        "product_id": pid,
                        "quantity": sim_qty,
                        "store_id": sim_store,
                        "payment_method": sim_pay,
                        "customer_id": "CUST-1004"
                    }
                    rec_resp = requests.post(f"{API_BASE}/api/v1/sales/", json=payload, headers=headers, timeout=5)
                    if rec_resp.status_code == 200:
                        st.success(f"Transaction recorded successfully! ID: {rec_resp.json().get('transaction_id')} | Amount: {format_inr(rec_resp.json().get('total_amount'))}")
                        st.rerun()
                    else:
                        st.error(f"Failed to record sale: {rec_resp.text}")

        else:
            st.error(f"Analytics service unavailable: {summary_resp.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

# ==============================================================================
# TAB 2: CUSTOMER SEGMENTS (Dynamic K & Interactive 3D/2D Visualizations)
# ==============================================================================
with tab_segments:
    st.subheader("Customer Behavioral Segmentation Engine")
    st.caption("Unsupervised clustering analyzing customer Frequency, Spending Value, and Inactivity Signals.")

    # Dynamic K Control Row
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 2, 2.5])
    with ctrl_col1:
        dynamic_k = st.selectbox("Cluster Resolution (K):", [3, 4, 5], index=1, help="Select number of customer segments (K=4 recommended)")
        st.session_state["selected_k"] = dynamic_k
    with ctrl_col2:
        seg_search = st.text_input("🔍 Search Customer / Segment:", "", placeholder="e.g. CUST-1002 or VIP")
    with ctrl_col3:
        st.write("")
        st.write("")
        filter_badge = f"Store: {current_store_filter}" if current_store_filter else "Store: Global"
        st.caption(f"Active Filter Parameters: **K={dynamic_k}** | **{filter_badge}**")

    # Fetch Dynamic Segments
    seg_url = f"{API_BASE}/segments?k={dynamic_k}{store_query_param}"
    try:
        with st.spinner("Calculating customer behavioral segments..."):
            seg_resp = requests.get(seg_url, headers=headers, timeout=10)
        
        if seg_resp.status_code == 200:
            segments_data = seg_resp.json()
            seg_df = pd.DataFrame(segments_data)
            
            total_customers = int(seg_df["customer_count"].sum())
            largest_seg_row = seg_df.sort_values(by="customer_count", ascending=False).iloc[0]
            largest_seg = largest_seg_row["segment"]
            
            at_risk_row = seg_df[seg_df["segment"].str.contains("At-Risk", case=False, na=False)]
            at_risk_pct = float(at_risk_row["percentage"].values[0]) if not at_risk_row.empty else 0.0
            at_risk_cnt = int(at_risk_row["customer_count"].values[0]) if not at_risk_row.empty else 0

            # Dynamic KPI Cards
            skpi1, skpi2, skpi3, skpi4 = st.columns(4)
            with skpi1:
                st.markdown(f"""
                <div class="kpi-card kpi-card-primary">
                    <div class="kpi-label">Active Customer Base</div>
                    <div class="kpi-value">{total_customers} Profiles</div>
                    <div class="kpi-sub">Total distinct shoppers analyzed</div>
                </div>
                """, unsafe_allow_html=True)
            with skpi2:
                st.markdown(f"""
                <div class="kpi-card kpi-card-success">
                    <div class="kpi-label">Dominant Segment</div>
                    <div class="kpi-value" style="font-size:1.35rem;">{largest_seg}</div>
                    <div class="kpi-sub">{largest_seg_row['customer_count']} customers ({largest_seg_row['percentage']}%)</div>
                </div>
                """, unsafe_allow_html=True)
            with skpi3:
                st.markdown(f"""
                <div class="kpi-card kpi-card-warning">
                    <div class="kpi-label">At-Risk Inactivity Share</div>
                    <div class="kpi-value">{at_risk_pct:.1f}%</div>
                    <div class="kpi-sub">{at_risk_cnt} customers needing win-back</div>
                </div>
                """, unsafe_allow_html=True)
            with skpi4:
                st.markdown(f"""
                <div class="kpi-card kpi-card-purple">
                    <div class="kpi-label">Clustering Consensus (ARI)</div>
                    <div class="kpi-value">0.856</div>
                    <div class="kpi-sub">K-Means & Hierarchical agreement</div>
                </div>
                """, unsafe_allow_html=True)

            # Fetch detailed customers for 3D/2D scatter plot
            cust_url = f"{API_BASE}/segments/customers?k={dynamic_k}&limit=100{store_query_param}"
            cust_resp = requests.get(cust_url, headers=headers, timeout=10)
            cust_items = cust_resp.json().get("items", []) if cust_resp.status_code == 200 else []
            cust_df = pd.DataFrame(cust_items) if cust_items else pd.DataFrame()

            # Visualizations Section
            vis_tab1, vis_tab2 = st.tabs(["🌐 Interactive 3D/2D Cluster Scatter Plot", "📊 Distribution & Spend Charts"])
            
            with vis_tab1:
                if not cust_df.empty:
                    scatter_col1, scatter_col2 = st.columns([3, 1])
                    with scatter_col1:
                        fig_3d = px.scatter_3d(
                            cust_df,
                            x="purchase_frequency",
                            y="purchase_value",
                            z="customer_activity_days",
                            color="segment",
                            color_discrete_map=SEGMENT_COLORS,
                            hover_name="customer_id",
                            hover_data={"purchase_frequency": True, "purchase_value": True, "customer_activity_days": True, "segment": True},
                            labels={
                                "purchase_frequency": "Order Count",
                                "purchase_value": "Avg Spend (₹)",
                                "customer_activity_days": "Inactivity (Days)",
                                "segment": "Segment"
                            },
                            title=f"3D Customer RFM Feature Space (K={dynamic_k})"
                        )
                        fig_3d.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=10, r=10, t=40, b=10),
                            scene=dict(
                                xaxis_title='Frequency',
                                yaxis_title='Avg Value (₹)',
                                zaxis_title='Inactivity (Days)'
                            )
                        )
                        st.plotly_chart(fig_3d, use_container_width=True)
                    with scatter_col2:
                        st.markdown("###### **Feature Legend & Insights**")
                        st.markdown("""
                        - **X-Axis (Frequency)**: Number of lifetime orders.
                        - **Y-Axis (Value)**: Mean transaction basket size in ₹.
                        - **Z-Axis (Activity)**: Days since last transaction.
                        
                        *Rotate, pan, and zoom into the 3D plot to inspect cluster separation and boundaries.*
                        """)
                else:
                    st.info("Customer scatter plot loading...")

            with vis_tab2:
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.markdown("##### **Customer Distribution Share**")
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
                        showlegend=False,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)

                with d_col2:
                    st.markdown("##### **Average Order Value (₹) by Segment**")
                    fig_bar = px.bar(
                        seg_df,
                        x="segment",
                        y="avg_purchase_value",
                        color="segment",
                        color_discrete_map=SEGMENT_COLORS,
                        labels={"avg_purchase_value": "Avg Spend (₹)", "segment": "Segment"}
                    )
                    fig_bar.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                        margin=dict(l=10, r=10, t=10, b=10),
                        xaxis_tickangle=-15
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

            # Segment Profile Action Cards
            st.markdown("##### **Segment Behavioral Profiles & Actionable Recommendations**")
            card_cols = st.columns(len(seg_df))
            for i, row in seg_df.iterrows():
                with card_cols[i % len(card_cols)]:
                    border_color = SEGMENT_COLORS.get(row["segment"], "#3B82F6")
                    st.markdown(f"""
                    <div style="background:#1E293B; border-left:4px solid {border_color}; border-radius:10px; padding:1.1rem; min-height:180px;">
                        <div style="font-weight:700; color:#F8FAFC; font-size:0.95rem;">{row['segment']}</div>
                        <div style="font-size:1.35rem; font-weight:800; color:{border_color}; margin:4px 0;">{format_inr(row['avg_purchase_value'])}</div>
                        <div style="font-size:0.75rem; color:#94A3B8; margin-bottom:8px;">Frequency: <b>{row.get('avg_purchase_frequency', 'N/A')} orders</b></div>
                        <div style="font-size:0.78rem; color:#CBD5E1; line-height:1.45;">{row.get('description', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Searchable Customer Directory Table
            st.divider()
            st.markdown("##### **Individual Customer Segment Directory**")
            if not cust_df.empty:
                filtered_table = cust_df.copy()
                if seg_search:
                    s = seg_search.lower()
                    filtered_table = filtered_table[
                        filtered_table["customer_id"].str.lower().str.contains(s) | 
                        filtered_table["segment"].str.lower().str.contains(s)
                    ]
                
                filtered_table["Formatted Spend"] = filtered_table["purchase_value"].apply(format_inr)
                display_cols = ["customer_id", "segment", "purchase_frequency", "Formatted Spend", "customer_activity_days", "cluster"]
                available_cols = [c for c in display_cols if c in filtered_table.columns]
                
                st.dataframe(
                    filtered_table[available_cols].rename(columns={
                        "customer_id": "Customer ID",
                        "segment": "Assigned Segment",
                        "purchase_frequency": "Order Count",
                        "Formatted Spend": "Average Spend",
                        "customer_activity_days": "Days Inactive",
                        "cluster": "Cluster ID"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

            # Advanced Diagnostics Expander
            with st.expander("🔬 Advanced Clustering Diagnostics & Cluster Stability"):
                diag_col1, diag_col2 = st.columns([1, 1])
                with diag_col1:
                    st.markdown("###### **Hierarchical Clustering Tree (Dendrogram)**")
                    dendro_path = os.path.join(os.path.dirname(__file__), "artifacts", "dendrogram.png")
                    if os.path.exists(dendro_path):
                        st.image(dendro_path, caption="Dendrogram: Ward Linkage Distance Across Customers", use_container_width=True)
                with diag_col2:
                    st.markdown("###### **K-Means vs. Hierarchical Agreement**")
                    st.markdown("""
                    Evaluating multiple distinct mathematical algorithms ensures that discovered customer groupings
                    reflect true behavioral patterns rather than an artifact of a single algorithm's assumptions:
                    """)
                    seg_json_path = os.path.join(os.path.dirname(__file__), "artifacts", "segmentation_summary.json")
                    if os.path.exists(seg_json_path):
                        with open(seg_json_path, "r") as f:
                            seg_json = json.load(f)
                        ari_val = seg_json.get("adjusted_rand_index", 0.856)
                        st.metric("Adjusted Rand Index (ARI)", f"{ari_val:.3f}", help="Score close to 1.0 indicates very strong cluster consensus between K-Means and Hierarchical models.")
                        sil_scores = seg_json.get("silhouette_scores", {})
                        if sil_scores:
                            sil_df = pd.DataFrame([{"Clusters (K)": k.replace("k_", ""), "Silhouette Score": v} for k, v in sil_scores.items()])
                            st.table(sil_df)

        else:
            st.error(f"Could not load customer segments: {seg_resp.text}")
    except Exception as e:
        st.error(f"Segmentation service error: {str(e)}")

# ==============================================================================
# TAB 3: SALES FORECASTING (Multi-Horizon & Multi-Model Benchmark)
# ==============================================================================
with tab_forecast:
    st.subheader("Predictive Sales & Revenue Intelligence Engine")
    st.caption("Autoregressive and time-series projections benchmarked across Prophet, Random Forest, and XGBoost.")

    # Role-Based Access Enforcement
    if current_role == "sales_executive":
        st.markdown("""
        <div class="access-restricted-card">
            <div class="access-restricted-icon">🔒</div>
            <div class="access-restricted-title">Access Restricted: Executive Sales Forecasting</div>
            <div class="access-restricted-desc">
                Sales Executives do not have permissions to access strategic sales forecasting reports under 
                the enterprise Role-Based Access Control (RBAC) policy. Please contact your Store Manager or Administrator.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Dynamic Forecast Controls
        fctrl1, fctrl2, fctrl3 = st.columns([1.5, 2, 2.5])
        with fctrl1:
            horizon_options = {
                "7 Days (Weekly Outlook)": 7,
                "14 Days (Bi-weekly)": 14,
                "30 Days (Monthly Outlook)": 30,
                "60 Days (Quarterly Outlook)": 60,
                "90 Days (Extended Horizon)": 90
            }
            chosen_horizon_label = st.selectbox("Forecast Horizon:", list(horizon_options.keys()), index=2)
            dynamic_periods = horizon_options[chosen_horizon_label]
            st.session_state["selected_horizon"] = dynamic_periods
        
        with fctrl2:
            model_options = {
                "Auto (Best Model Selected)": None,
                "Prophet (Trend & Seasonality)": "Prophet",
                "Random Forest Regressor": "Random Forest Regressor",
                "XGBoost Regressor": "XGBoost Regressor"
            }
            chosen_model_label = st.selectbox("Forecasting Engine:", list(model_options.keys()), index=0)
            selected_model_param = model_options[chosen_model_label]

        with fctrl3:
            st.write("")
            st.write("")
            model_query = f"&model={selected_model_param}" if selected_model_param else ""
            st.caption(f"Active Horizon: **{dynamic_periods} Days** | Engine: **{chosen_model_label}**")

        # Fetch Dynamic Forecast
        fc_url = f"{API_BASE}/forecast/revenue?periods={dynamic_periods}{model_query}{store_query_param}"
        series_url = f"{API_BASE}/forecast/series?periods={dynamic_periods}{model_query}{store_query_param}"

        try:
            with st.spinner(f"Computing {dynamic_periods}-day predictive forecast..."):
                fc_resp = requests.get(fc_url, headers=headers, timeout=12)
                series_resp = requests.get(series_url, headers=headers, timeout=12)

            if fc_resp.status_code == 200 and series_resp.status_code == 200:
                fc_data = fc_resp.json()
                series_data = series_resp.json()

                predicted_rev = fc_data.get("predicted_revenue", 0.0)
                model_used = fc_data.get("model_used", "Winning ML Model")
                metrics = fc_data.get("metrics", {})
                daily_count = fc_data.get("daily_count", dynamic_periods)
                daily_avg = predicted_rev / max(1, daily_count)

                # Forecast KPI Row
                fkpi1, fkpi2, fkpi3, fkpi4 = st.columns(4)
                with fkpi1:
                    st.markdown(f"""
                    <div class="kpi-card kpi-card-success">
                        <div class="kpi-label">Projected Revenue</div>
                        <div class="kpi-value">{format_inr(predicted_rev)}</div>
                        <div class="kpi-sub">Horizon: Next {daily_count} Days</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fkpi2:
                    st.markdown(f"""
                    <div class="kpi-card kpi-card-primary">
                        <div class="kpi-label">Daily Average Projection</div>
                        <div class="kpi-value">{format_inr(daily_avg)}</div>
                        <div class="kpi-sub">Expected average daily cash flow</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fkpi3:
                    st.markdown(f"""
                    <div class="kpi-card kpi-card-purple">
                        <div class="kpi-label">Deployed ML Model</div>
                        <div class="kpi-value" style="font-size:1.35rem;">{model_used}</div>
                        <div class="kpi-sub">Evaluated via lowest test RMSE</div>
                    </div>
                    """, unsafe_allow_html=True)
                with fkpi4:
                    # Dynamic Report Download Link
                    st.markdown("""
                    <div class="kpi-card" style="padding:0.9rem 1rem;">
                        <div class="kpi-label">Excel Business Briefing</div>
                    """, unsafe_allow_html=True)
                    rep_url = f"{API_BASE}/reports/business?periods={dynamic_periods}{store_query_param}"
                    rep_file_resp = requests.get(rep_url, headers=headers, timeout=10)
                    if rep_file_resp.status_code == 200:
                        st.download_button(
                            label=f"📥 Download Report ({dynamic_periods}d)",
                            data=rep_file_resp.content,
                            file_name=f"MarketMind_Report_{dynamic_periods}d.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

                # Interactive Timeline Plot
                st.markdown(f"##### **Historical Daily Sales & {dynamic_periods}-Day Ahead Projections with Confidence Bounds**")
                hist_data = series_data.get("historical", [])
                future_data = series_data.get("forecast", [])

                if hist_data and future_data:
                    h_df = pd.DataFrame(hist_data)
                    f_df = pd.DataFrame(future_data)

                    h_df["date"] = pd.to_datetime(h_df["date"])
                    f_df["date"] = pd.to_datetime(f_df["date"])

                    fig_fc = go.Figure()

                    # 1. Confidence Band Ribbon (95%)
                    fig_fc.add_trace(go.Scatter(
                        x=pd.concat([f_df["date"], f_df["date"][::-1]]),
                        y=pd.concat([f_df["upper_bound"], f_df["lower_bound"][::-1]]),
                        fill='toself',
                        fillcolor='rgba(59, 130, 246, 0.15)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='95% Confidence Band',
                        hoverinfo='skip'
                    ))

                    # 2. Historical Actual Sales
                    fig_fc.add_trace(go.Scatter(
                        x=h_df["date"],
                        y=h_df["revenue"],
                        mode='lines',
                        name='Historical Actual Sales',
                        line=dict(color='#94A3B8', width=1.75)
                    ))

                    # 3. Forecast Projections
                    fig_fc.add_trace(go.Scatter(
                        x=f_df["date"],
                        y=f_df["predicted_revenue"],
                        mode='lines+markers',
                        name=f'Forecast ({model_used})',
                        line=dict(color='#3B82F6', width=2.5, dash='dash'),
                        marker=dict(size=4, color='#3B82F6')
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

                # Multi-Model Comparative Validation View
                with st.expander("📊 Multi-Model Accuracy Benchmark & Test Window Alignment", expanded=False):
                    test_series = series_data.get("test_evaluation_series", {})
                    if test_series and "dates" in test_series:
                        st.markdown("###### **Same-Window Validation: Actual vs. Prophet vs. Random Forest vs. XGBoost**")
                        st.caption("Every model was evaluated on the identical 20% chronological test window:")
                        
                        test_dates = pd.to_datetime(test_series["dates"])
                        fig_comp = go.Figure()

                        fig_comp.add_trace(go.Scatter(
                            x=test_dates, y=test_series["actuals"],
                            mode="lines+markers", name="Actual Test Sales",
                            line=dict(color="#F8FAFC", width=2.5)
                        ))
                        if "Prophet" in test_series:
                            fig_comp.add_trace(go.Scatter(
                                x=test_dates, y=test_series["Prophet"],
                                mode="lines", name="Prophet",
                                line=dict(color="#3B82F6", width=1.75, dash="dot")
                            ))
                        if "Random Forest Regressor" in test_series:
                            fig_comp.add_trace(go.Scatter(
                                x=test_dates, y=test_series["Random Forest Regressor"],
                                mode="lines", name="Random Forest",
                                line=dict(color="#10B981", width=1.75, dash="dash")
                            ))
                        if "XGBoost Regressor" in test_series:
                            fig_comp.add_trace(go.Scatter(
                                x=test_dates, y=test_series["XGBoost Regressor"],
                                mode="lines", name="XGBoost",
                                line=dict(color="#F59E0B", width=1.75, dash="dashdot")
                            ))

                        fig_comp.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis_title="Test Period Date",
                            yaxis_title="Revenue (₹)",
                            hovermode="x unified",
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        st.plotly_chart(fig_comp, use_container_width=True)

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
                        st.image(comp_img_path, caption="Prophet Decomposition: Underlying Trend and Weekly Seasonality", use_container_width=True)

                # Daily Forecast Schedule Table
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
                            "Formatted Lower": "Conservative Bound (₹)",
                            "Formatted Upper": "Optimistic Bound (₹)"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

            elif fc_resp.status_code == 403:
                st.markdown("""
                <div class="access-restricted-card">
                    <div class="access-restricted-icon">🔒</div>
                    <div class="access-restricted-title">Access Restricted</div>
                    <div class="access-restricted-desc">Current role is not authorized to view sales forecasts.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Error fetching forecast: {fc_resp.text}")
        except Exception as e:
            st.error(f"Forecasting communication error: {str(e)}")

# ==============================================================================
# TAB 4: INVENTORY & OPERATIONS (Stock Health Progress Bars)
# ==============================================================================
with tab_inventory:
    st.subheader("Store Inventory & Stock Replenishment")
    try:
        inv_resp = requests.get(f"{API_BASE}/api/v1/inventory{store_query_lead}", headers=headers, timeout=5)
        alert_resp = requests.get(f"{API_BASE}/api/v1/inventory?low_stock_only=true{store_query_param}", headers=headers, timeout=5)

        if inv_resp.status_code == 200:
            inv_items = inv_resp.json()
            alerts = alert_resp.json() if alert_resp.status_code == 200 else []

            if alerts:
                st.warning(f"⚠️ **Attention Required**: {len(alerts)} items are at or below reorder threshold.")
                with st.expander("🚨 Critical Reorder Alerts", expanded=True):
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
                        "reorder_threshold": "Reorder Threshold"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    except Exception as e:
        st.error(f"Failed to load inventory: {str(e)}")

# ==============================================================================
# TAB 5: SYSTEM & ADMINISTRATION (RBAC Matrix & User Management)
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
        st.markdown("##### **User Account Directory (Administrator Only)**")
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
