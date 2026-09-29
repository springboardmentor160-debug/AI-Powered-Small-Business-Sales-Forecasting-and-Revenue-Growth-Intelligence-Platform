/**
 * MarketMind AI — Enterprise Sales & Customer Intelligence Platform
 * Redesigned UI/UX Frontend Application Logic
 */

const API_BASE = '/api';

// Application State
let currentUser = null;
let authToken = localStorage.getItem('access_token') || null;

// Loaded Analytics Telemetry State
let overviewData = null;
let segSummaryData = null;
let customerListData = [];
let fcstPredictionsData = null;
let fcstMetricsData = null;
let regionalData = null;
let categoryData = null;
let currentForecastModel = 'Prophet';

// Active Role View Group State
let activeRoleGroup = null;

// Chart Instances Registry
let charts = {};

document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    setupEventListeners();
});

/* Initialize Global Event Listeners */
function setupEventListeners() {
    // Password Visibility Eye Toggle
    const btnToggleEye = document.getElementById('btn-toggle-password');
    if (btnToggleEye) {
        btnToggleEye.addEventListener('click', togglePasswordVisibility);
    }

    // Login Form Submit
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    // Logout Button
    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
        btnLogout.addEventListener('click', handleLogout);
    }

    // Refresh Data Button
    const btnRefresh = document.getElementById('btn-refresh');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', loadDashboardData);
    }

    // Mobile Sidebar Toggle
    const btnMobileMenu = document.getElementById('btn-mobile-menu');
    if (btnMobileMenu) {
        btnMobileMenu.addEventListener('click', () => {
            document.getElementById('app-sidebar').classList.toggle('mobile-open');
        });
    }

    // Demo Accounts Quick Selection
    document.querySelectorAll('.btn-demo-role').forEach(btn => {
        btn.addEventListener('click', () => {
            const emailInput = document.getElementById('login-email');
            const passInput = document.getElementById('login-password');
            if (emailInput && passInput) {
                emailInput.value = btn.dataset.email;
                passInput.value = btn.dataset.pass;
                handleLoginSubmit(new Event('submit'));
            }
        });
    });

    // Forecast Model Toggle Buttons (Business Owner view)
    document.querySelectorAll('.btn-model-select').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.btn-model-select').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentForecastModel = btn.dataset.model;
            renderForecastCharts();
        });
    });

    // Customer Directory Filters & Search for Sales Executive
    const seSearch = document.getElementById('se-search-input');
    if (seSearch) {
        seSearch.addEventListener('input', handleCustomerSearch);
    }
    const seFilter = document.getElementById('se-segment-filter');
    if (seFilter) {
        seFilter.addEventListener('change', handleCustomerFilterChange);
    }

    // Admin User Creation Form
    const adminCreateForm = document.getElementById('admin-create-user-form');
    if (adminCreateForm) {
        adminCreateForm.addEventListener('submit', handleAdminCreateUserSubmit);
    }
}

/* Password Toggle Function */
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('login-password');
    const eyeIcon = document.getElementById('eye-icon');
    if (!passwordInput || !eyeIcon) return;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeIcon.className = 'fa-regular fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        eyeIcon.className = 'fa-regular fa-eye';
    }
}

/* Authenticated Fetch Wrapper */
async function authFetch(endpoint, options = {}) {
    const headers = options.headers || {};
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    headers['Content-Type'] = 'application/json';

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        handleLogout();
        throw new Error('Session expired or unauthorized. Please log in.');
    }
    if (response.status === 403) {
        const err = await response.json().catch(() => ({ detail: 'Permission denied.' }));
        alert(`Access Denied: ${err.detail || 'Insufficient permissions for this role.'}`);
        throw new Error(`Forbidden: ${err.detail}`);
    }
    if (!response.ok) {
        const errJson = await response.json().catch(() => ({ detail: `Server error (${response.status})` }));
        throw new Error(errJson.detail || `Server error (${response.status})`);
    }
    return response;
}

/* Authentication Initialization */
async function initAuth() {
    if (!authToken) {
        showLoginModal();
        return;
    }
    try {
        const res = await authFetch('/auth/me');
        if (res.ok) {
            currentUser = await res.json();
            showAppLayout();
        } else {
            handleLogout();
        }
    } catch (e) {
        handleLogout();
    }
}

