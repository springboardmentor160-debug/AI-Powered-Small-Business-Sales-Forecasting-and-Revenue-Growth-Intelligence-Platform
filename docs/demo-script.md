# 10-minute live demo script

**Before you start:** open the API URL once so it is awake, sign out, and keep the test-results CSV open in a second tab.

| Min | Show | Say |
|---|---|---|
| 0:00 | Login screen (move the mouse through the particles) | "MarketMind AI turns a small business's sales history into decisions: forecasts, customer groups, churn, recommendations and fraud alerts." |
| 1:00 | Sign in as admin → Dashboard | "Revenue and orders are live from the API; the LIVE badge is a real heartbeat measuring backend latency every 5 seconds." |
| 2:30 | Press **Ctrl+K** → jump to Forecasts | "Five modules sit behind one secure API. Here are the forecasts." |
| 3:30 | Forecasts page | "Random Forest explains about half of daily revenue (R² 0.50); Prophet scored below zero, so we don't use it. We report that honestly." |
| 4:30 | Customers / Churn / Recommendations | "Four segments (silhouette 0.57). Churn model: 77% accuracy vs 44% for always guessing, 85% recall. Collaborative filtering beats popularity by 47% on precision." |
| 6:00 | Alerts | "Isolation Forest catches 38% of injected extreme invoices at a 0.35% false-alarm rate. Accuracy alone would say 99% and mislead, which is why we report recall." |
| 7:00 | Invoices → **Create New Invoice** → create → **Download** | "Sales executives and admins can create invoices; every row downloads as a formatted invoice." |
| 8:00 | Administration → Add user, change a role, Update | "Admin-only. Roles are enforced on the backend. Passwords are bcrypt-hashed, so they can't be viewed." |
| 9:00 | Stop the backend → reload (optional, if comfortable) | "If the server dies, users see a clear message, not a blank screen." |
| 9:30 | Deployed URL | "The same platform runs in the cloud via Docker." |

**Likely questions**
- *Why is anomaly recall only 38%?* The detector is tuned strict (0.5% flagged). We measured it honestly with injected cases, since no real fraud labels exist, and know the lever to raise it.
- *Why k=4 clusters when k=3 scores higher?* k=3's smallest group has 25 customers; k=4 gives usable segments.
- *Is the data real?* UCI Online Retail (transactions) and M5 (demand), cleaned and reconciled in Milestone 2.
