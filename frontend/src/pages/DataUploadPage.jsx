import { useRef, useState } from "react";
import { IconAI, IconSales, IconUpload } from "../components/Icons";
import "./DataUploadPage.css";

const fieldLabels = {
  Invoice_Date: "Invoice Date",
  Revenue: "Revenue",
  Units: "Units / Quantity",
  Category: "Category",
  Brand: "Brand",
  City: "City / Location",
  Store_Format: "Store Format",
  Channel: "Sales Channel",
  Payment_Mode: "Payment Mode",
  Customer_ID: "Customer Identifier",
  Customer_Age: "Customer Age",
  Customer_Gender: "Customer Gender",
  Loyalty_Flag: "Loyalty Information",
  Selling_Price: "Selling Price",
  Cost_Price: "Cost Price",
  Cost: "Cost",
  Margin: "Margin",
  "Margin_%": "Margin Percentage",
  Stock_On_Hand: "Stock On Hand",
  Reorder_Level: "Reorder Level",
  Lead_Time_Days: "Lead Time",
  Invoice_ID: "Transaction Identifier",
};

const moduleNames = {
  sales_analytics: "Sales Analytics",
  sales_forecast: "Sales Forecast",
  customer_segmentation: "Customer Segmentation",
  customer_churn: "Customer Churn",
  product_recommendations: "Product Recommendations",
  anomaly_detection: "Anomaly Detection",
};

const modulePages = {
  sales_analytics: "sales",
  sales_forecast: "forecasting",
  customer_segmentation: "segmentation",
  customer_churn: "churn",
  product_recommendations: "recommendations",
  anomaly_detection: "anomalies",
};

function getTokenHeaders(extraHeaders = {}) {
  const token = localStorage.getItem("token");
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extraHeaders,
  };
}

async function readApiResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "The data upload request could not be completed."
    );
  }
  return data;
}

function formatBytes(size) {
  if (!Number.isFinite(size)) return "";
  return size >= 1024 * 1024
    ? `${(size / (1024 * 1024)).toFixed(1)} MB`
    : `${Math.max(1, Math.round(size / 1024))} KB`;
}

function hasActualValue(value) {
  return value !== undefined && value !== null && value !== "";
}