async function handleLoginSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();

    const emailInput = document.getElementById('login-email');
    const passwordInput = document.getElementById('login-password');
    const submitBtn = document.getElementById('btn-login-submit');
    const errorEl = document.getElementById('login-error');

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    errorEl.style.display = 'none';
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>AUTHENTICATING...</span>';
    }

    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({ detail: 'Invalid login credentials.' }));
            errorEl.textContent = errData.detail || 'Invalid email or password.';
            errorEl.style.display = 'block';
            return;
        }

        const data = await res.json();
        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('access_token', authToken);

        showAppLayout();
    } catch (err) {
        errorEl.textContent = 'Unable to connect to MarketMind backend server. Please check connection.';
        errorEl.style.display = 'block';
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> <span>SIGN IN</span>';
        }
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('access_token');
    showLoginModal();
}

function showLoginModal() {
    const loginModal = document.getElementById('login-modal');
    const appLayout = document.getElementById('app-layout');
    if (loginModal) loginModal.style.display = 'flex';
    if (appLayout) appLayout.style.display = 'none';
}

function showAppLayout() {
    const loginModal = document.getElementById('login-modal');
    const appLayout = document.getElementById('app-layout');
    if (loginModal) loginModal.style.display = 'none';
    if (appLayout) appLayout.style.display = 'flex';

    // Update Header Profile Badge
    document.getElementById('user-name-display').textContent = currentUser.name || currentUser.email;
    document.getElementById('user-role-badge').textContent = currentUser.role;

    const avatarEl = document.getElementById('user-avatar');
    if (avatarEl && currentUser.name) {
        avatarEl.textContent = currentUser.name.charAt(0).toUpperCase();
    }

    // Build Role-Specific Navigation and View Group
    setupRoleNavigation(currentUser.role);
    loadDashboardData();
}

/* ==========================================================================
   ROLE-BASED DYNAMIC NAVIGATION & VIEW SETUP (REQUIREMENT #4)
   ========================================================================== */

