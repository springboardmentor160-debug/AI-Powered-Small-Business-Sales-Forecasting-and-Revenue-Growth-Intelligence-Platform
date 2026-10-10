import os

import streamlit as st

import requests

import pandas as pd

# =========================================

# PAGE CONFIGURATION

# =========================================

st.set_page_config(

    page_title="MarketMind AI",

    page_icon="📊",

    layout="wide"

)

# =========================================

# API URL

# =========================================

API_URL = "http://127.0.0.1:8000"

# =========================================

# SESSION STATE

# =========================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if "user_name" not in st.session_state:

    st.session_state.user_name = ""

if "user_role" not in st.session_state:

    st.session_state.user_role = ""

if "user_email" not in st.session_state:

    st.session_state.user_email = ""

# =========================================

# HELPER FUNCTION

# =========================================

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

# =========================================

# LOGIN / REGISTER PAGE

# =========================================

def login_page():

    st.title("📊 MARKETMIND AI")

    st.subheader("Welcome to MarketMind AI")

    tab1, tab2 = st.tabs(

        ["Login", "Register"]

    )

    # =====================================

    # LOGIN

    # =====================================

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

    # =====================================

    # REGISTER

    # =====================================

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

# =========================================

# DASHBOARD

# =========================================

def dashboard():

    # =====================================

    # HEADER

    # =====================================

    col1, col2 = st.columns(

        [5, 1]

    )

    with col1:

        st.title(

            "MARKETMIND AI"

        )

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

    # =====================================

    # ROLE ACCESS

    # =====================================

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

    # =====================================

    # ADMIN PANEL

    # =====================================

    if st.session_state.user_role == "admin":

        st.markdown("---")

        st.subheader(

            "👑 Admin Panel"

        )

        st.write(

            "Admin-only features"

        )

        if st.button(

            "👥 View All Users"

        ):

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

    # =====================================

    # STORE SELECTOR

    # =====================================

    st.markdown("---")

    st.selectbox(

        "Store",

        ["Downtown"]

    )

    # =====================================

    # BACKEND DATA

    # =====================================

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

    forecast_data = get_data(

        "/forecast/revenue"

    )

    segment_data = get_data(

        "/customers/segments"

    )

    recommendation_data = get_data(

        "/inventory/recommendations"

    )

    # =====================================

    # BUSINESS OVERVIEW

    # =====================================

    st.markdown("---")

    st.subheader(

        "Business Overview"

    )

    col1, col2, col3 = st.columns(3)

    # -------------------------------------

    # TOTAL REVENUE

    # -------------------------------------

    with col1:

        if summary_data:

            st.metric(

                "💰 TOTAL REVENUE",

                f"₹{summary_data.get('revenue', 0):,.0f}"

            )

        else:

            st.metric(

                "💰 TOTAL REVENUE",

                "No Data"

            )

    # -------------------------------------

    # LOW STOCK

    # -------------------------------------

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

    # -------------------------------------

    # TOP PRODUCT

    # -------------------------------------

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

    # =====================================

    # SALES TREND

    # =====================================

    st.markdown("---")

    st.subheader(

        "📈 Sales Trend Chart | Last 30 Days"

    )

    if trend_data:

        try:

            trend_df = pd.DataFrame(

                trend_data

            )

            trend_df["date"] = pd.to_datetime(

                trend_df["date"]

            )

            trend_df = trend_df.sort_values(

                "date"

            )

            trend_chart = trend_df.set_index(

                "date"

            )

            st.line_chart(

                trend_chart["revenue"]

            )

        except Exception:

            st.warning(

                "Unable to display sales trend."

            )

    else:

        st.warning(

            "Sales trend data is not available."

        )

    # =====================================

    # REVENUE FORECAST

    # =====================================

    st.markdown("---")

    st.subheader(

        "🔮 Revenue Forecast | Next 30 Days"

    )

    if forecast_data:

        try:

            forecast_df = pd.DataFrame(

                forecast_data["forecast"]

            )

            forecast_df["date"] = pd.to_datetime(

                forecast_df["date"]

            )

            forecast_df = forecast_df.sort_values(

                "date"

            )

            # ---------------------------------

            # FORECAST SUMMARY METRICS

            # ---------------------------------

            forecast_values = (

                forecast_df[

                    "predicted_revenue"

                ]

                .astype(float)

                .tolist()

            )

            if forecast_values:

                average_forecast = (

                    sum(forecast_values)

                    / len(forecast_values)

                )

                highest_forecast = max(

                    forecast_values

                )

                lowest_forecast = min(

                    forecast_values

                )

                metric1, metric2, metric3 = (

                    st.columns(3)

                )

                with metric1:

                    st.metric(

                        "📊 Average Forecast",

                        f"₹{average_forecast:,.0f}"

                    )

                with metric2:

                    st.metric(

                        "📈 Highest Forecast",

                        f"₹{highest_forecast:,.0f}"

                    )

                with metric3:

                    st.metric(

                        "📉 Lowest Forecast",

                        f"₹{lowest_forecast:,.0f}"

                    )

            # ---------------------------------

            # FORECAST CHART

            # ---------------------------------

            forecast_chart = forecast_df.set_index(

                "date"

            )

            st.line_chart(

                forecast_chart[

                    "predicted_revenue"

                ]

            )

            st.caption(

                "Forecast generated using Prophet. "

                "The prediction represents expected daily revenue."

            )

            # ---------------------------------

            # FORECAST DETAILS

            # ---------------------------------

            with st.expander(

                "View Forecast Details"

            ):

                display_forecast = (

                    forecast_df.copy()

                )

                display_forecast[

                    "date"

                ] = display_forecast[

                    "date"

                ].dt.strftime(

                    "%d %b %Y"

                )

                display_forecast[

                    "predicted_revenue"

                ] = display_forecast[

                    "predicted_revenue"

                ].round(2)

                display_forecast[

                    "lower_bound"

                ] = display_forecast[

                    "lower_bound"

                ].round(2)

                display_forecast[

                    "upper_bound"

                ] = display_forecast[

                    "upper_bound"

                ].round(2)

                st.dataframe(

                    display_forecast,

                    use_container_width=True,

                    hide_index=True

                )

        except Exception as error:

            st.warning(

                f"Unable to display revenue forecast: {error}"

            )

    else:

        st.info(

            "Revenue forecast data is not available."

        )

    # =====================================

    # FORECAST MODEL PERFORMANCE

    # =====================================

    st.markdown("---")

    st.subheader(

        "📊 Forecast Model Performance"

    )

    model_file = (

        "data/forecast_model_comparison.csv"

    )

    if os.path.exists(model_file):

        try:

            model_df = pd.read_csv(

                model_file

            )

            if (

                "MAE" in model_df.columns

                and "RMSE" in model_df.columns

            ):

                model_df["MAE"] = (

                    model_df["MAE"]

                    .astype(float)

                    .round(2)

                )

                model_df["RMSE"] = (

                    model_df["RMSE"]

                    .astype(float)

                    .round(2)

                )

            st.dataframe(

                model_df,

                use_container_width=True,

                hide_index=True

            )

            st.caption(

                "Models evaluated using MAE and RMSE "

                "on the same time-based test period."

            )

        except Exception:

            st.info(

                "Unable to load model comparison."

            )

    else:

        st.info(

            "Forecast model comparison is not available yet."

        )

    # =====================================

    # BUSINESS REPORT DOWNLOAD

    # =====================================

    st.subheader(

        "📄 Business Report"

    )

    business_report_file = (

        "data/business_report.xlsx"

    )

    if os.path.exists(

        business_report_file

    ):

        try:

            with open(

                business_report_file,

                "rb"

            ) as file:

                report_bytes = file.read()

            st.download_button(

                label="📥 Download Business Report",

                data=report_bytes,

                file_name="business_report.xlsx",

                mime=(

                    "application/vnd.openxmlformats-officedocument."

                    "spreadsheetml.sheet"

                )

            )

        except Exception:

            st.info(

                "Business report could not be loaded."

            )

    else:

        st.info(

            "Business report file is not available yet."

        )

    # =====================================

    # INVENTORY + CUSTOMER SEGMENTS

    # =====================================

    st.markdown("---")

    col1, col2 = st.columns(2)

    # =====================================

    # INVENTORY RECOMMENDATIONS

    # =====================================

    with col1:

        st.subheader(

            "📦 Inventory Recommendations"

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

                    "recommendation"

                ]

                available_columns = [

                    column

                    for column in display_columns

                    if column in recommendation_df.columns

                ]

                st.write(

                    f"**{len(recommendation_df)} "

                    f"inventory recommendations found**"

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

    # =====================================

    # CUSTOMER SEGMENTS

    # =====================================

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

                        segment_df[

                            "segment"

                        ]

                        .value_counts()

                        .sort_values()

                    )

                    st.bar_chart(

                        segment_count,

                        horizontal=True

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

    # =====================================
    # MILESTONE 3: AI PRODUCT RECOMMENDATIONS
    # =====================================

    st.markdown("---")
    st.subheader("🛍️ AI Product Recommendations")
    st.caption(
        "Explore personalized product suggestions and products frequently "
        "purchased together."
    )

    personal_col, association_col = st.columns(2)

    with personal_col:
        st.markdown("### 👤 Personalized Recommendations")
        customer_id_input = st.text_input(
            "Customer ID",
            value="12346",
            key="milestone3_customer_id",
            help="Enter a customer ID present in the recommendation dataset.",
        )

        if st.button(
            "Get Personalized Recommendations",
            key="get_personalized_recommendations",
            use_container_width=True,
        ):
            if not customer_id_input.strip():
                st.warning("Please enter a customer ID.")
            else:
                try:
                    response = requests.get(
                        f"{API_URL}/recommendations/customer/"
                        f"{customer_id_input.strip()}",
                        params={"limit": 5},
                        timeout=15,
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        recommendations = payload.get("recommendations", [])
                        if recommendations:
                            st.success(
                                f"{len(recommendations)} recommendations found "
                                f"for customer {payload.get('customer_id', customer_id_input)}."
                            )
                            personal_df = pd.DataFrame(recommendations)
                            rename_map = {
                                "stock_code": "Stock Code",
                                "product": "Recommended Product",
                                "recommendation_score": "Recommendation Score",
                                "method": "Method",
                            }
                            personal_df = personal_df.rename(columns=rename_map)
                            if "Recommendation Score" in personal_df.columns:
                                personal_df["Recommendation Score"] = (
                                    pd.to_numeric(
                                        personal_df["Recommendation Score"],
                                        errors="coerce",
                                    ).round(4)
                                )
                            st.dataframe(
                                personal_df,
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.info(
                                payload.get(
                                    "message",
                                    "No recommendations found for this customer.",
                                )
                            )
                    else:
                        try:
                            detail = response.json().get("detail", response.text)
                        except ValueError:
                            detail = response.text
                        st.error(
                            f"Recommendation API returned {response.status_code}: "
                            f"{detail}"
                        )
                except requests.RequestException as error:
                    st.error(
                        "Could not connect to the recommendation API. "
                        f"Check that FastAPI is running. Details: {error}"
                    )

    with association_col:
        st.markdown("### 🧺 Frequently Bought Together")
        stock_code_input = st.text_input(
            "Purchased Product Stock Code",
            value="23289",
            key="milestone3_stock_code",
            help="Enter a stock code present in the association rules dataset.",
        )

        if st.button(
            "Find Related Products",
            key="get_association_recommendations",
            use_container_width=True,
        ):
            if not stock_code_input.strip():
                st.warning("Please enter a stock code.")
            else:
                try:
                    response = requests.get(
                        f"{API_URL}/recommendations/product/"
                        f"{stock_code_input.strip()}",
                        params={
                            "limit": 5,
                            "min_confidence": 0.20,
                            "min_support": 0.005,
                        },
                        timeout=15,
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        recommendations = payload.get("recommendations", [])
                        if recommendations:
                            st.success(
                                f"{len(recommendations)} related products found "
                                f"for stock code {payload.get('stock_code', stock_code_input)}."
                            )
                            association_df = pd.DataFrame(recommendations)
                            rename_map = {
                                "purchased_product": "Purchased Product",
                                "recommended_stock_code": "Recommended Stock Code",
                                "recommended_product": "Recommended Product",
                                "support": "Support",
                                "confidence": "Confidence",
                                "lift": "Lift",
                                "method": "Method",
                            }
                            association_df = association_df.rename(
                                columns=rename_map
                            )
                            for metric_column in [
                                "Support",
                                "Confidence",
                                "Lift",
                            ]:
                                if metric_column in association_df.columns:
                                    association_df[metric_column] = pd.to_numeric(
                                        association_df[metric_column],
                                        errors="coerce",
                                    ).round(4)
                            st.dataframe(
                                association_df,
                                use_container_width=True,
                                hide_index=True,
                            )
                            st.caption(
                                "Support measures how often products occur together; "
                                "confidence estimates the conditional frequency; lift "
                                "compares the association with independent occurrence. "
                                "Check support and transaction counts before interpreting "
                                "very high lift values."
                            )
                        else:
                            st.info(
                                payload.get(
                                    "message",
                                    "No matching product associations were found.",
                                )
                            )
                    else:
                        try:
                            detail = response.json().get("detail", response.text)
                        except ValueError:
                            detail = response.text
                        st.error(
                            f"Association API returned {response.status_code}: "
                            f"{detail}"
                        )
                except requests.RequestException as error:
                    st.error(
                        "Could not connect to the recommendation API. "
                        f"Check that FastAPI is running. Details: {error}"
                    )

    # =====================================
    # MILESTONE 3: CUSTOMER CHURN RISK
    # =====================================

    st.markdown("---")
    st.subheader("⚠️ Customer Churn Risk")
    st.caption(
        "Prioritize customers who may be at risk of becoming inactive. "
        "These estimates use proxy inactivity labels, not verified churn outcomes."
    )

    churn_file = os.path.join("data", "customer_churn_predictions.csv")
    churn_metrics_file = os.path.join("data", "churn_model_comparison.csv")

    if os.path.exists(churn_file):
        try:
            churn_df = pd.read_csv(churn_file)

            if churn_df.empty:
                st.info("The churn prediction file contains no customer records.")
            else:
                # Normalize column names to make display tolerant of minor naming differences.
                column_lookup = {str(col).strip().lower(): col for col in churn_df.columns}

                def find_column(*candidates):
                    for candidate in candidates:
                        if candidate.lower() in column_lookup:
                            return column_lookup[candidate.lower()]
                    return None

                churn_prob_col = find_column(
                    "churn_probability", "probability", "churn_prob"
                )
                churn_risk_col = find_column(
                    "risk_category", "risk_level", "churn_risk"
                )
                churn_customer_col = find_column(
                    "CustomerID", "customer_id", "customerid"
                )
                churn_model_col = find_column("model_used", "model")
                churn_label_col = find_column("label_type")

                metric_cols = st.columns(3)
                metric_cols[0].metric("Customers scored", f"{len(churn_df):,}")

                if churn_risk_col:
                    risk_values = churn_df[churn_risk_col].astype(str).str.lower()
                    high_count = int(risk_values.isin(["high", "high risk"]).sum())
                    medium_count = int(risk_values.isin(["medium", "medium risk"]).sum())
                else:
                    high_count = 0
                    medium_count = 0

                metric_cols[1].metric("High-risk customers", f"{high_count:,}")
                metric_cols[2].metric("Medium-risk customers", f"{medium_count:,}")

                if churn_metrics_file and os.path.exists(churn_metrics_file):
                    try:
                        churn_metrics_df = pd.read_csv(churn_metrics_file)
                        st.markdown("#### Churn Model Comparison")
                        st.dataframe(
                            churn_metrics_df.round(4),
                            use_container_width=True,
                            hide_index=True,
                        )
                        st.caption(
                            "Compare precision, recall, F1 and ROC-AUC together. "
                            "The saved comparison determines the reported model performance."
                        )
                    except Exception as error:
                        st.info(f"Could not display churn model comparison: {error}")

                if churn_prob_col:
                    churn_df[churn_prob_col] = pd.to_numeric(
                        churn_df[churn_prob_col], errors="coerce"
                    )
                    churn_df["Churn Probability (%)"] = (
                        churn_df[churn_prob_col].clip(0, 1) * 100
                    ).round(2)

                if churn_risk_col:
                    risk_filter_values = sorted(
                        churn_df[churn_risk_col].dropna().astype(str).unique().tolist()
                    )
                    selected_risks = st.multiselect(
                        "Filter by risk category",
                        options=risk_filter_values,
                        default=risk_filter_values,
                        key="churn_risk_filter",
                    )
                    filtered_churn_df = churn_df[
                        churn_df[churn_risk_col].astype(str).isin(selected_risks)
                    ].copy()
                else:
                    filtered_churn_df = churn_df.copy()
                    st.info("Risk category column was not found in the prediction file.")

                if churn_prob_col:
                    filtered_churn_df = filtered_churn_df.sort_values(
                        churn_prob_col, ascending=False, na_position="last"
                    )

                display_map = {}
                if churn_customer_col:
                    display_map[churn_customer_col] = "Customer ID"
                if churn_prob_col:
                    display_map[churn_prob_col] = "Churn Probability (0–1)"
                if churn_risk_col:
                    display_map[churn_risk_col] = "Risk Category"
                if churn_model_col:
                    display_map[churn_model_col] = "Model Used"
                if churn_label_col:
                    display_map[churn_label_col] = "Label Type"

                display_churn_df = filtered_churn_df.rename(columns=display_map)
                preferred_columns = [
                    "Customer ID",
                    "Churn Probability (%)",
                    "Churn Probability (0–1)",
                    "Risk Category",
                    "Model Used",
                    "Label Type",
                ]
                visible_columns = [
                    col for col in preferred_columns if col in display_churn_df.columns
                ]
                if not visible_columns:
                    visible_columns = display_churn_df.columns.tolist()

                st.markdown("#### Customers to Review")
                st.dataframe(
                    display_churn_df[visible_columns].head(100),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption(
                    "Showing up to 100 customers, sorted by estimated churn probability "
                    "when that field is available."
                )

                churn_csv = filtered_churn_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Filtered Churn Predictions",
                    data=churn_csv,
                    file_name="customer_churn_predictions_filtered.csv",
                    mime="text/csv",
                    key="download_churn_predictions",
                )
        except Exception as error:
            st.warning(f"Unable to display churn predictions: {error}")
    else:
        st.info(
            "Churn predictions are not available. Run "
            "`python churn_prediction.py` from the project folder first."
        )

    # =====================================
    # MILESTONE 3: ANOMALY ALERTS
    # =====================================

    st.markdown("---")
    st.subheader("🚨 Unusual Sales Activity Alerts")
    st.caption(
        "These are unusual-order alerts for human review, not proof of fraud."
    )

    alerts_file = os.path.join("data", "fraud_alerts.csv")
    anomalies_file = os.path.join("data", "transaction_anomalies.csv")

    if os.path.exists(alerts_file):
        try:
            alerts_df = pd.read_csv(alerts_file)

            if alerts_df.empty:
                st.success("No anomaly alerts are currently present in the alert file.")
            else:
                alert_columns = st.columns(3)
                alert_columns[0].metric("Orders flagged", f"{len(alerts_df):,}")

                if "severity" in alerts_df.columns:
                    severity_values = alerts_df["severity"].astype(str).str.lower()
                    high_alert_count = int((severity_values == "high").sum())
                    medium_alert_count = int((severity_values == "medium").sum())
                else:
                    high_alert_count = 0
                    medium_alert_count = 0

                alert_columns[1].metric("High severity", f"{high_alert_count:,}")
                alert_columns[2].metric("Medium severity", f"{medium_alert_count:,}")

                if "severity" in alerts_df.columns:
                    severity_options = sorted(
                        alerts_df["severity"].dropna().astype(str).unique().tolist()
                    )
                    selected_severities = st.multiselect(
                        "Filter alert severity",
                        options=severity_options,
                        default=severity_options,
                        key="anomaly_severity_filter",
                    )
                    filtered_alerts_df = alerts_df[
                        alerts_df["severity"].astype(str).isin(selected_severities)
                    ].copy()
                else:
                    filtered_alerts_df = alerts_df.copy()

                if "total_amount" in filtered_alerts_df.columns:
                    filtered_alerts_df["total_amount"] = pd.to_numeric(
                        filtered_alerts_df["total_amount"], errors="coerce"
                    )
                    filtered_alerts_df = filtered_alerts_df.sort_values(
                        "total_amount", ascending=False, na_position="last"
                    )

                st.markdown("#### Alerts Requiring Review")
                st.dataframe(
                    filtered_alerts_df.head(200),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption("Showing up to 200 alerts. Use the filters to narrow the list.")

                alerts_csv = filtered_alerts_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Filtered Anomaly Alerts",
                    data=alerts_csv,
                    file_name="fraud_alerts_filtered.csv",
                    mime="text/csv",
                    key="download_anomaly_alerts",
                )

                if os.path.exists(anomalies_file):
                    with st.expander("View all analyzed orders"):
                        try:
                            all_anomalies_df = pd.read_csv(anomalies_file)
                            st.write(f"Orders in analysis: {len(all_anomalies_df):,}")
                            st.dataframe(
                                all_anomalies_df.head(200),
                                use_container_width=True,
                                hide_index=True,
                            )
                            st.caption("The full dataset remains available in the CSV file.")
                        except Exception as error:
                            st.info(f"Could not load the complete anomaly results: {error}")
        except Exception as error:
            st.warning(f"Unable to display anomaly alerts: {error}")
    else:
        st.info(
            "Anomaly alerts are not available. Run "
            "`python anomaly_detection.py` from the project folder first."
        )

    # =====================================

    # EXPORT DASHBOARD REPORT

    # =====================================

    st.markdown("---")

    st.subheader(

        "📄 Export Dashboard Report"

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

    csv = (

        report_df

        .to_csv(index=False)

        .encode("utf-8")

    )

    st.download_button(

        label="📥 Export Dashboard CSV",

        data=csv,

        file_name="marketmind_report.csv",

        mime="text/csv"

    )

    # =====================================

    # BACKEND STATUS

    # =====================================

    st.markdown("---")

    if summary_data:

        st.success(

            "Backend connected successfully ✅"

        )

    else:

        st.error(

            "FastAPI backend is not running ❌"

        )

# =========================================

# MAIN APPLICATION

# =========================================

if st.session_state.logged_in:

    dashboard()

else:

    login_page()
