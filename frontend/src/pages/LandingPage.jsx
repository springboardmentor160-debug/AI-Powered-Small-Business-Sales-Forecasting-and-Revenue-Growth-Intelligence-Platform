import {
  IconAI,
  IconAnomaly,
  IconArrowRight,
  IconChurn,
  IconCustomers,
  IconForecasting,
  IconInventory,
  IconRecommendations,
  IconSales,
  IconSegmentation,
  IconUpload,
} from "../components/Icons";
import "./LandingPage.css";

const trustItems = [
  { label: "Sales Analytics", icon: IconSales },
  { label: "AI Forecasting", icon: IconForecasting },
  { label: "Customer Intelligence", icon: IconCustomers },
  { label: "Product Recommendations", icon: IconRecommendations },
  { label: "Inventory Insights", icon: IconInventory },
  { label: "Anomaly Detection", icon: IconAnomaly },
];

const features = [
  {
    title: "Sales Analytics",
    description: "See performance across products, channels and locations.",
    icon: IconSales,
    tone: "blue",
  },
  {
    title: "Sales Forecasting",
    description: "Use historical sales patterns to plan for what comes next.",
    icon: IconForecasting,
    tone: "purple",
  },
  {
    title: "Customer Segmentation",
    description: "Understand customer groups through their purchasing behavior.",
    icon: IconSegmentation,
    tone: "teal",
  },
  {
    title: "Churn Prediction",
    description: "Identify customers whose activity may be declining.",
    icon: IconChurn,
    tone: "amber",
  },
  {
    title: "Product Recommendations",
    description: "Explore products and categories with recommendation insights.",
    icon: IconRecommendations,
    tone: "rose",
  },
  {
    title: "Anomaly Detection",
    description: "Spot unusual patterns in sales and business activity.",
    icon: IconAnomaly,
    tone: "indigo",
  },
];

const outcomes = [
  { title: "Understand what drives sales", icon: IconSales },
  { title: "Plan for future revenue", icon: IconForecasting },
  { title: "Recognize customers at risk", icon: IconChurn },
  { title: "Find product growth opportunities", icon: IconRecommendations },
  { title: "Notice inventory and sales anomalies", icon: IconInventory },
];

function BrandMark() {
  return (
    <a className="landing-brand" href="#home" aria-label="MarketMind AI home">
      <span className="landing-brand-mark"><IconAI size={21} /></span>
      <span>MarketMind <strong>AI</strong></span>
    </a>
  );
}

function DashboardPreview() {
  return (
    <div className="landing-dashboard" aria-label="Preview of MarketMind business dashboard">
      <div className="landing-dashboard-topbar">
        <div className="landing-window-dots" aria-hidden="true"><i /><i /><i /></div>
        <span>Business overview</span>
        <span className="landing-dashboard-period">Sales intelligence</span>
      </div>
      <div className="landing-dashboard-content">
        <div className="landing-dashboard-heading">
          <div>
            <span className="landing-preview-eyebrow">MARKETMIND AI</span>
            <h2>Business overview</h2>
          </div>
          <span className="landing-preview-filter">All business</span>
        </div>
        <div className="landing-preview-metrics">
          <article className="landing-preview-card landing-preview-revenue">
            <span>Revenue</span>
            <strong>Sales performance</strong>
            <div className="landing-mini-chart" aria-hidden="true">
              <svg viewBox="0 0 250 58" preserveAspectRatio="none">
                <path d="M0 48 C20 43 25 31 45 38 S74 47 93 29 S125 35 145 20 S172 33 190 14 S225 25 250 5" />
                <path className="landing-chart-fill" d="M0 48 C20 43 25 31 45 38 S74 47 93 29 S125 35 145 20 S172 33 190 14 S225 25 250 5 V58 H0 Z" />
              </svg>
            </div>
            <small>Revenue trends</small>
          </article>
          <article className="landing-preview-card landing-preview-trend">
            <div className="landing-preview-card-heading"><span>Sales trend</span><IconSales size={16} /></div>
            <div className="landing-trend-bars" aria-hidden="true">
              {[36, 56, 43, 72, 54, 84, 64, 94, 73, 88, 62, 100].map((height, index) => (
                <i key={index} style={{ height: `${height}%` }} />
              ))}
            </div>
            <small>Performance by period</small>
          </article>
        </div>
        <div className="landing-preview-lower">
          <article className="landing-preview-card landing-preview-forecast">
            <div className="landing-preview-card-heading">
              <span>Sales forecast</span>
              <IconForecasting size={16} />
            </div>
            <div className="landing-forecast-graphic" aria-hidden="true">
              <span />
              <svg viewBox="0 0 340 80" preserveAspectRatio="none">
                <path className="landing-forecast-history" d="M0 61 C27 54 32 38 58 46 S94 60 118 39 S153 49 173 29" />
                <path className="landing-forecast-future" d="M173 29 C199 18 208 39 233 23 S276 32 294 14 S326 24 340 8" />
              </svg>
            </div>
            <div className="landing-forecast-legend"><i /> Historical <i /> Forecast</div>
          </article>
          <article className="landing-preview-card landing-preview-segments">
            <div className="landing-preview-card-heading"><span>Customer segments</span><IconSegmentation size={16} /></div>
            <div className="landing-segment-visual" aria-hidden="true">
              <span className="segment-vip" />
              <span className="segment-regular" />
              <span className="segment-occasional" />
              <span className="segment-at-risk" />
            </div>
            <div className="landing-segment-labels"><span>High value</span><span>Regular</span></div>
          </article>
        </div>
        <div className="landing-preview-alerts">
          <span className="landing-alert-icon"><IconChurn size={15} /></span>
          <span><strong>Churn risk</strong><small>Customer activity signals</small></span>
          <span className="landing-alert-icon inventory-alert"><IconInventory size={15} /></span>
          <span><strong>Inventory alert</strong><small>Stock and reorder signals</small></span>
        </div>
      </div>
    </div>
  );
}