function setupRoleNavigation(role) {
    const navContainer = document.getElementById('dynamic-nav-container');
    const navLabel = document.getElementById('role-nav-label');
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    const roleGroups = document.querySelectorAll('.role-view-group');

    // Hide all view groups
    roleGroups.forEach(g => g.style.display = 'none');

    let navItems = [];
    let targetGroupId = '';

    if (role === 'Business Owner') {
        targetGroupId = 'view-group-business-owner';
        if (navLabel) navLabel.textContent = 'Executive Navigation';
        if (pageTitle) pageTitle.textContent = 'Business Owner Overview';
        if (pageSubtitle) pageSubtitle.textContent = 'Executive revenue performance, growth forecasts & business insights';

        navItems = [
            { id: 'view-bo-overview', label: 'Executive Overview', icon: 'fa-table-cells-large' },
            { id: 'view-bo-sales', label: 'Sales & Regions', icon: 'fa-chart-pie' },
            { id: 'view-bo-customers', label: 'Customer Value', icon: 'fa-users' },
            { id: 'view-bo-forecast', label: 'Sales Forecast', icon: 'fa-arrow-trend-up' },
            { id: 'view-bo-reports', label: 'Business Reports', icon: 'fa-file-contract' }
        ];
    } else if (role === 'Store Manager') {
        targetGroupId = 'view-group-store-manager';
        if (navLabel) navLabel.textContent = 'Store Manager Ops';
        if (pageTitle) pageTitle.textContent = 'Store Operations Dashboard';
        if (pageSubtitle) pageSubtitle.textContent = 'Operational sales trends, product categories & inventory status';

        navItems = [
            { id: 'view-sm-overview', label: 'Operations Overview', icon: 'fa-store' },
            { id: 'view-sm-categories', label: 'Categories & Margins', icon: 'fa-table-list' },
            { id: 'view-sm-regions', label: 'Regional Analytics', icon: 'fa-map-location-dot' },
            { id: 'view-sm-forecast', label: 'Operational Forecast', icon: 'fa-arrow-trend-up' },
            { id: 'view-sm-reports', label: 'Store Reports', icon: 'fa-file-contract' }
        ];
    } else if (role === 'Sales Executive') {
        targetGroupId = 'view-group-sales-executive';
        if (navLabel) navLabel.textContent = 'Sales Portfolio Nav';
        if (pageTitle) pageTitle.textContent = 'Sales Executive Portfolio';
        if (pageSubtitle) pageSubtitle.textContent = 'Customer account portfolio, high-value champions & at-risk alerts';

        navItems = [
            { id: 'view-se-overview', label: 'Portfolio Overview', icon: 'fa-address-book' },
            { id: 'view-se-directory', label: 'Account Directory', icon: 'fa-users-viewfinder' },
            { id: 'view-se-segments', label: 'Customer Segments', icon: 'fa-sliders' },
            { id: 'view-se-forecast', label: 'Sales Targets', icon: 'fa-chart-line' },
            { id: 'view-se-reports', label: 'Sales Reports', icon: 'fa-file-contract' }
        ];
    } else if (role === 'Administrator') {
        targetGroupId = 'view-group-admin';
        if (navLabel) navLabel.textContent = 'Platform Administration';
        if (pageTitle) pageTitle.textContent = 'System Administration';
        if (pageSubtitle) pageSubtitle.textContent = 'User management, database telemetry & ML model benchmark evaluation';

        navItems = [
            { id: 'view-admin-overview', label: 'System Overview', icon: 'fa-shield-halved' },
            { id: 'view-admin-users', label: 'User Management', icon: 'fa-users-gear' },
            { id: 'view-admin-models', label: 'ML Model Evaluation', icon: 'fa-sliders' },
            { id: 'view-admin-data', label: 'Data Telemetry', icon: 'fa-server' },
            { id: 'view-admin-reports', label: 'System Reports', icon: 'fa-file-contract' }
        ];
    }

    // Display active role view group
    const activeGroup = document.getElementById(targetGroupId);
    if (activeGroup) activeGroup.style.display = 'block';

    // Render Navigation Buttons
    if (navContainer) {
        navContainer.innerHTML = navItems.map((item, idx) => `
            <button class="nav-item ${idx === 0 ? 'active' : ''}" data-view="${item.id}">
                <i class="fa-solid ${item.icon}"></i>
                <span>${item.label}</span>
            </button>
        `).join('');

        // Attach click handlers to nav buttons
        navContainer.querySelectorAll('.nav-item').forEach(btn => {
            btn.onclick = () => {
                const targetViewId = btn.dataset.view;
                navContainer.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Switch Tab Content in current role group
                if (activeGroup) {
                    activeGroup.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                    const targetPane = document.getElementById(targetViewId);
                    if (targetPane) targetPane.classList.add('active');
                }

                // Lazy load tab data if required
                if (targetViewId.endsWith('-reports')) {
                    loadReportForRole(role, 'segmentation');
                } else if (targetViewId === 'view-admin-users' && role === 'Administrator') {
                    fetchAdminUsersList();
                }

                // Close mobile menu if active
                const sidebar = document.getElementById('app-sidebar');
                if (sidebar) sidebar.classList.remove('mobile-open');
            };
        });
    }

    // Attach click handlers to report buttons inside role view
    if (activeGroup) {
        activeGroup.querySelectorAll('.btn-report-item').forEach(rBtn => {
            rBtn.onclick = () => {
                activeGroup.querySelectorAll('.btn-report-item').forEach(b => b.classList.remove('active'));
                rBtn.classList.add('active');
                loadReportForRole(role, rBtn.dataset.report);
            };
        });
    }
}

/* Master Data Telemetry Loader */
async function loadDashboardData() {
    try {
        await Promise.all([
            fetchRoleDashboardInsights(),
            fetchOverviewData(),
            fetchRegionalAnalyticsData(),
            fetchCategoryAnalyticsData(),
            fetchSegmentationSummaryData(),
            fetchCustomerDirectoryData(),
            fetchForecastingPredictionsData(),
            fetchForecastingMetricsData()
        ]);
        console.log('[MarketMind AI] Dashboard telemetry updated cleanly from backend API & PostgreSQL.');
    } catch (err) {
        console.error('Error loading dashboard telemetry:', err);
    }
}