export default function DataUploadPage({
  activeDatasetId,
  activeDatasetFilename,
  onActivateDataset,
  setActivePage,
}) {
  const fileInputRef = useRef(null);
  const [upload, setUpload] = useState(null);
  const [mapping, setMapping] = useState({});
  const [mappingChanged, setMappingChanged] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isSavingMapping, setIsSavingMapping] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  const columns = upload?.columns || [];
  const previewRows = upload?.preview || [];
  const validation = upload?.validation || {};
  const capabilities = upload?.capabilities || [];
  const isReady = validation.valid === true;

  const handleFile = async (file) => {
    if (!file) return;
    setError("");
    setAnalysis(null);

    const allowedExtension = /\.(csv|xlsx|xls)$/i.test(file.name);
    if (!allowedExtension) {
      setError("Choose a CSV, XLSX, or XLS file.");
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setError("The selected file is larger than the 25 MB upload limit.");
      return;
    }
    if (file.size === 0) {
      setError("The selected file is empty. Choose a file containing data.");
      return;
    }

    setUpload(null);
    setMapping({});
    setMappingChanged(false);
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch("/api/data-upload", {
        method: "POST",
        headers: getTokenHeaders(),
        body: formData,
      });
      const data = await readApiResponse(response);
      if (!data.dataset_id || !Array.isArray(data.columns)) {
        throw new Error("The upload service returned incomplete file information.");
      }
      setUpload(data);
      setMapping(data.mapping || {});
      setMappingChanged(false);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const saveMapping = async () => {
    if (!upload?.dataset_id) return;
    setError("");
    setIsSavingMapping(true);
    try {
      const response = await fetch(
        `/api/data-upload/${encodeURIComponent(upload.dataset_id)}/mapping`,
        {
          method: "PATCH",
          headers: getTokenHeaders({ "Content-Type": "application/json" }),
          body: JSON.stringify({ mapping }),
        }
      );
      const data = await readApiResponse(response);
      setUpload((current) => ({ ...current, ...data }));
      setMapping(data.mapping || mapping);
      setMappingChanged(false);
      setAnalysis(null);
    } catch (mappingError) {
      setError(mappingError.message);
    } finally {
      setIsSavingMapping(false);
    }
  };

  const analyzeData = async () => {
    if (!upload?.dataset_id) return;
    setError("");
    setIsAnalyzing(true);
    setAnalysis(null);
    try {
      const response = await fetch(
        `/api/data-upload/${encodeURIComponent(upload.dataset_id)}/analyze`,
        {
          method: "POST",
          headers: getTokenHeaders(),
        }
      );
      const data = await readApiResponse(response);
      setAnalysis(data);
      onActivateDataset(upload.dataset_id, upload.filename);
    } catch (analysisError) {
      setError(analysisError.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const removeUpload = async () => {
    if (!upload?.dataset_id) return;
    setError("");
    setIsRemoving(true);
    try {
      const response = await fetch(
        `/api/data-upload/${encodeURIComponent(upload.dataset_id)}`,
        { method: "DELETE", headers: getTokenHeaders() }
      );
      await readApiResponse(response);
      if (activeDatasetId === upload.dataset_id) {
        onActivateDataset(null, "");
      }
      setUpload(null);
      setMapping({});
      setMappingChanged(false);
      setAnalysis(null);
    } catch (removeError) {
      setError(removeError.message);
    } finally {
      setIsRemoving(false);
    }
  };

  const resetToDefault = () => {
    onActivateDataset(null, "");
  };

  const summary = analysis?.summary || {};

  return (
    <div className="page-container data-upload-page">
      <header className="upload-page-header">
        <div className="upload-page-title">
          <span className="upload-title-icon"><IconUpload size={19} color="#4776e6" /></span>
          <div>
            <h1>Data Upload &amp; Analysis</h1>
            <p>Upload your sales data and generate AI-powered business insights.</p>
          </div>
        </div>
        <p className="upload-page-description">
          Use your own sales data with MarketMind AI to understand sales
          performance, customer behavior, forecasting, recommendations, churn
          risk, and anomalies.
        </p>
      </header>

      <div className="upload-source-bar">
        <div>
          <span className="upload-source-dot" />
          <strong>
            Data Source: {activeDatasetId ? "Uploaded Dataset" : "Default Dataset"}
          </strong>
          {activeDatasetId && activeDatasetFilename && (
            <span className="upload-source-file">{activeDatasetFilename}</span>
          )}
        </div>
        {activeDatasetId && (
          <button type="button" className="upload-text-button" onClick={resetToDefault}>
            Switch to default dataset
          </button>
        )}
      </div>

      <div className="upload-workflow" aria-label="Upload workflow">
        {["Upload", "Validate", "Preview", "Analyze", "Insights"].map((step, index) => (
          <div className={`upload-workflow-step ${upload || index === 0 ? "complete" : ""}`} key={step}>
            <span>{index + 1}</span>
            <strong>{step}</strong>
            {index < 4 && <i aria-hidden="true" />}
          </div>
        ))}
      </div>

      <div className="upload-layout">
        <section className="upload-card">
          <div className="upload-section-heading">
            <span className="upload-heading-icon"><IconUpload size={17} color="#4776e6" /></span>
            <div>
              <h2>Upload Your Sales Data</h2>
              <p>Upload a CSV or Excel file to analyze your business data.</p>
            </div>
          </div>

          {!upload && (
            <div
              className={`upload-dropzone ${dragging ? "is-dragging" : ""}`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragLeave={(event) => {
                event.preventDefault();
                setDragging(false);
              }}
              onDrop={(event) => {
                event.preventDefault();
                setDragging(false);
                handleFile(event.dataTransfer.files?.[0]);
              }}
            >
              <span className="upload-dropzone-icon"><IconUpload size={25} color="#4776e6" /></span>
              <strong>{isUploading ? "Uploading and checking your file…" : "Drag & drop your file here"}</strong>
              <span>or</span>
              <button
                type="button"
                className="upload-browse-button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                Browse Files
              </button>
              <small>CSV, XLSX, XLS · Maximum file size: 25 MB</small>
              <input
                ref={fileInputRef}
                className="upload-file-input"
                type="file"
                accept=".csv,.xlsx,.xls,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                onChange={(event) => handleFile(event.target.files?.[0])}
              />
            </div>
          )}

          {upload && (
            <div className="upload-file-card">
              <span className={`upload-file-status ${isReady ? "is-valid" : "is-invalid"}`}>
                {isReady ? "✓" : "!"}
              </span>
              <div className="upload-file-details">
                <strong>{upload.filename}</strong>
                <span>
                  {formatBytes(upload.size_bytes)}
                  {hasActualValue(upload.row_count) && ` · ${upload.row_count.toLocaleString()} rows`}
                  {hasActualValue(upload.column_count) && ` · ${upload.column_count} columns`}
                </span>
                <small>{isReady ? "File uploaded and validated" : "File uploaded · review validation"}</small>
              </div>
              <button
                type="button"
                className="upload-remove-button"
                onClick={removeUpload}
                disabled={isRemoving}
              >
                {isRemoving ? "Removing…" : "Remove File"}
              </button>
            </div>
          )}

          {error && (
            <div className="upload-error" role="alert">
              <strong>We couldn’t complete that step.</strong>
              <span>{error}</span>
            </div>
          )}

          <details className="upload-requirements">
            <summary>What data should I upload?</summary>
            <p>
              For the best analysis, your file should contain sales transaction
              information such as date, product/category, sales or revenue,
              quantity, location, channel and customer-related fields when
              available.
            </p>
            <strong>Required fields depend on the analysis you want to run.</strong>
          </details>
        </section>

        <section className="upload-card upload-validation-card">
          <div className="upload-section-heading">
            <span className="upload-heading-icon upload-heading-icon-green">
              <IconAI size={16} color="#16946b" />
            </span>
            <div>
              <h2>File Validation</h2>
              <p>We check the file structure before analyzing it.</p>
            </div>
          </div>

          {!upload ? (
            <div className="upload-validation-empty">
              Upload a file to see its validation results and analysis readiness.
            </div>
          ) : (
            <>
              <div className={`upload-validation-status ${isReady ? "is-valid" : "is-invalid"}`}>
                <span>{isReady ? "✓" : "!"}</span>
                <div>
                  <strong>{isReady ? "Validation complete" : "Review required"}</strong>
                  <small>
                    {isReady
                      ? "The file can be previewed and analyzed."
                      : "Address the items below before analysis."}
                  </small>
                </div>
              </div>
              <ul className="upload-validation-list">
                {(validation.checks || []).map((check, index) => (
                  <li className={`validation-${check.status || "info"}`} key={`${check.label}-${index}`}>
                    <span>{check.status === "passed" ? "✓" : check.status === "warning" ? "!" : "•"}</span>
                    <div>
                      <strong>{check.label}</strong>
                      {check.message && <small>{check.message}</small>}
                    </div>
                  </li>
                ))}
                {(validation.issues || []).map((issue, index) => (
                  <li className="validation-error" key={`issue-${index}`}>
                    <span>!</span>
                    <div><strong>{typeof issue === "string" ? issue : issue.message}</strong></div>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      </div>

      {upload && (
        <>
          {Object.keys(mapping).length > 0 && (
            <section className="upload-card upload-mapping-card">
              <div className="upload-section-heading">
                <span className="upload-heading-icon"><IconSales size={16} color="#4776e6" /></span>
                <div>
                  <h2>Confirm Your Data Columns</h2>
                  <p>Match the columns in your file to the fields used for business analysis.</p>
                </div>
              </div>
              <div className="upload-mapping-heading">
                <span>Your Column</span>
                <span>MarketMind Field</span>
              </div>
              <div className="upload-mapping-list">
                {Object.entries(mapping).map(([field, source]) => (
                  <label className="upload-mapping-row" key={field}>
                    <span>{source || "Not mapped"}</span>
                    <span className="upload-mapping-arrow">→</span>
                    <select
                      value={source || ""}
                      onChange={(event) => {
                        setMapping((current) => ({
                          ...current,
                          [field]: event.target.value || null,
                        }));
                        setMappingChanged(true);
                      }}
                    >
                      <option value="">Not available</option>
                      {columns.map((column) => (
                        <option key={column} value={column}>{column}</option>
                      ))}
                    </select>
                    <small>{fieldLabels[field] || field.replaceAll("_", " ")}</small>
                  </label>
                ))}
              </div>
              <div className="upload-mapping-footer">
                <span>Map only the fields available in your file; other analysis options may remain unavailable.</span>
                <button
                  type="button"
                  className="upload-secondary-button"
                  onClick={saveMapping}
                  disabled={isSavingMapping}
                >
                  {isSavingMapping ? "Saving…" : "Save Column Mapping"}
                </button>
              </div>
            </section>
          )}

          <section className="upload-card upload-preview-card">
            <div className="upload-preview-header">
              <div>
                <h2>Data Preview</h2>
                <p>Review the first rows and detected columns before analysis.</p>
              </div>
              <div className="upload-preview-counts">
                {hasActualValue(upload.row_count) && <strong>{upload.row_count.toLocaleString()} rows</strong>}
                {hasActualValue(upload.column_count) && <strong>{upload.column_count} columns</strong>}
              </div>
            </div>
            {previewRows.length > 0 && columns.length > 0 ? (
              <div className="upload-table-scroll">
                <table className="upload-preview-table">
                  <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
                  <tbody>
                    {previewRows.slice(0, 10).map((row, index) => (
                      <tr key={index}>
                        {columns.map((column) => <td key={column}>{row[column] ?? ""}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="upload-preview-empty">
                A preview is not available for this file. Review the validation notes.
              </div>
            )}
          </section>

          <section className="upload-analysis-section">
            <div className="upload-analysis-header">
              <div>
                <span className="upload-eyebrow">Next step</span>
                <h2>What would you like to analyze?</h2>
                <p>Available options depend on the fields found in your uploaded data.</p>
              </div>
              <button
                type="button"
                className="upload-primary-button"
                onClick={analyzeData}
                disabled={!isReady || mappingChanged || isAnalyzing}
              >
                {isAnalyzing ? "Analyzing your data…" : "Analyze My Data"}
              </button>
            </div>

            <div className="upload-capability-grid">
              {capabilities.map((capability) => (
                <article className={`upload-capability-card ${capability.available ? "is-available" : "is-unavailable"}`} key={capability.id}>
                  <span className="upload-capability-icon">
                    <IconSales size={17} color={capability.available ? "#4776e6" : "#96a1b1"} />
                  </span>
                  <div>
                    <h3>{moduleNames[capability.id] || capability.label}</h3>
                    <p>{capability.description || capability.reason}</p>
                    <span>{capability.available ? "Available for this dataset" : "Not available for this dataset"}</span>
                  </div>
                </article>
              ))}
              {capabilities.length === 0 && (
                <div className="upload-capability-placeholder">
                  Upload and validate a file to see which analyses are supported.
                </div>
              )}
            </div>
          </section>
        </>
      )}

      {analysis && (
        <section className="upload-results-section">
          <div className="upload-results-header">
            <div>
              <span className="upload-eyebrow">Analysis complete</span>
              <h2>Your Business Analysis Is Ready</h2>
            </div>
            <span className="upload-active-source">Data Source: Uploaded File</span>
          </div>
          <div className="upload-result-metrics">
            {[
              ["Revenue", summary.revenue],
              ["Sales Volume", summary.sales_volume],
              ["Records Analyzed", summary.records_analyzed],
              ["Date Range", summary.date_range],
            ].filter(([, value]) => hasActualValue(value)).map(([label, value]) => (
              <article className="upload-result-card" key={label}>
                <span>{label}</span>
                <strong>{typeof value === "number" ? value.toLocaleString() : value}</strong>
              </article>
            ))}
          </div>
          <div className="upload-explore-card">
            <div>
              <h3>Explore AI Insights</h3>
              <p>Open an available analysis with your uploaded dataset selected.</p>
            </div>
            <div className="upload-explore-links">
              {capabilities.filter((item) => item.available && modulePages[item.id]).map((item) => (
                <button
                  type="button"
                  key={item.id}
                  onClick={() => setActivePage(modulePages[item.id])}
                >
                  {moduleNames[item.id] || item.label} <span>→</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
