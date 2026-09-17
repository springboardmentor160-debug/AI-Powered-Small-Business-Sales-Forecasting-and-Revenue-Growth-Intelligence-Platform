import streamlit as st  # IMPORT STREAMLIT TO BUILD THE WEB USER INTERFACE
import requests         # IMPORT REQUESTS TO SEND HTTP REQUESTS AND FETCH DATA FROM APIS

#------------------------------------------
# 1. GLOBAL STREAMLIT APPLICATION CONTAINER
#------------------------------------------

# CONFIGURE HIGH-LEVEL BROWSER METADATA, RESPONSIVE WIDE CANVAS LAYOUT, AND SIDEBAR DEFAULTS
st.set_page_config(page_title="MarketMind AI Secure Dashboard", layout="wide", initial_sidebar_state="expanded")

# INITIALIZE GLOBAL TRACKING TOKEN IN DYNAMIC st.session_state MEMORY BLOCKS
# ENFORCES STATE PERSISTENCE ACROSS BROWSER RENDER REFRESHES
if "token" not in st.session_state:
    st.session_state["token"] = None # HOLDS THE SIGNED JWT TOKEN ONCE VALIDATED
if "role" not in st.session_state:
    st.session_state["role"] = None # CACHES AUTHORIZATION ROLE MATRIX VALUES

# MICROSERVICES ROUTING CONFIGURATION TARGET LAYER
BACKEND_URL = "http://127.0.0.1:8000"

#------------------------------------
# 2.AUTHENTICATION SEPARATION GATEWAY
#------------------------------------

# CONDITION A : UNAUTHENTICATED STATE -> RESTRICT VIEW SPACE TO CREDENTIALS ENTRY PROTOCOLS
if st.session_state["token"] is None:
    st.title("🔒 MarketMind AI — Secure Access Portal")

    # ISOLATE FUNCTIONAL AUTHENTICATION PIPELINES VIA UNIFIED STRUCTURAL UI TABS
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])

    # SUB-MODULES : USER SIGN IN LOGIC
    with tab1:
        st.subheader("Login Credentials")
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log In", use_container_width=True):
            try:
                # DISPATCH POST PAYLOAD DIRECTLY TO CORE BACKEND AUTHENTICATION ENDPOINT
                response = requests.post(f"{BACKEND_URL}/login",
                                         json={"email": login_email, "password": login_password})

                # CHECK SERVER HTTP RESPONSE STATUS RESOLUTION
                if response.status_code == 200:
                    payload = response.json()
                    # COMMIT TEMPORARY ACCESS VARIABLE DIRECTLY TO BROWSER
                    st.session_state["token"] = payload["access_token"]
                    st.session_state["role"] = payload["role"]
                    st.success("Access Granted! Syncing business framework...")
                    st.rerun()  # INSTANTLY RE-RENDERS APPLICATION VIEWPOINT TO LOAD CORE DASHBOARD MODULES
                else:
                    st.error("Authentication Refused: Incorrect access credentials mismatch.")
            except requests.exceptions.RequestException as e:
                st.error(f"Platform Connection Interrupted: {str(e)}")

    # SUB-MODULE : PROFILE REGISTRATION LOGIC
    with tab2:
        st.subheader("Register New Employee Profile")
        reg_name = st.text_input("Full Employee Name")
        reg_email = st.text_input("Work Email Address")
        reg_password = st.text_input("Create Security Password", type="password")
        # ENFORCES RESTRICTED ROLE STRUCTURES MAPPED EXACTLY ONTO THE backend RBAC MATRIX
        reg_role = st.selectbox("Assign Authorized Business Role",
                                ["business_owner", "store_manager", "sales_executive", "admin"])

        if st.button("Register Account", use_container_width=True):
            try:
                # SEND EXPLICIT CREATION ENTITY PACKAGE TO backend DATASTORE SCHEMA
                response = requests.post(f"{BACKEND_URL}/register", json={
                    "name": reg_name,
                    "email": reg_email,
                    "password": reg_password,
                    "role": reg_role
                })
                if response.status_code == 200:
                    st.success("Account created successfully! Switch to Sign In tab link.")
                else:
                    # SAFELY EXTRACT STRUCTURED VALIDATION DETAIL KEY PR [ARSE RAW TEXT STRING
                    try:
                        error_msg = response.json().get('detail', 'Validation Failure.')
                    except ValueError:  # Specifically catching JSON decoding errors
                        error_msg = response.text
                    st.error(f"Registration Blocked: {error_msg}")
            except requests.exceptions.RequestException as e:  # Specific exception clearing the PyCharm warning
                st.error(f"Cannot trace active route gateway back to backend layer. Error: {str(e)}")

