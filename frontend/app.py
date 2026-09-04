import streamlit as st
import requests
import pandas as pd


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------
st.set_page_config(
    page_title="MarketMind AI",
    page_icon="📊",
    layout="wide"
)


# -----------------------------------------
# API URL
# -----------------------------------------
API_URL = "http://127.0.0.1:8000"


# -----------------------------------------
# SESSION STATE
# -----------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""


# -----------------------------------------
# HELPER FUNCTION TO GET API DATA
# -----------------------------------------
def get_data(endpoint):

    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except Exception:
        return None


# -----------------------------------------
# LOGIN / REGISTER PAGE
# -----------------------------------------
def login_page():

    st.title("📊 MARKETMIND AI")
    st.subheader("Welcome to MarketMind AI")

    tab1, tab2 = st.tabs([
        "Login",
        "Register"
    ])

    # -----------------------------------------
    # LOGIN TAB
    # -----------------------------------------
    with tab1:

        st.subheader("Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login"):

            if email == "" or password == "":

                st.warning(
                    "Please enter email and password."
                )

            else:

                login_data = {
                    "email": email,
                    "password": password
                }

                try:

                    response = requests.post(
                        f"{API_URL}/login",
                        json=login_data,
                        timeout=10
                    )

                    if response.status_code == 200:

                        data = response.json()

                        user_data = data.get(
                            "user",
                            {}
                        )

                        st.session_state.logged_in = True

                        st.session_state.user_name = (
                            user_data.get(
                                "name",
                                email
                            )
                        )

                        st.session_state.user_email = (
                            user_data.get(
                                "email",
                                email
                            )
                        )

                        st.session_state.user_role = (
                            user_data.get(
                                "role",
                                "user"
                            )
                        )

                        st.success(
                            "Login successful! ✅"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Invalid email or password ❌"
                        )

                except Exception:

                    st.error(
                        "Backend is not running ❌"
                    )

    # -----------------------------------------
    # REGISTER TAB
    # -----------------------------------------
    with tab2:

        st.subheader("Create New Account")

        name = st.text_input(
            "Name",
            key="register_name"
        )

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        role = st.selectbox(
            "Role",
            [
                "user",
                "admin"
            ]
        )

        if st.button("Register"):

            if (
                name == ""
                or register_email == ""
                or register_password == ""
            ):

                st.warning(
                    "Please fill all fields."
                )

            else:

                register_data = {
                    "name": name,
                    "email": register_email,
                    "password": register_password,
                    "role": role
                }

                try:

                    response = requests.post(
                        f"{API_URL}/register",
                        json=register_data,
                        timeout=10
                    )

                    if response.status_code == 200:

                        st.success(
                            "Registration successful! "
                            "Now login. ✅"
                        )

                    else:

                        try:

                            error_data = response.json()

                            st.error(
                                error_data.get(
                                    "detail",
                                    "Registration failed."
                                )
                            )

                        except Exception:

                            st.error(
                                "Registration failed."
                            )

                except Exception:

                    st.error(
                        "Backend is not running ❌"
                    )


