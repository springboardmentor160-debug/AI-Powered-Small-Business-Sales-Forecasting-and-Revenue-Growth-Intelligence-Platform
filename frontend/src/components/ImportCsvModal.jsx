import React, { useState } from 'react';
import { UploadCloud, X, FileText, CheckCircle2 } from 'lucide-react';

export default function ImportCsvModal({ isOpen, onClose, onCsvImported }) {
  if (!isOpen) return null;

  const [fileName, setFileName] = useState('');
  const [parsedRows, setParsedRows] = useState([]);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setError(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target?.result;
        if (typeof text !== 'string') return;

        const lines = text.split(/\r?\n/).filter(line => line.trim().length > 0);
        if (lines.length < 2) {
          setError('CSV file must contain a header row and at least one data row.');
          return;
        }

        const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
        const rows = [];

        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',').map(v => v.trim().replace(/^["']|["']$/g, ''));
          if (values.length >= headers.length) {
            const rowObj = {};
            headers.forEach((h, idx) => {
              rowObj[h] = values[idx];
            });
            rows.push(rowObj);
          }
        }

        if (rows.length === 0) {
          setError('Could not extract valid records from this CSV.');
          return;
        }

        setParsedRows(rows);
      } catch (err) {
        setError('Failed to parse CSV file: ' + err.message);
      }
    };

    reader.readAsText(file);
  };

  const handleImport = () => {
    if (parsedRows.length === 0) return;
    onCsvImported(parsedRows);
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
        maxWidth: '480px',
        width: '100%',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UploadCloud size={22} color="#6366f1" />
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc' }}>Import Custom Sales CSV</h2>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
          Upload any sales CSV file. The platform will automatically parse records, calculate revenue, update product rankings, and refresh your dashboard live.
        </p>

        {error && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', padding: '0.75rem', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        <div style={{
          border: '2px dashed rgba(99, 102, 241, 0.4)',
          borderRadius: '12px',
          padding: '2rem 1rem',
          textAlign: 'center',
          backgroundColor: 'rgba(15, 23, 42, 0.5)',
          cursor: 'pointer',
          position: 'relative'
        }}>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{
              position: 'absolute',
              inset: 0,
              opacity: 0,
              cursor: 'pointer',
              width: '100%',
              height: '100%'
            }}
          />
          <FileText size={32} color="#818cf8" style={{ margin: '0 auto 0.75rem' }} />
          <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem' }}>
            {fileName ? fileName : 'Choose CSV File or Drag Here'}
          </div>
          <div style={{ color: '#64748b', fontSize: '0.8rem', marginTop: '0.25rem' }}>
            Accepts any retail transaction CSV format
          </div>
        </div>

        {parsedRows.length > 0 && (
          <div style={{
            marginTop: '1.25rem',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#34d399',
            fontSize: '0.85rem'
          }}>
            <CheckCircle2 size={16} />
            <span>Ready to import <strong>{parsedRows.length}</strong> transactions</span>
          </div>
        )}

        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem' }}>
          <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="btn"
            style={{ flex: 1 }}
            disabled={parsedRows.length === 0}
            onClick={handleImport}
          >
            Import Now
          </button>
        </div>
      </div>
    </div>
  );
}
