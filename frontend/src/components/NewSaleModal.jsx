import React, { useState } from 'react';
import { PlusCircle, X, DollarSign, Package, MapPin, User } from 'lucide-react';

export default function NewSaleModal({ isOpen, onClose, onSaleRecorded, defaultStore, existingLocations = [] }) {
  if (!isOpen) return null;

  const [productName, setProductName] = useState('');
  const [category, setCategory] = useState('Electronics');
  const [quantity, setQuantity] = useState(1);
  const [unitPrice, setUnitPrice] = useState('');
  const [storeId, setStoreId] = useState(defaultStore && defaultStore !== 'ALL' ? defaultStore : (existingLocations[0] || 'Store-1'));
  const [customStore, setCustomStore] = useState('');
  const [isCustomStore, setIsCustomStore] = useState(existingLocations.length === 0);
  const [customerId, setCustomerId] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('UPI');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!productName.trim() || !unitPrice) {
      alert('Please enter a product name and unit price.');
      return;
    }

    const finalLocation = isCustomStore 
      ? (customStore.trim() || 'Store-1') 
      : storeId;

    onSaleRecorded({
      product_name: productName.trim(),
      category: category,
      quantity: parseInt(quantity, 10) || 1,
      unit_price: parseFloat(unitPrice) || 0.0,
      store_id: finalLocation,
      customer_id: customerId.trim() || `CUST-${Math.floor(1000 + Math.random() * 9000)}`,
      payment_method: paymentMethod
    });

    onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        borderRadius: '16px',
        padding: '2rem',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <PlusCircle size={22} color="#6366f1" />
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc' }}>Record Sale</h2>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
              PRODUCT NAME
            </label>
            <div style={{ position: 'relative' }}>
              <Package size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                className="select-input"
                style={{ width: '100%', paddingLeft: '38px' }}
                placeholder="e.g. Wireless Headphones"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                required
                autoFocus
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
                CATEGORY
              </label>
              <select
                className="select-input"
                style={{ width: '100%' }}
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="Electronics">Electronics</option>
                <option value="Clothing">Clothing</option>
                <option value="Home & Kitchen">Home & Kitchen</option>
                <option value="Books">Books</option>
                <option value="Groceries">Groceries</option>
                <option value="Beauty & Care">Beauty & Care</option>
                <option value="Accessories">Accessories</option>
              </select>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8' }}>
                  LOCATION
                </label>
                {existingLocations.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setIsCustomStore(!isCustomStore)}
                    style={{ background: 'transparent', border: 'none', color: '#818cf8', fontSize: '0.75rem', cursor: 'pointer', padding: 0 }}
                  >
                    {isCustomStore ? 'Choose Existing' : '+ New Location'}
                  </button>
                )}
              </div>
              <div style={{ position: 'relative' }}>
                <MapPin size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                {isCustomStore || existingLocations.length === 0 ? (
                  <input
                    type="text"
                    className="select-input"
                    style={{ width: '100%', paddingLeft: '38px' }}
                    placeholder="e.g. Store A, Branch 1"
                    value={customStore}
                    onChange={(e) => setCustomStore(e.target.value)}
                    required
                  />
                ) : (
                  <select
                    className="select-input"
                    style={{ width: '100%', paddingLeft: '38px' }}
                    value={storeId}
                    onChange={(e) => setStoreId(e.target.value)}
                  >
                    {existingLocations.map((loc) => (
                      <option key={loc} value={loc}>{loc}</option>
                    ))}
                  </select>
                )}
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
                QUANTITY (UNITS)
              </label>
              <input
                type="number"
                min="1"
                className="select-input"
                style={{ width: '100%' }}
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
                UNIT PRICE ($)
              </label>
              <div style={{ position: 'relative' }}>
                <DollarSign size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  className="select-input"
                  style={{ width: '100%', paddingLeft: '34px' }}
                  placeholder="29.99"
                  value={unitPrice}
                  onChange={(e) => setUnitPrice(e.target.value)}
                  required
                />
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
                CUSTOMER ID (OPTIONAL)
              </label>
              <div style={{ position: 'relative' }}>
                <User size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                <input
                  type="text"
                  className="select-input"
                  style={{ width: '100%', paddingLeft: '34px' }}
                  placeholder="e.g. CUST-101"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
                PAYMENT METHOD
              </label>
              <select
                className="select-input"
                style={{ width: '100%' }}
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                <option value="UPI">UPI / Mobile</option>
                <option value="Credit Card">Credit Card</option>
                <option value="Debit Card">Debit Card</option>
                <option value="Cash">Cash</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.75rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ flex: 1 }}
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn"
              style={{ flex: 1 }}
            >
              Save Sale
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