# -----------------------------------------
# DASHBOARD
# -----------------------------------------
def dashboard():

    # -----------------------------------------
    # HEADER
    # -----------------------------------------
    col1, col2 = st.columns([5, 1])

    with col1:

        st.title("MARKETMIND AI")

        st.caption(
            f"Welcome, "
            f"{st.session_state.user_name} "
            f"({st.session_state.user_role})"
        )

    with col2:

        st.write("")

        if st.button("🚪 Logout"):

            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_role = ""
            st.session_state.user_email = ""

            st.rerun()


    # -----------------------------------------
    # ROLE-BASED ACCESS
    # -----------------------------------------
    if st.session_state.user_role == "admin":

        st.success(
            "👑 Admin Access: Full system access"
        )

    elif st.session_state.user_role == "manager":

        st.info(
            "📊 Manager Access: Analytics and inventory access"
        )

    elif st.session_state.user_role == "sales_executive":

        st.info(
            "💼 Sales Executive Access: Sales dashboard access"
        )

    else:

        st.warning(
            "👤 Standard User Access"
        )


    # -----------------------------------------
    # ADMIN PANEL
    # -----------------------------------------
    if st.session_state.user_role == "admin":

        st.markdown("---")

        st.subheader("👑 Admin Panel")

        st.write("Admin-only features")

        if st.button("👥 View All Users"):

            users_data = get_data(
                "/admin/users"
            )

            if users_data:

                users_df = pd.DataFrame(
                    users_data
                )

                st.dataframe(
                    users_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.error(
                    "Unable to load users."
                )


    # -----------------------------------------
    # STORE SELECTOR
    # -----------------------------------------
    st.markdown("---")

    store = st.selectbox(
        "Store",
        ["Downtown"]
    )


    # -----------------------------------------
    # GET DATA FROM BACKEND
    # -----------------------------------------
    summary_data = get_data(
        "/summary"
    )

    inventory_data = get_data(
        "/inventory/summary"
    )

    top_product_data = get_data(
        "/sales/top-product"
    )

    trend_data = get_data(
        "/sales/trend"
    )

    segment_data = get_data(
        "/customers/segments"
    )

    recommendation_data = get_data(
        "/inventory/recommendations"
    )


    # -----------------------------------------
    # BUSINESS OVERVIEW
    # -----------------------------------------
    st.markdown("---")

    st.subheader(
        "Business Overview"
    )

    col1, col2, col3 = st.columns(3)


    # SALES TODAY
    with col1:

        if summary_data:

            st.metric(
                "💰 SALES TODAY",
                f"₹{summary_data.get('revenue', 0):,.0f}"
            )

        else:

            st.metric(
                "💰 SALES TODAY",
                "No Data"
            )


    # LOW STOCKS
    with col2:

        if inventory_data:

            st.metric(
                "📦 LOW STOCKS",
                inventory_data.get(
                    "low_stock_products",
                    0
                )
            )

        else:

            st.metric(
                "📦 LOW STOCKS",
                "No Data"
            )


    # TOP PRODUCT
    with col3:

        if top_product_data:

            product_name = top_product_data.get(
                "product",
                "No Data"
            )

            if len(product_name) > 25:

                product_name = (
                    product_name[:25]
                    + "..."
                )

            st.metric(
                "🏆 TOP PRODUCT",
                product_name
            )

        else:

            st.metric(
                "🏆 TOP PRODUCT",
                "No Data"
            )


    # -----------------------------------------
    # SALES TREND
    # -----------------------------------------
    st.markdown("---")

    st.subheader(
        "📈 Sales Trend Chart | Last 30 Days"
    )

    if trend_data:

        try:

            df = pd.DataFrame(
                trend_data
            )

            df["date"] = pd.to_datetime(
                df["date"]
            )

            df = df.sort_values(
                "date"
            )

            chart_data = df.set_index(
                "date"
            )

            st.line_chart(
                chart_data["revenue"]
            )

        except Exception:

            st.warning(
                "Unable to display sales trend."
            )

    else:

        st.warning(
            "Sales trend data is not available."
        )


    # -----------------------------------------
    # AI INSIGHTS
    # -----------------------------------------
    st.markdown("---")

    col1, col2 = st.columns(2)


    # -----------------------------------------
    # INVENTORY RECOMMENDATIONS
    # -----------------------------------------
    with col1:

        st.subheader(
            "🤖 AI Inventory Recommendations"
        )

        if recommendation_data:

            try:

                recommendation_df = pd.DataFrame(
                    recommendation_data
                )

                display_columns = [
                    "product_name",
                    "category",
                    "stock_quantity",
                    "reorder_level",
                    "recommendation",
                    "priority"
                ]

                available_columns = [
                    col for col in display_columns
                    if col in recommendation_df.columns
                ]

                st.write(
                    f"**{len(recommendation_df)} inventory recommendations found**"
                )

                st.dataframe(
                    recommendation_df[
                        available_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            except Exception:

                st.warning(
                    "Unable to display inventory recommendations."
                )

        else:

            st.info(
                "No inventory recommendations available."
            )


    # -----------------------------------------
    # CUSTOMER SEGMENTS
    # -----------------------------------------
    with col2:

        st.subheader(
            "👥 Customer Segments"
        )

        if segment_data:

            try:

                segment_df = pd.DataFrame(
                    segment_data
                )

                if "segment" in segment_df.columns:

                    segment_count = (
                        segment_df["segment"]
                        .value_counts()
                    )

                    st.bar_chart(
                        segment_count
                    )

                    st.caption(
                        "Customers grouped based on purchasing behavior."
                    )

                else:

                    st.info(
                        "Customer segment data is available."
                    )

            except Exception:

                st.info(
                    "Unable to display customer segments."
                )

        else:

            st.info(
                "Customer segmentation data is not available."
            )


    # -----------------------------------------
    # EXPORT REPORT
    # -----------------------------------------
    st.markdown("---")

    st.subheader(
        "📄 Export Report"
    )

    report_data = {

        "Metric": [

            "Total Revenue",
            "Total Sales",
            "Total Customers",
            "Total Products",
            "Low Stock Products"

        ],

        "Value": [

            summary_data.get(
                "revenue",
                0
            )
            if summary_data
            else 0,

            summary_data.get(
                "sales",
                0
            )
            if summary_data
            else 0,

            summary_data.get(
                "customers",
                0
            )
            if summary_data
            else 0,

            summary_data.get(
                "products",
                0
            )
            if summary_data
            else 0,

            inventory_data.get(
                "low_stock_products",
                0
            )
            if inventory_data
            else 0

        ]
    }


    report_df = pd.DataFrame(
        report_data
    )

    csv = report_df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )

    st.download_button(
        label="📥 Export Dashboard Report",
        data=csv,
        file_name="marketmind_report.csv",
        mime="text/csv"
    )


    # -----------------------------------------
    # BACKEND STATUS
    # -----------------------------------------
    st.markdown("---")

    if summary_data:

        st.success(
            "Backend connected successfully ✅"
        )

    else:

        st.error(
            "FastAPI backend is not running ❌"
        )


# -----------------------------------------
# MAIN APPLICATION
# -----------------------------------------
if st.session_state.logged_in:

    dashboard()

else:

    login_page()