/* 1. Fetch Dynamic Role Insights from Backend */
async function fetchRoleDashboardInsights() {
    let endpoint = '/dashboard/business-owner';
    if (currentUser.role === 'Store Manager') endpoint = '/dashboard/store-manager';
    else if (currentUser.role === 'Sales Executive') endpoint = '/dashboard/sales-executive';
    else if (currentUser.role === 'Administrator') endpoint = '/dashboard/admin';

    try {
        const res = await authFetch(endpoint);
        const data = await res.json();
        renderInsights(data.insights);

        // Populate role-specific top KPI Cards from dashboard response
        if (currentUser.role === 'Store Manager') {
            const smSales = document.getElementById('sm-kpi-sales');
            const smRegion = document.getElementById('sm-kpi-region');
            const smCat = document.getElementById('sm-kpi-category');
            const smInv = document.getElementById('sm-kpi-inventory');

            if (smSales) smSales.textContent = `$${(data.total_sales || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            if (smRegion) smRegion.textContent = data.top_region || 'N/A';
            if (smCat) smCat.textContent = data.top_category || 'N/A';
            if (smInv) smInv.textContent = (data.total_inventory_items || 0).toLocaleString();

        } else if (currentUser.role === 'Sales Executive') {
            const seCust = document.getElementById('se-kpi-customers');
            const seAov = document.getElementById('se-kpi-aov');
            const seAtrisk = document.getElementById('se-kpi-atrisk');
            const seChamp = document.getElementById('se-kpi-champions');

            if (seCust) seCust.textContent = (data.total_customers || 0).toLocaleString();
            if (seAov) seAov.textContent = `$${(data.avg_order_value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            if (seAtrisk) seAtrisk.textContent = (data.at_risk_count || 0).toLocaleString();
            if (seChamp) seChamp.textContent = (data.champions_count || 0).toLocaleString();

        } else if (currentUser.role === 'Administrator') {
            const adUsers = document.getElementById('admin-kpi-users');
            const adTx = document.getElementById('admin-kpi-transactions');
            const adCust = document.getElementById('admin-kpi-customers');
            const adModel = document.getElementById('admin-kpi-model');

            if (adUsers) adUsers.textContent = (data.total_users || 0).toLocaleString();
            if (adTx) adTx.textContent = (data.total_transactions || 0).toLocaleString();
            if (adCust) adCust.textContent = (data.total_customers || 0).toLocaleString();
            if (adModel) adModel.textContent = data.best_model || 'Prophet';
        }
    } catch (e) {
        console.warn('Could not load role dashboard insights:', e);
    }
}

/* Render Dynamic Natural Language Insights Banner */
function renderInsights(insights) {
    const container = document.getElementById('insights-container');
    if (!container) return;

    if (!insights || insights.length === 0) {
        container.innerHTML = '<div class="insight-card-item"><p class="insight-message-text">No data available for current selection.</p></div>';
        return;
    }

    container.innerHTML = insights.map(i => `
        <div class="insight-card-item insight-${i.type || 'info'}">
            <div class="insight-header-row">
                <i class="fa-solid ${getInsightIcon(i.type)}"></i>
                <h4>${i.title}</h4>
            </div>
            <p class="insight-message-text">${i.message}</p>
        </div>
    `).join('');
}

function getInsightIcon(type) {
    if (type === 'warning') return 'fa-triangle-exclamation';
    if (type === 'success' || type === 'positive') return 'fa-circle-check';
    if (type === 'caution') return 'fa-circle-exclamation';
    return 'fa-lightbulb';
}

/* 2. Fetch Overview Data */
async function fetchOverviewData() {
    try {
        const res = await authFetch('/overview');
        overviewData = await res.json();

        // Business Owner Top KPIs
        const boRev = document.getElementById('bo-kpi-revenue');
        const boOrders = document.getElementById('bo-kpi-orders');
        if (boRev) boRev.textContent = `$${overviewData.total_sales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        if (boOrders) boOrders.textContent = overviewData.total_orders.toLocaleString();

    } catch (e) {
        console.error('Error fetching overview data:', e);
    }
}

/* 3. Fetch Regional Analytics */
async function fetchRegionalAnalyticsData() {
    try {
        const res = await authFetch('/analytics/regions');
        regionalData = await res.json();
        renderRegionalCharts();
    } catch (e) {
        console.error('Error fetching regional analytics:', e);
    }
}

/* 4. Fetch Category Analytics */
async function fetchCategoryAnalyticsData() {
    try {
        const res = await authFetch('/analytics/categories');
        categoryData = await res.json();

        // Compute Business Owner Total Net Profit from category profits
        if (categoryData && currentUser.role === 'Business Owner') {
            const totalProfit = categoryData.reduce((acc, c) => acc + (c.profit || 0), 0);
            const boProfit = document.getElementById('bo-kpi-profit');
            if (boProfit) boProfit.textContent = `$${totalProfit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }

        renderCategoryChartsAndTables();
    } catch (e) {
        console.error('Error fetching category analytics:', e);
    }
}

/* 5. Fetch Segmentation Summary */
async function fetchSegmentationSummaryData() {
    try {
        const res = await authFetch('/segmentation/summary');
        segSummaryData = await res.json();

        // Populate Segment Filter options for Sales Executive
        const seFilterSelect = document.getElementById('se-segment-filter');
        if (seFilterSelect && segSummaryData.cluster_summary) {
            seFilterSelect.innerHTML = '<option value="">All Customer Segments</option>';
            segSummaryData.cluster_summary.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.segment_name;
                opt.textContent = `${c.segment_name} (${c.customer_count} accounts)`;
                seFilterSelect.appendChild(opt);
            });
        }

        renderSegmentationCharts();
    } catch (e) {
        console.error('Error fetching segmentation summary:', e);
    }
}

