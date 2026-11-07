import initialData from './mockData.json';

const STORAGE_KEY = 'mm_platform_dataset';

/**
 * Get or initialize the persistent platform dataset
 */
export function getStoredDataset() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch (e) {
    console.error('Error reading dataset from localStorage:', e);
  }

  // Initialize from bundled database records
  const fresh = JSON.parse(JSON.stringify(initialData));
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(fresh));
  } catch (e) {}
  return fresh;
}

/**
 * Save updated dataset into persistent localStorage
 */
export function saveStoredDataset(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.error('Error saving dataset to localStorage:', e);
  }
}

/**
 * Dynamic Universal Login:
 * Accepts ANY username, ANY password, and user-selected role/store.
 * No hardcoded demo restriction — whatever the user inputs, the system accepts and personalizes!
 */
export async function apiLogin(username, password, selectedRole = 'business_owner', selectedStore = 'STORE-001') {
  const trimmed = (username || '').trim();
  if (!trimmed) {
    throw new Error('Please enter a username');
  }

  const role = selectedRole || 'business_owner';
  const formattedName = trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
  const storeId = (role === 'store_manager' || role === 'sales_executive') ? selectedStore : null;

  const userObj = {
    access_token: `mm_token_${trimmed.toLowerCase()}_${Date.now()}`,
    token_type: 'bearer',
    role: role,
    username: trimmed,
    store_id: storeId,
    full_name: formattedName
  };

  // Add this user to the persistent user directory if Administrator
  try {
    const ds = getStoredDataset();
    if (!ds.users.some(u => u.username.toLowerCase() === trimmed.toLowerCase())) {
      ds.users.push({
        user_id: ds.users.length + 1,
        username: trimmed,
        full_name: formattedName,
        email: `${trimmed.toLowerCase()}@marketmind.ai`,
        role_name: role,
        role_id: role === 'business_owner' ? 1 : role === 'store_manager' ? 2 : role === 'sales_executive' ? 3 : 4,
        store_id: storeId,
        is_active: true
      });
      saveStoredDataset(ds);
    }
  } catch (e) {}

  return userObj;
}

/**
 * Get Analytics Summary dynamically based on current data
 */
export async function apiGetSummary(storeId) {
  const ds = getStoredDataset();
  const key = (storeId && storeId !== 'ALL') ? storeId : 'ALL';
  return ds.summaries[key] || ds.summaries['ALL'];
}

/**
 * Get Inventory list dynamically
 */
export async function apiGetInventory() {
  const ds = getStoredDataset();
  return ds.inventory || [];
}

/**
 * Get Users directory dynamically
 */
export async function apiGetUsers() {
  const ds = getStoredDataset();
  return ds.users || [];
}

/**
 * Get ML Forecast dataset
 */
export async function apiGetForecast() {
  const ds = getStoredDataset();
  return ds.forecast || {};
}

/**
 * Get Customer Segmentation dataset
 */
export async function apiGetSegmentation() {
  const ds = getStoredDataset();
  return ds.segmentation || {};
}

/**
 * Record a New Sales Transaction dynamically:
 * Appends to dataset, recalculates revenue, category breakdown, top products, and deducts inventory!
 */