#--------------------------------------------
# 3. CORE RUNTIME / AUTHORIZED DASHBOARD VIEW
#--------------------------------------------

# CONDITION B : AUTHENTICATED SESSION STATE -> DISPLAY CORE ORGANIZATIONAL METRICS DASHBOARD
else:
    st.title("📊 MarketMind AI Business Operations Engine")
    # MODULE : SIDEBAR NAVIGATION & AUDITING CONTEXT
    st.sidebar.markdown(f"### 🛡️ Operational Identity Context")
    st.sidebar.info(f"**Privilege Scope:** `{st.session_state['role'].upper()}`")

    # CLEAN CACHE BREAKDOWN ROUTINE FOR SECURE EXPLICIT SESSION TERMINATIONS
    if st.sidebar.button("Log Out & Terminate Session", use_container_width=True):
        st.session_state["token"] = None
        st.session_state["role"] = None
        st.rerun()

    # DEFINE HIGH-LEVEL MODULAR DASHBOARD SEPARATION ARCHITECTURE MAPPING ENTERPRISE DIVISION
    tab_sales, tab_forecast, tab_invoices, tab_admin, tab_inventory = st.tabs([
        "💰 Executive KPI Metrics Summary",
        "📈 Time-Series Trend Projections",
        "🧾 Invoices Registry Management",
        "⚙️ Core System Governance",
        "📦 Inventory Preview"
    ])

    # INJECT AUTHORIZATION HEADER CONTEXT USING STANDARD SECURITY BEARER FORMATTING MODELS
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    # TAB A MODULE : CORPORATE EXECUTIVE API HANDLING
    with tab_sales:
        st.header("Executive Sales Summaries & Volume Aggregates")
        res = requests.get(f"{BACKEND_URL}/sales/summary", headers=headers)
        if res.status_code == 200:
            data = res.json()
            # SPLIT SCREEN INTO THREE COLUMNS DYNAMICALLY USING MODERN METRIC STRUCTURES
            col1, col2, col3 = st.columns(3)
            col1.metric("Calculated Total Gross Revenue", f"${data['total_revenue']:,}")
            col2.metric("Valid Orders Parsed", f"{data['total_orders']:,}")
            col3.metric("Top Volumetric Contributor", data['top_product'])
        else:
            st.error(f"🛑 Access Denied: {res.json().get('detail', 'Role criteria mismatch.')}")

    # TAB B MODULE : REVENUE FORECASTING CONTROLS
    with tab_forecast:
        st.header("Predictive Sales Trend Framework Grid")
        res = requests.get(f"{BACKEND_URL}/forecast/revenue", headers=headers)
        if res.status_code == 200:
            data = res.json()
            st.success(f"Connection Connected. Security Scope: {data['status']}")
            st.json(data["sample_forecast_trends"]) #RENDER STRUCTED DATA MODELS CLEANLY
        else:
            st.error(f"🛑 Access Denied: {res.json().get('detail', 'Role criteria mismatch.')}")

    # TAB C MODULE : INVOICE TRANSACTION ARCHIVE DATA
    with tab_invoices:
        st.header("Invoices Voucher ledger Matrix Archive")

        # DYNAMIC VALIDATION FLOW #1 : READ TRANSACTIONAL REGISTRY LOG BLOCKS
        view_res = requests.get(f"{BACKEND_URL}/invoices/view", headers=headers)
        if view_res.status_code == 200:
            st.info(f"📁 Database Tracking Status: {view_res.json().get('message')}")
        else:
            st.error("Gating Matrix Blocked your role context from tracking invoice logs.")

        st.markdown("---")
        st.subheader("Transactional Operations Layer")

        # DYNAMIC VALIDATION FLOW #2 : CREATE NEW LEDGER MUTATION (WRITE OPERATIONS)
        if st.button("Instantiate New Structural Invoice Ledger Entry"):
            create_res = requests.post(f"{BACKEND_URL}/invoices/create", headers=headers)
            if create_res.status_code == 200:
                st.success(f"⚡ Voucher Committed Successfully: {create_res.json().get('message')}")
            else:
                st.error(f"🚫 Security Core Blocked Action: {create_res.json().get('detail')}")

    # TAB D MODULE : SYSTEM GOVERNANCE (ADMIN STRATUM CONTROL)
    with tab_admin:
        st.header("Identity Workspace Governance Space Control")
        res = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
        if res.status_code == 200:
            st.warning("⚠️ Critical Identity Domain Scope Active.")
            st.write("Registered Account In-Memory Entities Profile Directory:",
                     res.json().get("registered_user_profiles"))
        else:
            st.error(f"🛑 Access Denied: {res.json().get('detail')}")

    # TAB E: MILESTONE 2 INVENTORY PREVIEW
    with tab_inventory:
        st.header("📦 Milestone 2 — Inventory Preview")

        st.write(
            "Estimated inventory generated from your "
            "UCI Online Retail II sales data."
        )

        st.info(
            "The Inventory"
        )

        if st.button("Load Inventory Preview", use_container_width=True):

            try:
                with st.spinner("Loading inventory data..."):

                    inventory_res = requests.get(
                        f"{BACKEND_URL}/milestone2/preview",
                        headers=headers,
                        timeout=120
                    )

                if inventory_res.status_code == 200:
                    inventory_data = inventory_res.json()

                    st.success(
                        inventory_data.get(
                            "message",
                            "Inventory preview loaded"
                        )
                    )

                    # SUMMARY METRICS
                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Total Products",
                        f"{inventory_data.get('total_products', 0):,}"
                    )

                    col2.metric(
                        "Total Units Sold",
                        f"{inventory_data.get('total_units_sold', 0):,}"
                    )

                    col3.metric(
                        "Estimated Remaining Stock",
                        f"{inventory_data.get('total_estimated_remaining_stock', 0):,}"
                    )

                    st.markdown("---")

                    st.subheader("Inventory Product Records")

                    products = inventory_data.get("products", [])

                    if products:
                        st.dataframe(
                            products,
                            use_container_width=True,
                            hide_index=True
                        )

                        csv_data = requests.models.complexjson.dumps(
                            products,
                            indent=2
                        )

                        st.download_button(
                            label="Download Inventory JSON",
                            data=csv_data,
                            file_name="marketmind_inventory_preview.json",
                            mime="application/json"
                        )

                    else:
                        st.warning("No inventory product records returned.")

                    st.caption(
                        inventory_data.get(
                            "note",
                            "Inventory values are estimates."
                        )
                    )

                else:
                    st.error(
                        f"Inventory API error "
                        f"({inventory_res.status_code}): "
                        f"{inventory_res.text}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to backend: {e}")

        # --------------------------------------------------
        # TAB E: ADMIN / GOVERNANCE
        # --------------------------------------------------

    with tab_admin:
        st.header("Identity Workspace Governance")

        try:
            res = requests.get(
                f"{BACKEND_URL}/admin/users",
                headers=headers,
                timeout=30
            )

            if res.status_code == 200:
                st.warning("Identity administration endpoint connected.")

                st.write(
                    "Registered User Profiles:",
                    res.json().get("registered_user_profiles", [])
                )
            else:
                st.error(f"Admin API error: {res.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Backend connection error: {e}")