/* 6. Fetch Customer Portfolio Directory */
async function fetchCustomerDirectoryData(segment = '') {
    try {
        const url = segment ? `/segmentation/customers?limit=100&segment=${encodeURIComponent(segment)}` : '/segmentation/customers?limit=100';
        const res = await authFetch(url);
        const data = await res.json();
        customerListData = data.customers || [];
        renderCustomerTables(customerListData);
    } catch (e) {
        console.error('Error fetching customer directory:', e);
    }
}

function renderCustomerTables(customers) {
    // Render for Sales Executive customer table
    const seTbody = document.querySelector('#se-customer-table tbody');
    const seDirTbody = document.querySelector('#se-directory-table tbody');

    [seTbody, seDirTbody].forEach(tbody => {
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!customers || customers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:20px;">No data available</td></tr>';
            return;
        }

        customers.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code>${c.customer_id}</code></td>
                <td><strong>${c.customer_name}</strong></td>
                <td><span class="tag-badge gold">${c.segment_name}</span></td>
                <td>${c.recency_days} days</td>
                <td>${c.frequency_orders} orders</td>
                <td>$${c.monetary_sales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td>$${c.avg_order_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td>${(c.avg_discount * 100).toFixed(1)}%</td>
            `;
            tbody.appendChild(tr);
        });
    });
}

function handleCustomerSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
        renderCustomerTables(customerListData);
        return;
    }
    const filtered = customerListData.filter(c => 
        (c.customer_name && c.customer_name.toLowerCase().includes(query)) ||
        (c.customer_id && c.customer_id.toLowerCase().includes(query)) ||
        (c.segment_name && c.segment_name.toLowerCase().includes(query))
    );
    renderCustomerTables(filtered);
}

function handleCustomerFilterChange(e) {
    fetchCustomerDirectoryData(e.target.value);
}

/* 7. Fetch Forecasting Predictions & Dynamic Growth Callout */
async function fetchForecastingPredictionsData() {
    try {
        const res = await authFetch('/forecasting/predictions');
        fcstPredictionsData = await res.json();

        // Calculate dynamic forecast growth statistics for Business Owner (Requirement #5)
        if (fcstPredictionsData && fcstPredictionsData.data) {
            const records = fcstPredictionsData.data;
            const historical = records.filter(r => r.y !== null).map(r => r.y);
            const future = records.filter(r => r.y === null && r.prophet_yhat !== null).map(r => r.prophet_yhat);

            if (historical.length >= 12 && future.length >= 12) {
                const recentSales = historical.slice(-12).reduce((a, b) => a + b, 0);
                const projectedSales = future.slice(0, 12).reduce((a, b) => a + b, 0);
                const diff = projectedSales - recentSales;
                const pctChange = recentSales > 0 ? (diff / recentSales) * 100 : 0.0;

                const growthEl = document.getElementById('bo-kpi-growth');
                const growthSubEl = document.getElementById('bo-kpi-growth-sub');
                if (growthEl) growthEl.textContent = `${pctChange >= 0 ? '+' : ''}${pctChange.toFixed(1)}%`;
                if (growthSubEl) growthSubEl.textContent = pctChange >= 0 ? 'Projected Increase' : 'Projected Contraction';

                // Update Forecast Callout Highlight Box
                const calloutSales = document.getElementById('bo-callout-sales');
                const calloutPct = document.getElementById('bo-callout-pct');
                const calloutTrend = document.getElementById('bo-callout-trend');
                const calloutText = document.getElementById('bo-callout-text');

                if (calloutSales) calloutSales.textContent = `$${projectedSales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                if (calloutPct) calloutPct.textContent = `${pctChange >= 0 ? '+' : ''}${pctChange.toFixed(1)}%`;

                if (calloutTrend) {
                    calloutTrend.className = pctChange >= 0 ? 'callout-trend' : 'callout-trend warning';
                    calloutTrend.innerHTML = pctChange >= 0 
                        ? `<i class="fa-solid fa-arrow-up"></i> <span>+${pctChange.toFixed(1)}%</span> compared with previous period`
                        : `<i class="fa-solid fa-arrow-down"></i> <span>${pctChange.toFixed(1)}%</span> compared with previous period`;
                }

                if (calloutText) {
                    calloutText.textContent = pctChange >= 0
                        ? `"Sales are projected to increase by approximately $${diff.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (+${pctChange.toFixed(1)}%) compared with the previous period."`
                        : `"Sales are projected to contract by approximately $${Math.abs(diff).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${pctChange.toFixed(1)}%) compared with the previous period."`;
                }
            }
        }

        renderForecastCharts();
    } catch (e) {
        console.error('Error fetching forecast predictions:', e);
    }
}

/* 8. Fetch Forecasting Model Benchmark Metrics */
async function fetchForecastingMetricsData() {
    try {
        const res = await authFetch('/forecasting/metrics');
        fcstMetricsData = await res.json();
        renderModelEvaluationTablesAndCharts();
    } catch (e) {
        console.error('Error fetching forecast metrics:', e);
    }
}

/* Strategic Markdown Report Loader */
async function loadReportForRole(role, reportName) {
    let targetContentId = 'bo-report-content';
    if (role === 'Store Manager') targetContentId = 'sm-report-content';
    else if (role === 'Sales Executive') targetContentId = 'se-report-content';
    else if (role === 'Administrator') targetContentId = 'admin-report-content';

    const box = document.getElementById(targetContentId);
    if (!box) return;

    box.innerHTML = '<div class="loading-skeleton-box"><i class="fa-solid fa-spinner fa-spin"></i> Loading strategic report...</div>';

    try {
        const res = await authFetch(`/reports/${reportName}`);
        if (!res.ok) {
            const errObj = await res.json().catch(() => ({ detail: `Server error (${res.status})` }));
            throw new Error(errObj.detail || `Server error (${res.status})`);
        }
        const data = await res.json();
        if (window.marked && data.content) {
            box.innerHTML = marked.parse(data.content);
        } else {
            box.innerText = data.content || 'No report content available.';
        }
    } catch (e) {
        box.innerHTML = `<p style="color:#DC2626; padding:16px;">Failed to load report: ${e.message}</p>`;
    }
}

/* Fetch Admin System Accounts List */
async function fetchAdminUsersList() {
    try {
        const res = await authFetch('/admin/users');
        const users = await res.json();
        const tbody = document.querySelector('#admin-users-list-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        if (!users || users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No data available</td></tr>';
            return;
        }

        users.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code>${u.id}</code></td>
                <td><strong>${u.name}</strong></td>
                <td>${u.email}</td>
                <td><span class="tag-badge gold">${u.role}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error('Could not fetch admin users list:', e);
    }
}

async function handleAdminCreateUserSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('admin-new-name').value.trim();
    const email = document.getElementById('admin-new-email').value.trim();
    const role = document.getElementById('admin-new-role').value;
    const password = document.getElementById('admin-new-password').value;
    const msgEl = document.getElementById('admin-user-action-msg');

    msgEl.style.display = 'none';

    try {
        const res = await authFetch('/admin/users', {
            method: 'POST',
            body: JSON.stringify({ name, email, role, password })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Error creating platform user.' }));
            msgEl.textContent = err.detail || 'Error creating platform user.';
            msgEl.style.background = '#FEE2E2';
            msgEl.style.color = '#991B1B';
            msgEl.style.display = 'block';
            return;
        }

        msgEl.textContent = `Account created successfully for '${name}' (${role}).`;
        msgEl.style.background = '#D1FAE5';
        msgEl.style.color = '#065F46';
        msgEl.style.display = 'block';

        document.getElementById('admin-create-user-form').reset();
        fetchAdminUsersList();
    } catch (err) {
        msgEl.textContent = 'Failed to create user account.';
        msgEl.style.background = '#FEE2E2';
        msgEl.style.color = '#991B1B';
        msgEl.style.display = 'block';
    }
}

/* ==========================================================================
   CHART RENDERING METHODS (EMERALD INK & CHAMPAGNE ACCENTS)
   ========================================================================== */

function renderRegionalCharts() {
    if (!regionalData) return;

    ['boRegionalChart', 'smRegionalChart', 'smRegionalFullChart'].forEach(canvasId => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (charts[canvasId]) charts[canvasId].destroy();

        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: regionalData.map(r => r.region),
                datasets: [{
                    label: 'Sales Revenue ($)',
                    data: regionalData.map(r => r.sales),
                    backgroundColor: '#064E3B',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } }
                }
            }
        });
    });
}

