import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import jwt

API_URL = "http://127.0.0.1:8000/sales"
LOGIN_URL = "http://127.0.0.1:8000/login"

st.set_page_config(
    page_title="MarketMind AI",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None


# ============================================================
# LOGIN
# ============================================================

if st.session_state.token is None:

    st.title("🔐 MarketMind AI Login")
    st.caption("Please log in to access the dashboard.")

    with st.form("login_form"):

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login_button = st.form_submit_button("Login")

        if login_button:

            if not username or not password:
                st.error("Please enter both username and password.")

            else:
                try:

                    response = requests.post(
                        LOGIN_URL,
                        json={
                            "username": username,
                            "password": password
                        },
                        timeout=30
                    )

                    if response.status_code == 200:

                        login_data = response.json()

                        token = login_data.get("access_token")

                        if not token:
                            st.error("Login succeeded but no access token was returned.")
                            st.stop()

                        # Decode token only to read the role/username.
                        # The actual token validation is performed by FastAPI.
                        decoded = jwt.decode(
                            token,
                            options={"verify_signature": False}
                        )

                        st.session_state.token = token
                        st.session_state.username = decoded.get("sub")
                        st.session_state.role = decoded.get("role")

                        st.success("Login successful!")

                        st.rerun()

                    else:

                        try:
                            error_message = response.json().get(
                                "detail",
                                "Invalid username or password."
                            )
                        except Exception:
                            error_message = "Invalid username or password."

                        st.error(error_message)

                except requests.exceptions.RequestException:
                    st.error(
                        "Could not connect to the FastAPI backend. "
                        "Make sure Uvicorn is running at "
                        "http://127.0.0.1:8000"
                    )

    st.stop()


# ============================================================
# LOGGED-IN USER INFORMATION
# ============================================================

st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

st.sidebar.info(
    f"Role: {st.session_state.role}"
)

if st.sidebar.button("Logout"):

    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None

    st.rerun()


# ============================================================
# MAIN DASHBOARD
# ============================================================

st.title("📊 MarketMind AI Dashboard")

st.caption(
    "Sales dashboard powered by FastAPI + PostgreSQL"
)


# ============================================================
# LOAD SALES DATA
# ============================================================

@st.cache_data
def get_sales():

    response = requests.get(
        API_URL,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


try:

    data = get_sales()

    if not data:

        st.warning(
            "No sales data was returned by the backend."
        )

        st.stop()

    df = pd.DataFrame(data)

    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"]
    )

    df["sales_amount"] = pd.to_numeric(
        df["sales_amount"]
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"]
    )


    # ========================================================
    # KEY METRICS
    # ========================================================

    total_sales = df["sales_amount"].sum()

    total_units = df["quantity"].sum()

    total_transactions = len(df)


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Sales",
        f"£{total_sales:,.2f}"
    )

    col2.metric(
        "Units Sold",
        f"{total_units:,.0f}"
    )

    col3.metric(
        "Transactions",
        f"{total_transactions:,}"
    )


    st.divider()


    # ========================================================
    # SALES OVER TIME
    # ========================================================

    st.subheader("📈 Sales Over Time")

    sales_over_time = (
        df.groupby(
            df["invoice_date"].dt.date
        )["sales_amount"]
        .sum()
        .reset_index()
    )

    sales_over_time.columns = [
        "date",
        "sales"
    ]

    fig = px.line(
        sales_over_time,
        x="date",
        y="sales",
        title="Sales Over Time",
        markers=True
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales Amount"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ========================================================
    # RECENT TRANSACTIONS
    # ========================================================

    st.subheader("Recent Transactions")

    recent = (
        df.sort_values(
            "invoice_date",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        recent[
            [
                "invoice_id",
                "product_id",
                "customer_id",
                "quantity",
                "unit_price",
                "invoice_date",
                "sales_amount"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # ROLE-BASED ACCESS
    # ========================================================

    user_role = st.session_state.role


    # --------------------------------------------------------
    # ANALYTICS
    # Analyst + Manager + Admin
    # --------------------------------------------------------

    if user_role in [
        "analyst",
        "manager",
        "admin"
    ]:

        st.divider()

        st.subheader("📊 Analytics")

        st.write(
            "Advanced analytics are available for "
            "Analyst, Manager, and Admin users."
        )

        avg_transaction = (
            total_sales / total_transactions
            if total_transactions > 0
            else 0
        )

        analytics_col1, analytics_col2 = st.columns(2)

        analytics_col1.metric(
            "Average Transaction Value",
            f"£{avg_transaction:,.2f}"
        )

        analytics_col2.metric(
            "Unique Customers",
            f"{df['customer_id'].nunique():,}"
        )


    # --------------------------------------------------------
    # REPORTS
    # Manager + Admin
    # --------------------------------------------------------

    if user_role in [
        "manager",
        "admin"
    ]:

        st.divider()

        st.subheader("📋 Reports")

        st.write(
            "Management reports are available for "
            "Manager and Admin users."
        )

        report_col1, report_col2 = st.columns(2)

        report_col1.metric(
            "Unique Products",
            f"{df['product_id'].nunique():,}"
        )

        report_col2.metric(
            "Reporting Transactions",
            f"{len(df):,}"
        )


    # --------------------------------------------------------
    # ADMIN
    # Admin only
    # --------------------------------------------------------

    if user_role == "admin":

        st.divider()

        st.subheader("👑 Admin")

        st.success(
            "Admin access granted."
        )

        st.write(
            "Administrative features are available "
            "only to Admin users."
        )


    # --------------------------------------------------------
    # VIEWER
    # Viewer only
    # --------------------------------------------------------

    if user_role == "viewer":

        st.divider()

        st.subheader("👁️ Viewer Access")

        st.info(
            "You have Viewer access. "
            "You can view the dashboard but do not "
            "have access to Analytics, Reports, or Admin features."
        )


except requests.exceptions.RequestException:

    st.error(
        "Could not connect to the FastAPI backend. "
        "Make sure Uvicorn is running at "
        "http://127.0.0.1:8000"
    )


except Exception as e:

    st.error(
        f"Dashboard error: {e}"
    )