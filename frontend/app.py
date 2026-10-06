import json

import pandas as pd
import requests
import streamlit as st


# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MarketMind AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# 2. SESSION STATE
# ============================================================

if "token" not in st.session_state:
    st.session_state["token"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None


# ============================================================
# 3. API HELPERS
# ============================================================

def get_headers():
    return {
        "Authorization": (
            f"Bearer {st.session_state['token']}"
        )
    }


def api_get(
    endpoint,
    timeout=120,
):

    try:

        return requests.get(
            f"{BACKEND_URL}{endpoint}",
            headers=get_headers(),
            timeout=timeout,
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Backend connection error: {error}"
        )

        return None


def api_post(
    endpoint,
    payload=None,
    timeout=120,
):

    try:

        return requests.post(
            f"{BACKEND_URL}{endpoint}",
            headers=get_headers(),
            json=payload,
            timeout=timeout,
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Backend connection error: {error}"
        )

        return None


def response_error(
    response,
    default_message="Request failed.",
):

    if response is None:
        return

    try:

        detail = response.json().get(
            "detail",
            default_message,
        )

    except (
        ValueError,
        AttributeError,
    ):

        detail = (
            response.text
            or default_message
        )

    st.error(
        f"API error ({response.status_code}): {detail}"
    )


def records_from_payload(
    payload,
    possible_keys,
):

    if isinstance(
        payload,
        list,
    ):
        return payload

    if not isinstance(
        payload,
        dict,
    ):
        return []

    for key in possible_keys:

        value = payload.get(key)

        if isinstance(
            value,
            list,
        ):
            return value

        if isinstance(
            value,
            dict,
        ):

            records = []

            for name, item in value.items():

                if isinstance(
                    item,
                    dict,
                ):

                    record = {
                        "model": name
                    }

                    record.update(
                        item
                    )

                    records.append(
                        record
                    )

            if records:
                return records

    return []


def show_api_status(payload):

    if isinstance(
        payload,
        dict,
    ):

        status = payload.get(
            "status"
        )

        if status:
            st.success(
                f"Backend status: {status}"
            )


def format_currency(value):

    try:

        return (
            f"${float(value):,.2f}"
        )

    except (
        TypeError,
        ValueError,
    ):

        return "N/A"


# ============================================================
# 4. LOGIN / REGISTRATION
# ============================================================

if st.session_state["token"] is None:

    st.title(
        "🔒 MarketMind AI"
    )

    st.subheader(
        "Small Business Sales Intelligence Platform"
    )

    st.caption(
        "Secure access portal • Milestone 2"
    )

    login_tab, register_tab = st.tabs(
        [
            "🔑 Sign In",
            "📝 Create Account",
        ]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.header(
            "Sign In"
        )

        login_email = st.text_input(
            "Email Address",
            key="login_email",
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button(
            "🔐 Log In",
            type="primary",
            use_container_width=True,
        ):

            if (
                not login_email
                or not login_password
            ):

                st.warning(
                    "Please enter both email and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/login",
                        json={
                            "email": login_email,
                            "password": login_password,
                        },
                        timeout=30,
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state[
                            "token"
                        ] = data[
                            "access_token"
                        ]

                        st.session_state[
                            "role"
                        ] = data[
                            "role"
                        ]

                        st.success(
                            "Access granted."
                        )

                        st.rerun()

                    else:

                        try:

                            detail = (
                                response.json()
                                .get(
                                    "detail",
                                    "Invalid credentials.",
                                )
                            )

                        except ValueError:

                            detail = response.text

                        st.error(
                            f"Authentication failed: {detail}"
                        )

                except requests.exceptions.RequestException as error:

                    st.error(
                        f"Cannot connect to backend: {error}"
                    )

    # ========================================================
    # REGISTRATION
    # ========================================================

    with register_tab:

        st.header(
            "Create Employee Account"
        )

        register_name = st.text_input(
            "Full Name",
            key="register_name",
        )

        register_email = st.text_input(
            "Work Email",
            key="register_email",
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password",
        )

        register_role = st.selectbox(
            "Business Role",
            [
                "business_owner",
                "store_manager",
                "sales_executive",
                "admin",
            ],
            key="register_role",
        )

        if st.button(
            "📝 Register Account",
            use_container_width=True,
        ):

            if (
                not register_name
                or not register_email
                or not register_password
            ):

                st.warning(
                    "Please complete all registration fields."
                )

            else:

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/register",
                        json={
                            "name": register_name,
                            "email": register_email,
                            "password": register_password,
                            "role": register_role,
                        },
                        timeout=30,
                    )

                    if response.status_code == 200:

                        st.success(
                            "Account created successfully. "
                            "Switch to Sign In."
                        )

                    else:

                        try:

                            detail = (
                                response.json()
                                .get(
                                    "detail",
                                    "Registration failed.",
                                )
                            )

                        except ValueError:

                            detail = response.text

                        st.error(
                            f"Registration failed: {detail}"
                        )

                except requests.exceptions.RequestException as error:

                    st.error(
                        f"Backend connection error: {error}"
                    )


# ============================================================
# 5. AUTHENTICATED DASHBOARD
# ============================================================

else:

    current_role = (
        st.session_state["role"]
    )

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "📊 MarketMind AI Business Intelligence Dashboard"
    )

    st.caption(
        "Milestone 2 • Customer Segmentation • "
        "Revenue Forecasting • Demand Forecasting • "
        "Inventory Intelligence • Governance"
    )

    # ========================================================
    # SIDEBAR
    # ========================================================

    st.sidebar.title(
        "🛡️ Operational Identity"
    )

    st.sidebar.info(
        f"Role: **{current_role.upper()}**"
    )

    st.sidebar.caption(
        "Authenticated MarketMind AI session"
    )

    if st.sidebar.button(
        "🚪 Log Out",
        use_container_width=True,
    ):

        st.session_state[
            "token"
        ] = None

        st.session_state[
            "role"
        ] = None

        st.rerun()

    # ========================================================
    # NAVIGATION
    # ========================================================

    (
        tab_sales,
        tab_segments,
        tab_revenue,
        tab_demand,
        tab_models,
        tab_invoices,
        tab_inventory,
        tab_admin,
    ) = st.tabs(
        [
            "💰 Executive KPIs",
            "👥 Customer Segmentation",
            "📈 Revenue Forecast",
            "📦 Demand Forecast",
            "🤖 Model Comparison",
            "🧾 Invoices",
            "📦 Inventory",
            "⚙️ Governance",
        ]
    )


    # ========================================================
    # TAB 1 — EXECUTIVE KPIs
    # ========================================================

    with tab_sales:

        st.header(
            "💰 Executive Sales Intelligence"
        )

        response = api_get(
            "/sales/summary"
        )

        if response is not None:

            if response.status_code == 200:

                data = response.json()

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Total Revenue",
                    format_currency(
                        data.get(
                            "total_revenue",
                            0,
                        )
                    ),
                )

                col2.metric(
                    "Total Orders",
                    f"{int(data.get('total_orders', 0)):,}",
                )

                col3.metric(
                    "Top Product",
                    data.get(
                        "top_product",
                        "N/A",
                    ),
                )

                st.success(
                    "Sales intelligence API connected."
                )

            else:

                response_error(
                    response,
                    "Unable to retrieve sales summary.",
                )


    # ========================================================
    # TAB 2 — CUSTOMER SEGMENTATION
    # ========================================================

    with tab_segments:

        st.header(
            "👥 Customer Segmentation Intelligence"
        )

        st.write(
            "Behavioral customer segmentation using "
            "the completed Milestone 2 clustering pipeline."
        )

        response = api_get(
            "/segments"
        )

        if response is not None:

            if response.status_code == 200:

                data = response.json()

                show_api_status(
                    data
                )

                total_customers = data.get(
                    "total_customers",
                    0,
                )

                segment_count = data.get(
                    "segment_count",
                    0,
                )

                col1, col2 = st.columns(2)

                col1.metric(
                    "Total Customers",
                    f"{int(total_customers):,}",
                )

                col2.metric(
                    "Business Segments",
                    f"{int(segment_count):,}",
                )

                segment_records = records_from_payload(
                    data,
                    [
                        "segment_summary",
                        "summary",
                        "segments",
                    ],
                )

                if segment_records:

                    segment_df = pd.DataFrame(
                        segment_records
                    )

                    st.subheader(
                        "Segment Distribution"
                    )

                    if (
                        "segment"
                        in segment_df.columns
                        and "customer_count"
                        in segment_df.columns
                    ):

                        chart_df = (
                            segment_df[
                                [
                                    "segment",
                                    "customer_count",
                                ]
                            ]
                            .set_index(
                                "segment"
                            )
                            .sort_values(
                                "customer_count"
                            )
                        )

                        st.bar_chart(
                            chart_df,
                            horizontal=True,
                        )

                    st.subheader(
                        "Segment Business Summary"
                    )

                    st.dataframe(
                        segment_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                customer_records = records_from_payload(
                    data,
                    [
                        "customers",
                        "customer_segments",
                        "records",
                    ],
                )

                if customer_records:

                    customer_df = pd.DataFrame(
                        customer_records
                    )

                    st.subheader(
                        "Customer Segment Assignments"
                    )

                    st.dataframe(
                        customer_df,
                        use_container_width=True,
                        hide_index=True,
                    )

            else:

                response_error(
                    response,
                    "Unable to retrieve segmentation.",
                )


    # ========================================================
    # TAB 3 — UCI REVENUE FORECAST
    # ========================================================

    with tab_revenue:

        st.header(
            "📈 UCI Revenue Forecasting"
        )

        st.write(
            "Revenue forecasting using the UCI Online Retail II "
            "sales history and completed Milestone 2 models."
        )

        response = api_get(
            "/forecast/revenue"
        )

        if response is not None:

            if response.status_code == 200:

                data = response.json()

                show_api_status(
                    data
                )

                # ------------------------------------------------
                # Validation information
                # ------------------------------------------------

                validation = data.get(
                    "validation",
                    {},
                )

                if validation:

                    st.caption(
                        "Chronological holdout: "
                        f"{validation.get('test_start', 'N/A')} "
                        f"to "
                        f"{validation.get('test_end', 'N/A')}"
                    )

                # ------------------------------------------------
                # Model metrics
                # ------------------------------------------------

                model_records = records_from_payload(
                    data,
                    [
                        "models",
                        "model_comparison",
                    ],
                )

                if model_records:

                    revenue_model_df = pd.DataFrame(
                        model_records
                    )

                    st.subheader(
                        "Revenue Model Performance"
                    )

                    st.dataframe(
                        revenue_model_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                # ------------------------------------------------
                # Predictions
                # ------------------------------------------------

                prediction_records = records_from_payload(
                    data,
                    [
                        "predictions",
                        "forecast",
                    ],
                )

                if prediction_records:

                    forecast_df = pd.DataFrame(
                        prediction_records
                    )

                    st.subheader(
                        "Actual vs Forecast"
                    )

                    chart_columns = [
                        column
                        for column in [
                            "actual_revenue",
                            "prophet_prediction",
                            "random_forest_prediction",
                            "xgboost_prediction",
                        ]
                        if column
                        in forecast_df.columns
                    ]

                    if (
                        "date"
                        in forecast_df.columns
                        and chart_columns
                    ):

                        chart_df = forecast_df[
                            [
                                "date",
                                *chart_columns,
                            ]
                        ].copy()

                        chart_df[
                            "date"
                        ] = pd.to_datetime(
                            chart_df[
                                "date"
                            ],
                            errors="coerce",
                        )

                        chart_df = (
                            chart_df
                            .dropna(
                                subset=[
                                    "date"
                                ]
                            )
                            .set_index(
                                "date"
                            )
                        )

                        st.line_chart(
                            chart_df
                        )

                    st.subheader(
                        "Revenue Forecast Records"
                    )

                    st.dataframe(
                        forecast_df,
                        use_container_width=True,
                        hide_index=True,
                    )

            else:

                response_error(
                    response,
                    "Unable to retrieve revenue forecast.",
                )


    # ========================================================
    # TAB 4 — M5 DEMAND FORECAST
    # ========================================================

    with tab_demand:

        st.header(
            "📦 M5 Demand Forecasting"
        )

        st.write(
            "Item/store demand forecasting using "
            "the M5 Forecasting Accuracy development series."
        )

        response = api_get(
            "/forecast/demand"
        )

        if response is not None:

            if response.status_code == 200:

                data = response.json()

                show_api_status(
                    data
                )

                st.caption(
                    "Validation horizon: "
                    f"{data.get('validation_horizon_days', 28)} days • "
                    f"{data.get('validation_start', 'N/A')} "
                    f"to "
                    f"{data.get('validation_end', 'N/A')}"
                )

                model_records = records_from_payload(
                    data,
                    [
                        "models",
                        "model_comparison",
                    ],
                )

                if model_records:

                    demand_model_df = pd.DataFrame(
                        model_records
                    )

                    st.subheader(
                        "Demand Model Performance"
                    )

                    st.dataframe(
                        demand_model_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                prediction_records = records_from_payload(
                    data,
                    [
                        "predictions",
                        "forecast",
                    ],
                )

                if prediction_records:

                    demand_df = pd.DataFrame(
                        prediction_records
                    )

                    st.subheader(
                        "Actual vs Predicted Demand"
                    )

                    if (
                        "date"
                        in demand_df.columns
                        and "actual_units"
                        in demand_df.columns
                        and "predicted_units"
                        in demand_df.columns
                    ):

                        chart_df = demand_df[
                            [
                                "date",
                                "actual_units",
                                "predicted_units",
                            ]
                        ].copy()

                        chart_df[
                            "date"
                        ] = pd.to_datetime(
                            chart_df[
                                "date"
                            ],
                            errors="coerce",
                        )

                        chart_df = (
                            chart_df
                            .dropna(
                                subset=[
                                    "date"
                                ]
                            )
                            .set_index(
                                "date"
                            )
                        )

                        st.line_chart(
                            chart_df
                        )

                    st.subheader(
                        "Demand Forecast Records"
                    )

                    st.dataframe(
                        demand_df,
                        use_container_width=True,
                        hide_index=True,
                    )

            else:

                response_error(
                    response,
                    "Unable to retrieve demand forecast.",
                )


    # ========================================================
    # TAB 5 — MODEL COMPARISON
    # ========================================================

    with tab_models:

        st.header(
            "🤖 Forecasting Model Comparison"
        )

        response = api_get(
            "/forecast/models"
        )

        if response is not None:

            if response.status_code == 200:

                data = response.json()

                show_api_status(
                    data
                )

                # ------------------------------------------------
                # UCI
                # ------------------------------------------------

                st.subheader(
                    "UCI Revenue Models"
                )

                uci_records = records_from_payload(
                    data,
                    [
                        "uci_revenue_models",
                    ],
                )

                if uci_records:

                    uci_df = pd.DataFrame(
                        uci_records
                    )

                    st.dataframe(
                        uci_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                    if (
                        "model"
                        in uci_df.columns
                        and "mae"
                        in uci_df.columns
                    ):

                        chart_df = (
                            uci_df[
                                [
                                    "model",
                                    "mae",
                                ]
                            ]
                            .set_index(
                                "model"
                            )
                            .sort_values(
                                "mae"
                            )
                        )

                        st.caption(
                            "Lower MAE indicates lower average forecasting error."
                        )

                        st.bar_chart(
                            chart_df,
                            horizontal=True,
                        )

                # ------------------------------------------------
                # M5
                # ------------------------------------------------

                st.subheader(
                    "M5 Demand Models"
                )

                m5_records = records_from_payload(
                    data,
                    [
                        "m5_demand_models",
                    ],
                )

                if m5_records:

                    m5_df = pd.DataFrame(
                        m5_records
                    )

                    st.dataframe(
                        m5_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                    if (
                        "model"
                        in m5_df.columns
                        and "mae"
                        in m5_df.columns
                    ):

                        chart_df = (
                            m5_df[
                                [
                                    "model",
                                    "mae",
                                ]
                            ]
                            .set_index(
                                "model"
                            )
                            .sort_values(
                                "mae"
                            )
                        )

                        st.caption(
                            "Lower MAE indicates lower average demand forecasting error."
                        )

                        st.bar_chart(
                            chart_df,
                            horizontal=True,
                        )

            else:

                response_error(
                    response,
                    "Unable to retrieve model comparison.",
                )


    # ========================================================
    # TAB 6 — INVOICE MANAGEMENT
    # ========================================================

    with tab_invoices:

        st.header(
            "🧾 Invoice Registry Management"
        )

        st.write(
            "Create and review transaction invoices "
            "through the secured backend registry."
        )

        # ----------------------------------------------------
        # CREATE INVOICE
        # ----------------------------------------------------

        if current_role in [
            "sales_executive",
            "admin",
        ]:

            st.subheader(
                "Create New Invoice"
            )

            with st.form(
                "invoice_creation_form",
                clear_on_submit=True,
            ):

                col1, col2 = st.columns(2)

                with col1:

                    customer_name = st.text_input(
                        "Customer Name",
                        placeholder="Enter customer name",
                    )

                    product_name = st.text_input(
                        "Product Name",
                        placeholder="Enter product name",
                    )

                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        value=1,
                        step=1,
                    )

                with col2:

                    unit_price = st.number_input(
                        "Unit Price",
                        min_value=0.01,
                        value=1.00,
                        step=0.01,
                        format="%.2f",
                    )

                    payment_status = st.selectbox(
                        "Payment Status",
                        [
                            "Pending",
                            "Paid",
                            "Cancelled",
                        ],
                    )

                submitted = st.form_submit_button(
                    "➕ Create Invoice",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:

                if (
                    not customer_name.strip()
                    or not product_name.strip()
                ):

                    st.warning(
                        "Customer name and product name are required."
                    )

                else:

                    payload = {
                        "customer_name": (
                            customer_name.strip()
                        ),
                        "product_name": (
                            product_name.strip()
                        ),
                        "quantity": int(
                            quantity
                        ),
                        "unit_price": float(
                            unit_price
                        ),
                        "payment_status": (
                            payment_status
                        ),
                    }

                    create_response = api_post(
                        "/invoices/create",
                        payload=payload,
                        timeout=60,
                    )

                    if create_response is not None:

                        if create_response.status_code == 200:

                            create_data = (
                                create_response.json()
                            )

                            created_invoice = (
                                create_data.get(
                                    "invoice",
                                    {},
                                )
                            )

                            st.success(
                                create_data.get(
                                    "message",
                                    "Invoice created successfully.",
                                )
                            )

                            if created_invoice:

                                c1, c2, c3 = st.columns(3)

                                c1.metric(
                                    "Invoice ID",
                                    created_invoice.get(
                                        "invoice_id",
                                        "N/A",
                                    ),
                                )

                                c2.metric(
                                    "Total Amount",
                                    format_currency(
                                        created_invoice.get(
                                            "total_amount",
                                            0,
                                        )
                                    ),
                                )

                                c3.metric(
                                    "Status",
                                    created_invoice.get(
                                        "payment_status",
                                        "N/A",
                                    ),
                                )

                        else:

                            response_error(
                                create_response,
                                "Invoice creation failed.",
                            )

        else:

            st.info(
                "Invoice creation is restricted to "
                "Sales Executive and Admin roles."
            )

        st.divider()

        # ----------------------------------------------------
        # INVOICE REGISTRY
        # ----------------------------------------------------

        st.subheader(
            "Transaction Archive"
        )

        view_response = api_get(
            "/invoices/view",
            timeout=60,
        )

        if view_response is not None:

            if view_response.status_code == 200:

                invoice_data = (
                    view_response.json()
                )

                total_invoices = invoice_data.get(
                    "total_invoices",
                    0,
                )

                st.metric(
                    "Stored Invoices",
                    f"{int(total_invoices):,}",
                )

                invoices = invoice_data.get(
                    "invoices",
                    [],
                )

                if invoices:

                    invoice_df = pd.DataFrame(
                        invoices
                    )

                    preferred_columns = [
                        "invoice_id",
                        "customer_name",
                        "product_name",
                        "quantity",
                        "unit_price",
                        "total_amount",
                        "payment_status",
                        "created_by",
                        "created_at",
                    ]

                    visible_columns = [
                        column
                        for column in preferred_columns
                        if column
                        in invoice_df.columns
                    ]

                    st.dataframe(
                        invoice_df[
                            visible_columns
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                    csv_data = invoice_df.to_csv(
                        index=False
                    )

                    st.download_button(
                        "⬇️ Download Invoice Registry",
                        data=csv_data,
                        file_name=(
                            "marketmind_invoice_registry.csv"
                        ),
                        mime="text/csv",
                        use_container_width=True,
                    )

                else:

                    st.info(
                        "No invoices have been created yet."
                    )

            else:

                response_error(
                    view_response,
                    "Invoice registry unavailable.",
                )


    # ========================================================
    # TAB 7 — INVENTORY
    # ========================================================

    with tab_inventory:

        st.header(
            "📦 Milestone 2 — Inventory Intelligence"
        )

        st.write(
            "Estimated product inventory generated from "
            "historical UCI Online Retail II sales."
        )

        st.info(
            "Inventory is estimated from historical sales. "
            "The UCI dataset does not contain verified physical "
            "stock counts."
        )

        if st.button(
            "🔄 Load Inventory Preview",
            use_container_width=True,
        ):

            with st.spinner(
                "Loading inventory data..."
            ):

                inventory_response = api_get(
                    "/milestone2/preview",
                    timeout=120,
                )

            if inventory_response is not None:

                if inventory_response.status_code == 200:

                    inventory_data = (
                        inventory_response.json()
                    )

                    st.success(
                        inventory_data.get(
                            "message",
                            "Inventory preview loaded.",
                        )
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Total Products",
                        f"{inventory_data.get('total_products', 0):,}",
                    )

                    col2.metric(
                        "Total Units Sold",
                        f"{inventory_data.get('total_units_sold', 0):,}",
                    )

                    col3.metric(
                        "Estimated Remaining Stock",
                        f"{inventory_data.get('total_estimated_remaining_stock', 0):,}",
                    )

                    products = inventory_data.get(
                        "products",
                        [],
                    )

                    if products:

                        inventory_df = pd.DataFrame(
                            products
                        )

                        st.subheader(
                            "Inventory Product Records"
                        )

                        st.dataframe(
                            inventory_df,
                            use_container_width=True,
                            hide_index=True,
                        )

                        json_data = json.dumps(
                            products,
                            indent=2,
                        )

                        st.download_button(
                            "⬇️ Download Inventory JSON",
                            data=json_data,
                            file_name=(
                                "marketmind_inventory_preview.json"
                            ),
                            mime="application/json",
                            use_container_width=True,
                        )

                    st.caption(
                        inventory_data.get(
                            "note",
                            "Inventory values are estimates.",
                        )
                    )

                else:

                    response_error(
                        inventory_response,
                        "Unable to retrieve inventory preview.",
                    )


    # ========================================================
    # TAB 8 — GOVERNANCE
    # ========================================================

    with tab_admin:

        st.header(
            "⚙️ Identity & System Governance"
        )

        if current_role != "admin":

            st.warning(
                "This area is restricted to administrator accounts."
            )

        else:

            response = api_get(
                "/admin/users",
                timeout=60,
            )

            if response is not None:

                if response.status_code == 200:

                    data = response.json()

                    st.success(
                        "Identity administration endpoint connected."
                    )

                    users = data.get(
                        "registered_user_profiles",
                        [],
                    )

                    if users:

                        user_df = pd.DataFrame(
                            {
                                "Registered User":
                                    users
                            }
                        )

                        st.dataframe(
                            user_df,
                            use_container_width=True,
                            hide_index=True,
                        )

                    else:

                        st.info(
                            "No registered users returned."
                        )

                else:

                    response_error(
                        response,
                        "Unable to retrieve governance data.",
                    )