function renderCategoryChartsAndTables() {
    if (!categoryData) return;

    // Render Category Charts
    ['boCategoryChart', 'smCategoryChart'].forEach(canvasId => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (charts[canvasId]) charts[canvasId].destroy();

        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: categoryData.map(c => c.category),
                datasets: [{
                    label: 'Category Revenue ($)',
                    data: categoryData.map(c => c.sales),
                    backgroundColor: ['#064E3B', '#D9A04B', '#0A6C52'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } }
                }
            }
        });
    });

    // Render Category Tables for Business Owner and Store Manager
    ['#bo-category-table tbody', '#sm-category-table tbody'].forEach(selector => {
        const tbody = document.querySelector(selector);
        if (!tbody) return;

        tbody.innerHTML = '';
        if (categoryData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No data available</td></tr>';
            return;
        }

        categoryData.forEach(cat => {
            const margin = cat.sales > 0 ? ((cat.profit / cat.sales) * 100).toFixed(1) : '0.0';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${cat.category}</strong></td>
                <td>$${cat.sales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td>${(cat.orders || 0).toLocaleString()}</td>
                <td>$${cat.profit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td><strong style="color: ${margin > 10 ? '#064E3B' : '#D9A04B'}">${margin}%</strong></td>
            `;
            tbody.appendChild(tr);
        });
    });
}

function renderSegmentationCharts() {
    if (!segSummaryData) return;
    const clusters = segSummaryData.cluster_summary;

    // Segment Share Doughnut Chart for Business Owner
    const boPieCanvas = document.getElementById('boSegmentShareChart');
    if (boPieCanvas) {
        const ctx = boPieCanvas.getContext('2d');
        if (charts.boPie) charts.boPie.destroy();

        charts.boPie = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: clusters.map(c => c.segment_name),
                datasets: [{
                    data: clusters.map(c => c.pct_sales),
                    backgroundColor: ['#064E3B', '#D9A04B', '#0A6C52', '#FBE7C9', '#10B981'],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#17201D', font: { family: 'Plus Jakarta Sans', size: 12 } } }
                }
            }
        });
    }

    // Segment Revenue Bar Charts
    ['boSegRevChart', 'seSegmentRevChart'].forEach(canvasId => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (charts[canvasId]) charts[canvasId].destroy();

        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: clusters.map(c => c.segment_name),
                datasets: [{
                    label: 'Segment Total Sales ($)',
                    data: clusters.map(c => c.total_sales),
                    backgroundColor: ['#064E3B', '#D9A04B', '#0A6C52', '#10B981'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } }
                }
            }
        });
    });

    // Segment RFM Bar Charts
    ['boSegRfmChart', 'seSegmentRfmChart'].forEach(canvasId => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (charts[canvasId]) charts[canvasId].destroy();

        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: clusters.map(c => c.segment_name),
                datasets: [
                    { label: 'Avg Recency (Days)', data: clusters.map(c => c.mean_recency_days), backgroundColor: '#D9A04B', borderRadius: 4 },
                    { label: 'Avg Orders (Freq x10)', data: clusters.map(c => c.mean_frequency_orders * 10), backgroundColor: '#064E3B', borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#17201D' } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } }
                }
            }
        });
    });
}

function renderForecastCharts() {
    if (!fcstPredictionsData) return;
    const records = fcstPredictionsData.data;

    // Render Business Owner Sales Trend Chart
    const boSalesTrendCanvas = document.getElementById('boSalesTrendChart');
    if (boSalesTrendCanvas) {
        const ctx = boSalesTrendCanvas.getContext('2d');
        const histData = records.filter(d => d.y !== null);

        if (charts.boSalesTrend) charts.boSalesTrend.destroy();
        charts.boSalesTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: histData.map(d => d.ds.substring(0, 7)),
                datasets: [{
                    label: 'Historical Monthly Sales ($)',
                    data: histData.map(d => d.y),
                    borderColor: '#064E3B',
                    backgroundColor: 'rgba(6, 78, 59, 0.08)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 2,
                    pointBackgroundColor: '#064E3B'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } }
                }
            }
        });
    }

    // Render Forecast Canvas for all Role Forecast Tabs
    ['boForecastChart', 'smForecastChart', 'seForecastChart'].forEach(canvasId => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (charts[canvasId]) charts[canvasId].destroy();

        const labels = records.map(r => r.ds.substring(0, 7));
        const actuals = records.map(r => r.y);

        let datasets = [{
            label: 'Historical Actual Sales',
            data: actuals,
            borderColor: '#66736E',
            backgroundColor: 'rgba(102, 115, 110, 0.1)',
            borderWidth: 2,
            pointRadius: 3
        }];

        if (currentForecastModel === 'Prophet') {
            datasets.push({
                label: 'Prophet Forecast (yhat)',
                data: records.map(r => r.prophet_yhat),
                borderColor: '#064E3B',
                backgroundColor: 'rgba(6, 78, 59, 0.12)',
                borderWidth: 3,
                fill: false,
                tension: 0.3
            });
        } else if (currentForecastModel === 'XGBoost') {
            datasets.push({
                label: 'XGBoost Forecast (yhat)',
                data: records.map(r => r.xgboost_yhat),
                borderColor: '#0A6C52',
                backgroundColor: 'rgba(10, 108, 82, 0.12)',
                borderWidth: 3,
                fill: false,
                tension: 0.2
            });
        } else if (currentForecastModel === 'Random Forest') {
            datasets.push({
                label: 'Random Forest Forecast (yhat)',
                data: records.map(r => r.rf_yhat),
                borderColor: '#D9A04B',
                backgroundColor: 'rgba(217, 160, 75, 0.12)',
                borderWidth: 3,
                fill: false,
                tension: 0.2
            });
        } else {
            datasets.push({ label: 'Prophet', data: records.map(r => r.prophet_yhat), borderColor: '#064E3B', borderWidth: 2, tension: 0.3 });
            datasets.push({ label: 'XGBoost', data: records.map(r => r.xgboost_yhat), borderColor: '#0A6C52', borderWidth: 2, tension: 0.2 });
            datasets.push({ label: 'Random Forest', data: records.map(r => r.rf_yhat), borderColor: '#D9A04B', borderWidth: 2, tension: 0.2 });
        }

        charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { color: '#17201D', font: { family: 'Plus Jakarta Sans', size: 12 } } }
                },
                scales: {
                    x: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } }
                }
            }
        });
    });
}

function renderModelEvaluationTablesAndCharts() {
    if (!fcstMetricsData) return;

    const metricsMap = fcstMetricsData.model_metrics;
    const bestModel = fcstMetricsData.best_performing_model;
    const models = Object.keys(metricsMap);

    // Populate Admin Model Metrics Table
    const tbody = document.querySelector('#admin-eval-table tbody');
    if (tbody) {
        tbody.innerHTML = '';
        models.forEach(modelName => {
            const m = metricsMap[modelName];
            const isBest = modelName === bestModel;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${modelName} ${isBest ? '<i class="fa-solid fa-crown" style="color:#D9A04B; margin-left:4px;"></i>' : ''}</strong></td>
                <td>$${m.MAE.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td>$${m.RMSE.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td><strong style="color: ${m.R2 > 0.6 ? '#064E3B' : '#D9A04B'}">${m.R2}</strong></td>
                <td>${m.MAPE_pct}%</td>
                <td><span class="tag-badge ${isBest ? 'gold' : ''}">${isBest ? 'Best Performer' : 'Evaluated'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Render Admin Error Charts
    ['adminErrorChart', 'adminFullErrorChart'].forEach(canvasId => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (charts[canvasId]) charts[canvasId].destroy();

        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: models,
                datasets: [
                    { label: 'RMSE ($)', data: models.map(m => metricsMap[m].RMSE), backgroundColor: '#064E3B', borderRadius: 6 },
                    { label: 'MAE ($)', data: models.map(m => metricsMap[m].MAE), backgroundColor: '#D9A04B', borderRadius: 6 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#17201D' } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' } }
                }
            }
        });
    });

    // Render Admin R2 Charts
    ['adminR2Chart', 'adminFullR2Chart'].forEach(canvasId => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (charts[canvasId]) charts[canvasId].destroy();

        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: models,
                datasets: [{
                    label: 'R² Accuracy Score',
                    data: models.map(m => metricsMap[m].R2),
                    backgroundColor: models.map(m => m === bestModel ? '#064E3B' : '#D9A04B'),
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#66736E' } },
                    y: { grid: { color: '#DDE6E2' }, ticks: { color: '#66736E' }, min: 0, max: 1 }
                }
            }
        });
    });
}