export function recordSaleTransaction(txn) {
  const ds = getStoredDataset();
  const qty = parseInt(txn.quantity, 10) || 1;
  const price = parseFloat(txn.unit_price) || 10.0;
  const total = Math.round(qty * price * 100) / 100;
  const targetStore = txn.store_id || 'STORE-001';
  const category = txn.category || 'General Merchandise';
  const productName = txn.product_name || 'Retail Product';
  const customerId = txn.customer_id || `CUST-${Math.floor(1000 + Math.random() * 9000)}`;
  const paymentMethod = txn.payment_method || 'Credit Card';

  const newTxn = {
    transaction_id: `TXN-${Date.now().toString().slice(-5)}`,
    transaction_date: new Date().toISOString().replace('T', ' ').slice(0, 19),
    product_id: txn.product_id || `P-${Math.floor(100 + Math.random() * 900)}`,
    product_name: productName,
    category: category,
    quantity: qty,
    unit_price: price,
    total_amount: total,
    store_id: targetStore,
    customer_id: customerId,
    payment_method: paymentMethod
  };

  // Helper to update a summary object
  const updateSummary = (sumObj) => {
    if (!sumObj) return;
    sumObj.total_revenue = Math.round((sumObj.total_revenue + total) * 100) / 100;
    sumObj.total_transactions += 1;
    sumObj.total_items_sold += qty;

    // Add transaction to recent list
    if (!sumObj.recent_transactions) sumObj.recent_transactions = [];
    sumObj.recent_transactions.unshift(newTxn);
    if (sumObj.recent_transactions.length > 20) sumObj.recent_transactions.pop();

    // Update Category Breakdown
    if (!sumObj.category_breakdown) sumObj.category_breakdown = [];
    const catEntry = sumObj.category_breakdown.find(c => c.category.toLowerCase() === category.toLowerCase());
    if (catEntry) {
      catEntry.total_revenue = Math.round((catEntry.total_revenue + total) * 100) / 100;
      catEntry.total_quantity += qty;
    } else {
      sumObj.category_breakdown.push({
        category: category,
        total_revenue: total,
        total_quantity: qty
      });
    }

    // Update Top Products
    if (!sumObj.top_products) sumObj.top_products = [];
    const prodEntry = sumObj.top_products.find(p => p.product_name.toLowerCase() === productName.toLowerCase());
    if (prodEntry) {
      prodEntry.units_sold += qty;
      prodEntry.revenue = Math.round((prodEntry.revenue + total) * 100) / 100;
    } else {
      sumObj.top_products.push({
        product_name: productName,
        category: category,
        units_sold: qty,
        revenue: total
      });
    }
    sumObj.top_products.sort((a, b) => b.revenue - a.revenue);
  };

  // Update ALL global summary
  updateSummary(ds.summaries['ALL']);

  // Update target store summary
  if (ds.summaries[targetStore]) {
    updateSummary(ds.summaries[targetStore]);
  }

  // Deduct Inventory stock if matching item found
  if (ds.inventory) {
    const invItem = ds.inventory.find(i => i.product_name.toLowerCase() === productName.toLowerCase() || i.product_id === txn.product_id);
    if (invItem) {
      invItem.stock_level = Math.max(0, invItem.stock_level - qty);
      invItem.needs_reorder = invItem.stock_level <= invItem.reorder_threshold;
    }
  }

  saveStoredDataset(ds);
  return { updatedDataset: ds, newTransaction: newTxn };
}

/**
 * Import and recalculate dashboard from CSV rows
 */
export function importTransactionsFromCSV(rows) {
  const ds = getStoredDataset();
  if (!rows || rows.length === 0) return ds;

  rows.forEach(r => {
    const qty = parseInt(r.quantity || r.qty || 1, 10);
    const price = parseFloat(r.unit_price || r.price || 10.0);
    const total = parseFloat(r.total_amount || (qty * price));
    const store = r.store_id || r.store || 'STORE-001';
    const cat = r.category || 'General';
    const prod = r.product_name || r.product || 'Imported SKU';

    const itemTxn = {
      product_name: prod,
      category: cat,
      quantity: qty,
      unit_price: price,
      total_amount: total,
      store_id: store,
      customer_id: r.customer_id || 'CUST-IMP',
      payment_method: r.payment_method || 'Credit Card'
    };

    recordSaleTransaction(itemTxn);
  });

  return getStoredDataset();
}

/**
 * Reset dataset back to initial baseline
 */
export function resetPlatformData() {
  localStorage.removeItem(STORAGE_KEY);
  return getStoredDataset();
}
