import React, { useState } from 'react';
import { ShoppingBag, Plus, Minus, Trash2, CheckCircle2, CreditCard, Smartphone, Banknote, Search, Sparkles } from 'lucide-react';

const CATALOG_ITEMS = [
  { id: 'P101', name: 'Wireless Noise-Canceling Headphones', category: 'Electronics', price: 129.99, icon: '🎧' },
  { id: 'P102', name: 'Ergonomic Executive Chair', category: 'Home & Kitchen', price: 199.50, icon: '🪑' },
  { id: 'P103', name: 'Organic Cotton Crew T-Shirt', category: 'Clothing', price: 24.99, icon: '👕' },
  { id: 'P104', name: 'Insulated Stainless Steel Bottle', category: 'Home & Kitchen', price: 18.00, icon: '🍶' },
  { id: 'P105', name: 'Smart Fitness Tracker Pro', category: 'Electronics', price: 49.99, icon: '⌚' },
  { id: 'P106', name: 'Mechanical Gaming Keyboard', category: 'Electronics', price: 89.99, icon: '⌨️' },
  { id: 'P107', name: 'Artisan Roast Coffee Beans', category: 'Groceries', price: 14.50, icon: '☕' },
  { id: 'P108', name: 'Hydrating Face Treatment Serum', category: 'Beauty & Care', price: 34.50, icon: '✨' },
  { id: 'P109', name: 'Data Science & AI Handbook', category: 'Books', price: 42.00, icon: '📚' },
  { id: 'P110', name: 'Bluetooth Outdoor Speaker', category: 'Electronics', price: 54.99, icon: '🔊' },
  { id: 'P111', name: 'All-Weather Running Shoes', category: 'Clothing', price: 89.00, icon: '👟' },
  { id: 'P112', name: 'Organic Green Tea Tin', category: 'Groceries', price: 12.00, icon: '🍵' },
];

