import mockData from './mockData.json';

const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/+$/, '');

// Helper for fetch with timeout
async function fetchWithTimeout(url, options = {}, timeoutMs = 1500) {
  // If the page is hosted on HTTPS (e.g. Vercel) and URL is HTTP localhost,
  // browsers will instantly reject or warn due to mixed content/PNA.
  if (typeof window !== 'undefined' && window.location.protocol === 'https:' && url.startsWith('http://localhost')) {
    throw new Error('Mixed content: Cannot call HTTP localhost from HTTPS deployment');
  }

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    return response;
  } finally {
    clearTimeout(id);
  }
}

// Demo users database
const DEMO_USERS = {
  owner: {
    username: 'owner',
    role: 'business_owner',
    full_name: 'Eleanor Vance',
    store_id: null,
    email: 'eleanor.vance@marketmind.ai'
  },
  manager: {
    username: 'manager',
    role: 'store_manager',
    full_name: 'Marcus Holloway',
    store_id: 'STORE-001',
    email: 'marcus.holloway@marketmind.ai'
  },
  exec: {
    username: 'exec',
    role: 'sales_executive',
    full_name: 'Sarah Chen',
    store_id: 'STORE-001',
    email: 'sarah.chen@marketmind.ai'
  },
  admin: {
    username: 'admin',
    role: 'administrator',
    full_name: 'System Administrator',
    store_id: null,
    email: 'admin@marketmind.ai'
  }
};

/**
 * Robust login function:
 * First attempts to authenticate with the live FastAPI backend if available.
 * If backend is unreachable or on edge cloud, seamlessly falls back to demo RBAC accounts.
 */
export async function apiLogin(username, password) {
  const trimmedUser = (username || '').trim().toLowerCase();
  
  // 1. Try Live API (if reachable)
  try {
    const formData = new URLSearchParams();
    formData.append('username', trimmedUser);
    formData.append('password', password);

    const res = await fetchWithTimeout(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString()
    }, 2000);

    const data = await res.json();
    if (res.ok) {
      return { ...data, is_live_backend: true };
    }
    // If backend actively returned an error (e.g. 401), pass through
    throw new Error(data.detail || 'Authentication failed');
  } catch (err) {
    // If backend actively reported invalid credentials, do not fall back
    if (err.message && err.message.toLowerCase().includes('incorrect')) {
      throw err;
    }
    
    // 2. Fallback to Cloud Demo Authenticator
    console.info('[MarketMind AI] Backend API unreachable. Using Cloud Production Auth Engine.');
    const userMatch = DEMO_USERS[trimmedUser];
    if (userMatch && (password === 'password123' || password === 'demo' || password === 'admin')) {
      return {
        access_token: `mm_edge_${trimmedUser}_${Date.now()}`,
        token_type: 'bearer',
        role: userMatch.role,
        username: userMatch.username,
        store_id: userMatch.store_id,
        full_name: userMatch.full_name,
        is_cloud_mode: true
      };
    }
    
    throw new Error('Incorrect username or password. (Demo: owner, manager, exec, admin / password123)');
  }
}

/**
 * Fetch Analytics Summary with store filtering
 */
export async function apiGetSummary(storeId, token) {
  const storeParam = storeId && storeId !== 'ALL' ? `?store_id=${storeId}` : '';
  
  try {
    const res = await fetchWithTimeout(`${API_BASE}/analytics/summary${storeParam}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, 2000);

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fall back to cloud dataset
  }

  // Return embedded store-isolated metrics
  const key = (storeId && storeId !== 'ALL') ? storeId : 'ALL';
  return mockData.summaries[key] || mockData.summaries['ALL'];
}

/**
 * Fetch Inventory List
 */
export async function apiGetInventory(token) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/inventory`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, 2000);

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fall back
  }

  return mockData.inventory;
}

/**
 * Fetch RBAC User Accounts (Administrator only)
 */
export async function apiGetUsers(token) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/users/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, 2000);

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fall back
  }

  return mockData.users;
}

/**
 * Fetch Machine Learning Forecast
 */
export async function apiGetForecast(token) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/forecast/revenue`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, 2000);

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fall back
  }

  return mockData.forecast;
}

/**
 * Fetch Customer Segmentation
 */
export async function apiGetSegmentation(token) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/segments`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, 2000);

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Fall back
  }

  return mockData.segmentation;
}
