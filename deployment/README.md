# MarketMind AI — Milestone 4 Deployment Guide

This directory contains complete information regarding the cloud deployment of MarketMind AI on Vercel.

## 🔗 Live Application Links
- **Primary Production URL:** [https://marketmind-wheat.vercel.app](https://marketmind-wheat.vercel.app)
- **Deployment Alias:** [https://marketmind-25am064-2262.vercel.app](https://marketmind-25am064-2262.vercel.app)
- **API Health Check:** [https://marketmind-wheat.vercel.app/api/health](https://marketmind-wheat.vercel.app/api/health)

---

## 📋 Overview
MarketMind AI has been deployed to **Vercel** utilizing a serverless architecture:
1. **Frontend:** Deployed as static edge assets with custom CSS design tokens, responsive desktop views, and touch-optimized mobile interfaces.
2. **Backend API:** Built with **FastAPI** and executed through Vercel's Python Serverless Functions via `api/index.py`.
3. **Database Layer:** SQLite database seeded with 9,994 retail transactions, dynamically mirrored to `/tmp/marketmind.db` for serverless write compatibility (dataset uploads and telemetry tracking).

---

## 🔑 Demo Access Accounts

Use the one-click demo credentials below to access the platform:

| Role | Username / Email | Password |
| :--- | :--- | :--- |
| **Business Owner** | `owner@marketmind.ai` | `OwnerPass123!` |
| **Store Manager** | `manager@marketmind.ai` | `ManagerPass123!` |
| **Sales Executive** | `sales@marketmind.ai` | `SalesPass123!` |
| **Administrator** | `admin@marketmind.ai` | `AdminPass123!` |

---

## 📱 Mobile & Desktop Device Optimization
- **Desktop / Laptop (> 768px):** Multi-column KPI grid, 2-column comparative analytics, full-text button labels, persistent sidebar.
- **Mobile Phones (≤ 768px):** 2-row adaptive header, off-canvas sliding sidebar with backdrop, compact icon controls, single-column stacked KPI layout, zero horizontal viewport overflow.