export default function POSTerminal({ onSaleCompleted, currentLocation, locations = [] }) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [cart, setCart] = useState([]);
  const [customerName, setCustomerName] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Credit Card');
  const [storeLocation, setStoreLocation] = useState(currentLocation && currentLocation !== 'ALL' ? currentLocation : (locations[0] || 'Main Branch'));
  const [lastReceipt, setLastReceipt] = useState(null);

  const categories = ['All', 'Electronics', 'Clothing', 'Home & Kitchen', 'Groceries', 'Beauty & Care', 'Books'];

  const filteredItems = CATALOG_ITEMS.filter(item => {
    const matchesCat = selectedCategory === 'All' || item.category === selectedCategory;
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) || item.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(i => i.id === product.id);
      if (existing) {
        return prev.map(i => i.id === product.id ? { ...i, qty: i.qty + 1 } : i);
      }
      return [...prev, { ...product, qty: 1 }];
    });
  };

  const updateQty = (id, delta) => {
    setCart(prev => prev.map(i => {
      if (i.id === id) {
        const newQty = i.qty + delta;
        return newQty > 0 ? { ...i, qty: newQty } : null;
      }
      return i;
    }).filter(Boolean));
  };

  const removeItem = (id) => {
    setCart(prev => prev.filter(i => i.id !== id));
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
  const totalUnits = cart.reduce((sum, item) => sum + item.qty, 0);

  const handleCheckout = (e) => {
    e.preventDefault();
    if (cart.length === 0) return;

    // Process each line item into the platform dataset
    cart.forEach(item => {
      onSaleCompleted({
        product_name: item.name,
        category: item.category,
        quantity: item.qty,
        unit_price: item.price,
        store_id: storeLocation,
        customer_id: customerName.trim() || `CUST-${Math.floor(1000 + Math.random() * 9000)}`,
        payment_method: paymentMethod
      });
    });

    setLastReceipt({
      total: cartTotal,
      units: totalUnits,
      itemsCount: cart.length,
      method: paymentMethod,
      location: storeLocation,
      time: new Date().toLocaleTimeString()
    });

    setCart([]);
    setCustomerName('');
    setTimeout(() => setLastReceipt(null), 6000);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '1.75rem', alignItems: 'start' }}>
      {/* LEFT: Product Catalog & Quick-Tap Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Receipt Success Banner */}
        {lastReceipt && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%)',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            borderRadius: '16px',
            padding: '1.25rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 10px 25px -5px rgba(16, 185, 129, 0.2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={24} color="#ffffff" />
              </div>
              <div>
                <div style={{ fontWeight: 800, color: '#f8fafc', fontSize: '1rem' }}>Sale Completed Successfully!</div>
                <div style={{ color: '#a7f3d0', fontSize: '0.82rem' }}>
                  {lastReceipt.units} units • ${lastReceipt.total.toFixed(2)} paid via {lastReceipt.method} • {lastReceipt.location} ({lastReceipt.time})
                </div>
              </div>
            </div>
            <span className="badge badge-success">Processed Live</span>
          </div>
        )}

        {/* Search & Categories Bar */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: 1, minWidth: '220px' }}>
              <Search size={16} color="#64748b" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                className="select-input"
                style={{ width: '100%', paddingLeft: '40px' }}
                placeholder="Search catalog or category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#94a3b8', fontSize: '0.82rem' }}>
              <Sparkles size={14} color="#818cf8" />
              <span>Tap any item to ring up</span>
            </div>
          </div>

          {/* Category Chips */}
          <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '4px' }}>
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                style={{
                  padding: '0.4rem 0.9rem',
                  borderRadius: '10px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  border: '1px solid',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  whiteSpace: 'nowrap',
                  backgroundColor: selectedCategory === cat ? 'rgba(99, 102, 241, 0.25)' : 'rgba(15, 23, 42, 0.6)',
                  borderColor: selectedCategory === cat ? '#6366f1' : 'rgba(255, 255, 255, 0.08)',
                  color: selectedCategory === cat ? '#818cf8' : '#94a3b8'
                }}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Product Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
          {filteredItems.map((prod) => (
            <div
              key={prod.id}
              onClick={() => addToCart(prod)}
              className="card"
              style={{
                padding: '1.25rem',
                cursor: 'pointer',
                transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
              }}
            >
              <div>
                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{prod.icon}</div>
                <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#818cf8', fontWeight: 700 }}>
                  {prod.category}
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#f8fafc', marginTop: '0.2rem', lineHeight: 1.3 }}>
                  {prod.name}
                </div>
              </div>

              <div style={{ marginTop: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#10b981' }}>
                  ${prod.price.toFixed(2)}
                </div>
                <button
                  type="button"
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    background: 'rgba(99, 102, 241, 0.2)',
                    border: '1px solid rgba(99, 102, 241, 0.4)',
                    color: '#818cf8',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer'
                  }}
                >
                  <Plus size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT: Active Order Cart & Register Terminal */}
      <div className="card" style={{ padding: '1.5rem', position: 'sticky', top: '90px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShoppingBag size={20} color="#6366f1" />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#f8fafc' }}>Current Order</h2>
          </div>
          {cart.length > 0 && (
            <button
              onClick={() => setCart([])}
              style={{ background: 'transparent', border: 'none', color: '#fca5a5', fontSize: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <Trash2 size={13} /> Clear
            </button>
          )}
        </div>

        {/* Itemized Cart List */}
        {cart.length === 0 ? (
          <div style={{ padding: '3rem 1rem', textAlign: 'center', color: '#64748b' }}>
            <ShoppingBag size={36} color="#334155" style={{ margin: '0 auto 0.75rem' }} />
            <div style={{ fontWeight: 600, color: '#94a3b8', fontSize: '0.9rem' }}>Cart is Empty</div>
            <div style={{ fontSize: '0.78rem', marginTop: '0.25rem' }}>Tap any item from the catalog to ring up a sale.</div>
          </div>
        ) : (
          <div style={{ maxHeight: '280px', overflowY: 'auto', marginBottom: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {cart.map((item) => (
              <div key={item.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem 0.75rem', borderRadius: '10px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ flex: 1, minWidth: 0, marginRight: '0.5rem' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 600 }}>
                    ${item.price.toFixed(2)} each
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <button
                    onClick={() => updateQty(item.id, -1)}
                    style={{ width: '24px', height: '24px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', border: 'none', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  >
                    <Minus size={12} />
                  </button>
                  <span style={{ fontWeight: 700, fontSize: '0.85rem', minWidth: '18px', textAlign: 'center' }}>{item.qty}</span>
                  <button
                    onClick={() => updateQty(item.id, 1)}
                    style={{ width: '24px', height: '24px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', border: 'none', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  >
                    <Plus size={12} />
                  </button>
                  <button
                    onClick={() => removeItem(item.id)}
                    style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '0 4px' }}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Customer & Location Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
              Customer Name / ID (Optional)
            </label>
            <input
              type="text"
              className="select-input"
              style={{ width: '100%', fontSize: '0.82rem' }}
              placeholder="e.g. Sarah Jenkins or Walk-in"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
              Store Location
            </label>
            <input
              type="text"
              className="select-input"
              style={{ width: '100%', fontSize: '0.82rem' }}
              value={storeLocation}
              onChange={(e) => setStoreLocation(e.target.value)}
              placeholder="e.g. Branch-1"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.35rem', textTransform: 'uppercase' }}>
              Payment Method
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.35rem' }}>
              {[
                { name: 'Credit Card', icon: CreditCard },
                { name: 'UPI', icon: Smartphone },
                { name: 'Cash', icon: Banknote }
              ].map(m => {
                const Icon = m.icon;
                const active = paymentMethod === m.name;
                return (
                  <button
                    key={m.name}
                    type="button"
                    onClick={() => setPaymentMethod(m.name)}
                    style={{
                      padding: '0.5rem 0.25rem',
                      borderRadius: '8px',
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      border: '1px solid',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '4px',
                      backgroundColor: active ? 'rgba(99, 102, 241, 0.25)' : 'rgba(15, 23, 42, 0.6)',
                      borderColor: active ? '#6366f1' : 'rgba(255, 255, 255, 0.08)',
                      color: active ? '#818cf8' : '#94a3b8'
                    }}
                  >
                    <Icon size={14} />
                    <span>{m.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Pricing Summary */}
        <div style={{ paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.08)', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.82rem', marginBottom: '0.35rem' }}>
            <span>Total Units:</span>
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>{totalUnits}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#cbd5e1' }}>Total Due:</span>
            <span style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981' }}>
              ${cartTotal.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Ring Register Button */}
        <button
          onClick={handleCheckout}
          disabled={cart.length === 0}
          className="btn"
          style={{
            width: '100%',
            padding: '0.85rem',
            fontSize: '0.95rem',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            opacity: cart.length === 0 ? 0.5 : 1,
            cursor: cart.length === 0 ? 'not-allowed' : 'pointer'
          }}
        >
          <span>Complete Sale</span>
          <span>•</span>
          <span>${cartTotal.toFixed(2)}</span>
        </button>
      </div>
    </div>
  );
}
