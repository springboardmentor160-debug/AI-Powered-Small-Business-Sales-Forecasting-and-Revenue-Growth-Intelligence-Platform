# MarketMind AI — 5-7 Minute Live Demo Script & Contingency Plan

This script guides the presenter step-by-step through a flawless 5–7 minute live software demonstration for mentors, evaluators, and stakeholders.

---

## ⏱️ Step-by-Step Demo Flow (Total: 6 Minutes)

### Phase 1: Authentication & Dashboard Overview (0:00 – 1:30)
1. **Show the Login / Header Hero**:
   - Open [http://localhost:8501](http://localhost:8501) in your browser.
   - Point out the active user role badge (`Business Owner`) and scope (`Global Network`).
   - Mention the dark SaaS UI, custom typography, and real-time KPI overview (Gross Revenue, Total Transactions, Units Sold).
2. **Demonstrate POS Transaction Simulator**:
   - Scroll down to the **Live Transaction Simulator** on Tab 1.
   - Select product `PRD-001 (Wireless Mouse)`, quantity `2`, store `STORE-001`, payment `UPI`.
   - Click **➕ Record Sale**.
   - Point out the instant success notification with the generated transaction ID and show the KPI cards update dynamically.

### Phase 2: Role-Based Access Control Verification (1:30 – 2:45)
1. **Switch to Store Manager**:
   - In the left sidebar under **Role Quick Switcher**, click **🏬 Manager**.
   - Show that the Store Scope automatically locks to `STORE-001 (Enforced Store Scope)`.
   - Point out how the revenue numbers dynamically adjust to reflect only `STORE-001`.
2. **Demonstrate 403 Forbidden Enforcement (Sales Executive)**:
   - Click **💼 Exec** in the sidebar.
   - Click on the **📈 Sales Forecasting** tab.
   - Show the prominent red **Access Restricted** security banner explaining that Sales Executives do not have permissions to access strategic sales forecasting reports under RBAC policy.
   - Explain: *"This is enforced both on the frontend UI and securely at the FastAPI route level via HTTP 403."*

### Phase 3: Customer Behavioral Segments & 3D Visualization (2:45 – 4:00)
1. **Switch back to Business Owner**:
   - Click **👑 Owner** in the sidebar.
   - Navigate to the **👥 Customer Segments** tab.
2. **Review Segmentation Metrics**:
   - Highlight the 4 KPI cards: 25 customer profiles, dominant segment, 36% at-risk inactivity, and 0.856 ARI consensus score.
3. **Interact with the 3D Scatter Plot**:
   - Rotate the interactive 3D Plotly visualization showing Order Frequency, Average Spend, and Days Inactive.
   - Hover over a VIP customer (`CUST-1009`) and an At-Risk customer (`CUST-1002`).
4. **Live 404 Customer ID Verification**:
   - Open the **🔎 Instant Customer ID Verification** expander.
   - Enter `NONEXISTENT_999` and click **Verify Customer ID**.
   - Show the clear `❌ Not Found (404)` message.
   - Enter `CUST-1001` and show the verified customer profile card.

### Phase 4: Sales Forecasting & Excel Business Report Download (4:00 – 5:30)
1. **Navigate to Tab 3 (Sales Forecasting)**:
   - Point out the projected 30-day revenue (₹25,257.31) and the winning model (`Prophet`).
   - Show the interactive timeline chart with the 80% confidence bound shading.
2. **Inspect Model Evaluation Table**:
   - Scroll down to the **Model Architecture Benchmark** table showing Prophet (Winner, RMSE 570.02), Random Forest (RMSE 606.18), and XGBoost (RMSE 684.06).
3. **Download Excel Executive Briefing**:
   - Click the green button **📥 Download Report (30d)**.
   - Open the downloaded `MarketMind_Report_30d.xlsx` in Excel or LibreOffice.
   - Show both sheets: `Customer Segments` with formatted Rupee amounts, and `Sales Forecast` with daily projected revenue.

### Phase 5: Architecture & Q&A Wrap-up (5:30 – 6:30)
- Briefly show the Swagger API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) and the `/health` endpoint.
- Conclude: *"MarketMind AI delivers an end-to-end, resilient intelligence platform ready for cloud deployment. Thank you, and I look forward to your questions."*

---

## 🛡️ Backup & Contingency Plan (If Anything Unexpected Occurs)

| Potential Failure Point | Root Cause | Immediate Backup Action During Demo |
| :--- | :--- | :--- |
| **Streamlit Page shows "Backend Offline"** | FastAPI server was stopped or port changed. | Open terminal and run `python -m uvicorn backend.main:app --port 8000 --reload`. Refresh browser. The UI gracefully reconnects without losing state. |
| **Port 8000 or 8501 is busy** | Another process is occupying the port. | Run `python start_unified.py` which automatically binds the internal daemon and opens Streamlit on an available port. |
| **Excel does not open on demo machine** | Machine lacks Microsoft Excel or desktop viewer. | Display the pre-generated Excel artifact `artifacts/business_report.xlsx` directly via the terminal or Python preview, or view the interactive dataframe table inside the Streamlit UI. |
| **Network latency causes slow model rerun** | First-time computation overhead. | Mention that forecast results are cached using `@st.cache_data(ttl=300)`, ensuring sub-second response times on subsequent interactions. |
