app_js = 'frontend/app.js'
extra_js = """

/* ==========================================================================
   MILESTONE 3 DATA LOADERS & RENDERERS
   ========================================================================== */

async function loadMilestone3Data() {
    fetchRecommendations();
    fetchChurnPredictions('All');
    fetchAnomalies();
}

async function fetchRecommendations() {
    try {
        const rulesRes = await authFetch('/recommendations/rules?limit=30');
        const rules = await rulesRes.json();
        renderRulesTables(rules);

        const customersRes = await authFetch('/churn/predictions?limit=100');
        const customers = await customersRes.json();
        
        ['rec-customer-select-admin', 'rec-customer-select-bo'].forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                select.innerHTML = '<option value="">Select Customer Account...</option>';
                customers.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.customer_id;
                    opt.textContent = `${c.customer_name} (${c.customer_id})`;
                    select.appendChild(opt);
                });
                select.onchange = (e) => {
                    if (e.target.value) fetchCustomerRecsForElement(e.target.value, selectId === 'rec-customer-select-admin' ? 'customer-rec-results-admin' : 'customer-rec-results-bo');
                };
                if (customers.length > 0) {
                    select.value = customers[0].customer_id;
                    fetchCustomerRecsForElement(customers[0].customer_id, selectId === 'rec-customer-select-admin' ? 'customer-rec-results-admin' : 'customer-rec-results-bo');
                }
            }
        });
    } catch (e) {
        console.error('Error fetching recommendations:', e);
    }
}

async function fetchCustomerRecsForElement(customerId, containerId) {
    try {
        const res = await authFetch(`/recommendations/customer/${customerId}`);
        const recs = await res.json();
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!recs || recs.length === 0) {
            container.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:20px;">No recommendations found for this account.</div>`;
            return;
        }

        container.innerHTML = recs.map(r => `
            <div class="rec-card">
                <div class="rec-card-header">
                    <span class="rec-card-rank">Rank #${r.rank}</span>
                    <span style="font-size:0.75rem; font-weight:600;">${r.recommendation_type}</span>
                </div>
                <div class="rec-card-title">${r.product_name}</div>
                <div class="rec-card-category"><i class="fa-solid fa-tag"></i> ${r.category || 'General'} &bull; ${r.sub_category || ''}</div>
                <div class="rec-card-score"><i class="fa-solid fa-chart-line"></i> Affinity Score: ${(r.score * 100).toFixed(1)}%</div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Error fetching customer recs:', e);
    }
}

function renderRulesTables(rules) {
    ['rules-table-admin', 'rules-table-bo'].forEach(tableId => {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (!tbody) return;
        if (!rules || rules.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No association rules available.</td></tr>`;
            return;
        }
        tbody.innerHTML = rules.map(r => `
            <tr>
                <td><strong>${r.antecedent_name}</strong></td>
                <td><span style="color:#2E7D32; font-weight:600;"><i class="fa-solid fa-arrow-right"></i> ${r.consequent_name}</span></td>
                <td>${(r.support * 100).toFixed(2)}%</td>
                <td>${(r.confidence * 100).toFixed(1)}%</td>
                <td><span class="badge-risk-low">${r.lift.toFixed(2)}x Lift</span></td>
                <td>${r.recommendation_type}</td>
            </tr>
        `).join('');
    });
}

async function fetchChurnPredictions(riskFilter = 'All') {
    try {
        const res = await authFetch(`/churn/predictions?risk=${riskFilter}&limit=100`);
        const predictions = await res.json();
        renderChurnTables(predictions);

        const metricsRes = await authFetch('/churn/metrics');
        const metrics = await metricsRes.json();

        ['admin', 'bo'].forEach(suffix => {
            const bestM = document.getElementById(`churn-best-model-${suffix}`);
            const highC = document.getElementById(`churn-high-count-${suffix}`);
            const medC = document.getElementById(`churn-med-count-${suffix}`);
            const lowC = document.getElementById(`churn-low-count-${suffix}`);

            if (bestM) bestM.textContent = metrics.best_performing_model || 'Random Forest';
            if (highC) highC.textContent = metrics.high_risk_count || 0;
            if (medC) medC.textContent = metrics.medium_risk_count || 0;
            if (lowC) lowC.textContent = metrics.low_risk_count || 0;
        });
    } catch (e) {
        console.error('Error fetching churn predictions:', e);
    }
}

function renderChurnTables(predictions) {
    ['churn-table-admin', 'churn-table-bo'].forEach(tableId => {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (!tbody) return;
        if (!predictions || predictions.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;">No customers found for risk category.</td></tr>`;
            return;
        }
        tbody.innerHTML = predictions.map(c => {
            let badgeClass = 'badge-risk-low';
            if (c.risk_category === 'High Risk') badgeClass = 'badge-risk-high';
            else if (c.risk_category === 'Medium Risk') badgeClass = 'badge-risk-medium';

            return `
                <tr>
                    <td><code>${c.customer_id}</code></td>
                    <td><strong>${c.customer_name}</strong></td>
                    <td>${c.segment_name || 'Unassigned'}</td>
                    <td>${c.region || '—'}</td>
                    <td>${c.recency_days} days</td>
                    <td>${c.frequency} orders</td>
                    <td>$${c.monetary.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                    <td><strong>${(c.churn_probability * 100).toFixed(1)}%</strong></td>
                    <td><span class="${badgeClass}">${c.risk_category}</span></td>
                </tr>
            `;
        }).join('');
    });
}

async function fetchAnomalies() {
    try {
        const res = await authFetch('/anomalies/transactions?limit=100');
        const anomalies = await res.json();
        renderAnomaliesTables(anomalies);
    } catch (e) {
        console.error('Error fetching anomalies:', e);
    }
}

function renderAnomaliesTables(anomalies) {
    ['anomalies-table-admin', 'anomalies-table-bo'].forEach(tableId => {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (!tbody) return;
        if (!anomalies || anomalies.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;">No transaction anomalies detected.</td></tr>`;
            return;
        }
        tbody.innerHTML = anomalies.map(a => `
            <tr>
                <td><code>${a.order_id}</code></td>
                <td>${a.order_date ? a.order_date.substring(0, 10) : '—'}</td>
                <td><strong>${a.customer_name || '—'}</strong></td>
                <td>${a.region || '—'}</td>
                <td>${a.product_name || '—'}</td>
                <td><strong style="color:#C62828;">$${a.sales_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</strong></td>
                <td>${a.quantity}</td>
                <td>${(a.discount_pct * 100).toFixed(0)}%</td>
                <td><span class="badge-risk-medium">${a.anomaly_score.toFixed(3)}</span></td>
                <td style="color:#D84315; font-size:0.85rem; font-weight:600;"><i class="fa-solid fa-triangle-exclamation"></i> ${a.anomaly_reason}</td>
            </tr>
        `).join('');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(loadMilestone3Data, 1000);
});
"""

with open(app_js, 'a', encoding='utf-8') as f:
    f.write(extra_js)
print('Successfully appended Milestone 3 handlers to app.js!')