export default function LandingPage({ onLogin, onGetStarted, onUploadData }) {
  return (
    <div className="landing-page" id="home">
      <header className="landing-nav">
        <div className="landing-nav-inner">
          <BrandMark />
          <nav className="landing-nav-links" aria-label="Main navigation">
            <a href="#products">Products</a>
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#why-marketmind">Why MarketMind</a>
            <a href="#contact">Contact</a>
          </nav>
          <div className="landing-nav-actions">
            <button type="button" className="landing-login-link" onClick={onLogin}>Log In</button>
            <button type="button" className="landing-button landing-button-small" onClick={onGetStarted}>
              Get Started <IconArrowRight size={15} />
            </button>
          </div>
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-inner">
            <div className="landing-hero-copy">
              <div className="landing-hero-badge"><span /> AI-POWERED <i /> DATA-DRIVEN <i /> BUILT FOR SMALL BUSINESSES</div>
              <h1>Turn Sales Data Into <span>Smarter Business Decisions</span></h1>
              <p>
                AI-powered sales analytics, forecasting, customer intelligence
                and revenue growth insights for small businesses.
              </p>
              <div className="landing-hero-actions">
                <button type="button" className="landing-button" onClick={onGetStarted}>
                  Get Started <IconArrowRight size={17} />
                </button>
                <a href="#features" className="landing-button landing-button-outline">Explore Features</a>
              </div>
              <div className="landing-hero-note">
                <span><IconUpload size={15} /></span>
                Bring your own CSV or Excel data when you are ready.
              </div>
            </div>
            <div className="landing-hero-visual"><DashboardPreview /></div>
          </div>
        </section>

        <section className="landing-trust-strip" aria-label="MarketMind capabilities">
          <div className="landing-trust-inner">
            {trustItems.map(({ label, icon: Icon }) => (
              <div className="landing-trust-item" key={label}><Icon size={17} /><span>{label}</span></div>
            ))}
          </div>
        </section>

        <section className="landing-section landing-products" id="products">
          <div className="landing-section-heading" id="features">
            <span className="landing-section-kicker">ONE PLATFORM FOR YOUR BUSINESS</span>
            <h2>Clarity for every part of your sales</h2>
            <p>Bring your key business signals together and turn them into practical next steps.</p>
          </div>
          <div className="landing-feature-grid">
            {features.map(({ title, description, icon: Icon, tone }) => (
              <article className="landing-feature-card" key={title}>
                <span className={`landing-feature-icon tone-${tone}`}><Icon size={21} /></span>
                <h3>{title}</h3>
                <p>{description}</p>
                <a href="#how-it-works">Explore <span>→</span></a>
              </article>
            ))}
          </div>
        </section>

        <section className="landing-upload-section" id="upload-data">
          <div className="landing-upload-copy">
            <span className="landing-section-kicker">YOUR DATA, YOUR BUSINESS</span>
            <h2>Bring Your Own Business Data</h2>
            <p>Upload your CSV or Excel file and analyze your business with MarketMind AI.</p>
            <button type="button" className="landing-button" onClick={onUploadData}>
              Upload Your Data <IconArrowRight size={17} />
            </button>
          </div>
          <div className="landing-upload-steps">
            {[
              { title: "Flexible files", description: "CSV · XLSX · XLS", icon: IconUpload },
              { title: "Data validation", description: "Check columns and readiness", icon: IconAI },
              { title: "Preview & analyze", description: "Review rows, then explore insights", icon: IconSales },
            ].map(({ title, description, icon: Icon }, index) => (
              <div className="landing-upload-step" key={title}>
                <span className="landing-upload-step-icon"><Icon size={18} /></span>
                <span className="landing-upload-step-text"><strong>{title}</strong><small>{description}</small></span>
                {index < 2 && <span className="landing-upload-step-divider" />}
              </div>
            ))}
          </div>
        </section>

        <section className="landing-section landing-how" id="how-it-works">
          <div className="landing-section-heading">
            <span className="landing-section-kicker">HOW IT WORKS</span>
            <h2>From business data to clear next steps</h2>
            <p>A simple workflow designed to help you move from information to action.</p>
          </div>
          <div className="landing-process">
            {[
              { number: "01", title: "Upload Data", icon: IconUpload },
              { number: "02", title: "AI Analysis", icon: IconAI },
              { number: "03", title: "Get Insights", icon: IconSales },
              { number: "04", title: "Make Better Decisions", icon: IconArrowRight },
            ].map(({ number, title, icon: Icon }, index) => (
              <div className="landing-process-item" key={number}>
                <div className="landing-process-icon"><Icon size={22} /></div>
                <span>{number}</span>
                <strong>{title}</strong>
                {index < 3 && <i className="landing-process-arrow" aria-hidden="true">→</i>}
              </div>
            ))}
          </div>
        </section>

        <section className="landing-value-section" id="why-marketmind">
          <div className="landing-value-inner">
            <div className="landing-value-heading">
              <span className="landing-section-kicker">WHY MARKETMIND AI</span>
              <h2>From Data to Decisions</h2>
              <p>Focus on business questions that matter, with analysis built around your sales and customers.</p>
            </div>
            <div className="landing-outcome-list">
              {outcomes.map(({ title, icon: Icon }) => (
                <div className="landing-outcome" key={title}><span><Icon size={17} /></span><strong>{title}</strong></div>
              ))}
            </div>
          </div>
        </section>

        <section className="landing-final-cta">
          <div>
            <span className="landing-section-kicker">MARKETMIND AI</span>
            <h2>Make Smarter Decisions With MarketMind AI</h2>
            <p>Bring your sales data into one place and find a clearer path forward.</p>
          </div>
          <div className="landing-final-actions">
            <button type="button" className="landing-button landing-button-light" onClick={onGetStarted}>Get Started <IconArrowRight size={17} /></button>
            <a href="#products" className="landing-button landing-button-dark-outline">Explore the Platform</a>
          </div>
        </section>
      </main>

      <footer className="landing-footer" id="contact">
        <div className="landing-footer-main">
          <div className="landing-footer-about">
            <BrandMark />
            <p>Sales forecasting and revenue growth intelligence for small businesses.</p>
          </div>
          <div className="landing-footer-column">
            <strong>Products</strong>
            <a href="#products">Sales Analytics</a>
            <a href="#products">Sales Forecasting</a>
            <a href="#upload-data">Data Upload</a>
          </div>
          <div className="landing-footer-column">
            <strong>Explore</strong>
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#why-marketmind">Why MarketMind</a>
          </div>
          <div className="landing-footer-column">
            <strong>Get started</strong>
            <button type="button" onClick={onLogin}>Log In</button>
            <button type="button" onClick={onGetStarted}>Create an account</button>
            <a href="#contact">Contact</a>
          </div>
        </div>
        <div className="landing-footer-bottom"><span>© {new Date().getFullYear()} MarketMind AI</span><span>Built for better business decisions.</span></div>
      </footer>
    </div>
  );
}
