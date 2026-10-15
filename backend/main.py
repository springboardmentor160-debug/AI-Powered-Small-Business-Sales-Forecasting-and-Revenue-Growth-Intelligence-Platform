"""MarketMind AI - FastAPI app (all routes).
Store/sales data is queried live from the SQLite database; AI results are the JSON/CSV files produced by ../ml (see ml/outputs)."""
import hmac
import json
import math
from contextlib import asynccontextmanager
from datetime import date, timedelta
from typing import Annotated
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import and_, func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
import pandas as pd

import config
import models
import resettokens
from auth import ACCESS, create_access_token, get_current_user, hash_password, require_access, verify_password
from config import CORS_ORIGINS, ML_OUTPUTS as OUTPUTS
from database import get_db
from daterange import RANGE_DAYS, RANGE_PATTERN, previous_window, shift_dates_deep, shift_days, shift_str, window_start
from init_db import init_database
from mailer import send_reset_email
from models import utcnow
from schemas import (ForgotPassword, InvoiceCreate, InvoiceOut, InvoiceStatusUpdate, ResetPassword, Token, UserLogin, UserOut,
                     UserRegister)


@asynccontextmanager
async def lifespan(_app):
    init_database()          # tables + roles + admin (from env) exist even if init_db.py was never run; never deletes anything
    yield


app = FastAPI(title="MarketMind AI Backend", version="1.1", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_cache: dict = {}


def read_output(name: str):
    """Load an ML output file (cached until the file changes). 503 with a clear message if it hasn't been generated."""
    p = OUTPUTS / name
    if not p.exists():
        raise HTTPException(503, f"{name} is not available yet - run the ML pipeline (see README)")
    key = (name, p.stat().st_mtime)
    if key not in _cache:
        try:
            _cache.clear() if len(_cache) > 40 else None
            _cache[key] = json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" else pd.read_csv(p, dtype={"customer_id": str})
        except Exception:
            raise HTTPException(503, f"{name} could not be read")
    return _cache[key]


def db_guard(fn):
    """Turn database outages into a calm 503 instead of a stack trace."""
    try:
        return fn()
    except SQLAlchemyError:
        raise HTTPException(503, "Database is temporarily unavailable")


@app.get("/")
def root():
    return {"message": "MarketMind AI backend is running"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except SQLAlchemyError:
        database = "unavailable"
    return {"status": "ok" if database == "ok" else "degraded", "database": database}


# ---------------------------------------------------------------- auth
@app.post("/register", response_model=UserOut, status_code=201)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if body.role == "admin":
        expected = config.ADMIN_REGISTRATION_CODE
        if not expected:
            raise HTTPException(403, "Administrator sign-up is turned off. Set ADMIN_REGISTRATION_CODE in backend/.env to enable it, "
                                     "or ask an existing administrator to create the account.")
        if not hmac.compare_digest((body.admin_code or "").encode("utf-8"), expected.encode("utf-8")):
            raise HTTPException(403, "Wrong administrator access code")
    return _create_user(body, db)


def _create_user(body: UserRegister, db: Session):
    def run():
        if db.query(models.User).filter(models.User.email == body.email.lower()).first():
            raise HTTPException(400, "Email already registered")
        role = db.query(models.Role).filter_by(name=body.role).first()
        if not role:
            raise HTTPException(500, "Roles not initialised - run init_db.py")
        u = models.User(name=body.name, email=body.email.lower(), hashed_password=hash_password(body.password), role_id=role.id)
        db.add(u)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(400, "Email already registered")
        db.refresh(u)
        return UserOut(id=u.id, name=u.name, email=u.email, role=role.name)
    return db_guard(run)


@app.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)):
    u = db_guard(lambda: db.query(models.User).filter(models.User.email == body.email.lower()).first())
    if not u or not verify_password(body.password, u.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return Token(access_token=create_access_token(u.email, u.role.name, u.name), role=u.role.name, name=u.name)


FORGOT_REPLY = {"message": "If that e-mail address is registered, a reset link is on its way. Please check your inbox (and spam folder)."}


@app.post("/auth/forgot-password")
def forgot_password(body: ForgotPassword, background: BackgroundTasks, db: Session = Depends(get_db)):
    """Always answers the same way, so nobody can use this form to find out which e-mail addresses have accounts."""
    def run():
        u = db.query(models.User).filter(models.User.email == body.email.lower()).first()
        if not u:
            return
        now = utcnow()
        if db.query(models.PasswordResetToken).filter(models.PasswordResetToken.user_id == u.id,
                                                      models.PasswordResetToken.created_at > now - timedelta(seconds=60)).first():
            return                                   # at most one reset e-mail per minute per account (stops mail-bombing)
        db.query(models.PasswordResetToken).filter(models.PasswordResetToken.user_id == u.id,
                                                   models.PasswordResetToken.used_at.is_(None)).update({"used_at": now})   # older links die
        token = resettokens.new_token()
        db.add(models.PasswordResetToken(user_id=u.id, token_hash=resettokens.hash_token(token), created_at=now,
                                         expires_at=now + timedelta(minutes=config.RESET_TOKEN_MINUTES)))
        db.commit()
        background.add_task(send_reset_email, u.email, u.name, f"{config.FRONTEND_URL}/?reset_token={token}")
    db_guard(run)
    return FORGOT_REPLY


@app.post("/auth/reset-password")
def reset_password(body: ResetPassword, db: Session = Depends(get_db)):
    def run():
        rec = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token_hash == resettokens.hash_token(body.token)).first()
        if not rec or rec.used_at is not None or rec.expires_at < utcnow():
            raise HTTPException(400, "This reset link is invalid or has expired. Please request a new one.")
        u = db.get(models.User, rec.user_id)
        if not u:
            raise HTTPException(400, "This reset link is invalid or has expired. Please request a new one.")
        u.hashed_password = hash_password(body.new_password)
        rec.used_at = utcnow()
        db.commit()
        return {"message": "Your password has been updated. You can now log in."}
    return db_guard(run)


@app.get("/me")
def me(user: dict = Depends(get_current_user)):
    """Who am I + which features my role may use (the frontend builds its role-aware views from this)."""
    return {"email": user["sub"], "name": user.get("name"), "role": user["role"],
            "features": [f for f, roles in ACCESS.items() if user["role"] in roles]}


# ---------------------------------------------------------------- sales & inventory (database)
# Every store-data endpoint takes ?range=7d|30d|90d|365d|all (the dashboard's date dropdown), counted back from the newest record.
# Dates sent to the browser are shifted forward when REBASE_DATES_TO_TODAY is on (see daterange.py); filtering uses the original dates.
RangeParam = Annotated[str, Query(alias="range", pattern=RANGE_PATTERN)]


def _last_date(db: Session):
    return db.query(func.max(models.SalesTransaction.date)).scalar()


def _shift(last) -> int:
    return shift_days(last, date.today(), config.REBASE_DATES_TO_TODAY)


def _range_start(db: Session, rng: str):
    return window_start(_last_date(db), RANGE_DAYS[rng])


@app.get("/sales/summary")
def sales_summary(range_: RangeParam = "all", db: Session = Depends(get_db), user: dict = Depends(require_access("sales_summary"))):
    S = models.SalesTransaction

    def totals(lo, hi=None):
        q = db.query(func.coalesce(func.sum(S.revenue), 0), func.coalesce(func.sum(S.units_sold), 0), func.count(S.id))
        if lo:
            q = q.filter(S.date >= lo)
        if hi:
            q = q.filter(S.date <= hi)
        return q.one()

    def run():
        first, last, rows_all = db.query(func.min(S.date), func.max(S.date), func.count(S.id)).one()
        if not rows_all:
            raise HTTPException(503, "No sales data loaded - run load_data.py")
        days = RANGE_DAYS[range_]
        start = window_start(last, days)
        total, units, rows = totals(start)
        shift = _shift(last)
        today = db.query(func.sum(S.revenue)).filter(S.date == last).scalar()
        top_q = db.query(S.product_id, func.sum(S.revenue).label("r"))
        if start:
            top_q = top_q.filter(S.date >= start)
        top = top_q.group_by(S.product_id).order_by(func.sum(S.revenue).desc()).first()
        low = db.query(func.count(S.id)).filter(S.date == last, S.inventory_level < S.reorder_point).scalar()
        change = None                                   # % change versus the equally long window before this one (needs full data for it)
        if days:
            prev_start, prev_end = previous_window(last, days)
            if prev_start >= first:
                prev = float(totals(prev_start, prev_end)[0])
                if prev > 0:
                    change = round((float(total) - prev) / prev * 100, 1)
        return {"total_revenue": round(float(total), 2), "total_units": int(units), "total_orders": rows, "latest_date": shift_str(last, shift),
                "sales_latest_day": round(float(today or 0), 2), "top_product": top[0] if top else None, "low_stock_count": int(low or 0),
                "range": range_, "range_days": days, "range_start": shift_str(start or first, shift), "range_end": shift_str(last, shift),
                "change_pct": change, "date_shift_days": shift, "source_start": str(first), "source_end": str(last)}
    return db_guard(run)


@app.get("/sales/trend")
def sales_trend(days: int = Query(30, ge=7, le=365), range_: str | None = Query(None, alias="range", pattern=RANGE_PATTERN),
                db: Session = Depends(get_db), user: dict = Depends(require_access("sales_summary"))):
    """Daily revenue. With ?range= it covers that window; without it, the last `days` days (older behaviour)."""
    S = models.SalesTransaction

    def run():
        last = _last_date(db)
        if last is None:
            return []
        q = db.query(S.date, func.sum(S.revenue)).group_by(S.date)
        if range_ is not None:
            start = window_start(last, RANGE_DAYS[range_])
            rows = (q.filter(S.date >= start) if start else q).order_by(S.date).all()
        else:
            rows = list(reversed(q.order_by(S.date.desc()).limit(days).all()))
        shift = _shift(last)
        return [{"date": shift_str(d, shift), "revenue": round(float(r), 2)} for d, r in rows]
    return db_guard(run)


@app.get("/sales/by-category")
def sales_by_category(range_: RangeParam = "all", db: Session = Depends(get_db), user: dict = Depends(require_access("sales_summary"))):
    S = models.SalesTransaction

    def run():
        start = _range_start(db, range_)
        q = db.query(S.category, func.sum(S.revenue), func.sum(S.units_sold))
        return (q.filter(S.date >= start) if start else q).group_by(S.category).order_by(func.sum(S.revenue).desc()).all()
    rows = db_guard(run)
    total = sum(float(r or 0) for _, r, _ in rows) or 1.0
    return [{"category": c, "revenue": round(float(r or 0), 2), "units_sold": int(u or 0), "share_pct": round(float(r or 0) / total * 100, 1)}
            for c, r, u in rows]


@app.get("/sales/by-store")
def sales_by_store(range_: RangeParam = "all", db: Session = Depends(get_db), user: dict = Depends(require_access("sales_summary"))):
    S = models.SalesTransaction

    def run():
        start = _range_start(db, range_)
        q = db.query(S.store_id, S.region, func.sum(S.revenue), func.sum(S.units_sold))
        return (q.filter(S.date >= start) if start else q).group_by(S.store_id, S.region).order_by(func.sum(S.revenue).desc()).all()
    rows = db_guard(run)
    return [{"store_id": st, "region": rg, "revenue": round(float(r or 0), 2), "units_sold": int(u or 0)} for st, rg, r, u in rows]


@app.get("/sales/top-products")
def sales_top_products(limit: int = Query(10, ge=1, le=50), range_: RangeParam = "all", db: Session = Depends(get_db),
                       user: dict = Depends(require_access("sales_summary"))):
    S = models.SalesTransaction

    def run():
        start = _range_start(db, range_)
        q = db.query(S.product_id, S.category, func.sum(S.revenue), func.sum(S.units_sold))
        return (q.filter(S.date >= start) if start else q).group_by(S.product_id, S.category).order_by(func.sum(S.revenue).desc()).limit(limit).all()
    rows = db_guard(run)
    return [{"product_id": p, "category": c, "revenue": round(float(r or 0), 2), "units_sold": int(u or 0)} for p, c, r, u in rows]


@app.get("/inventory/alerts")
def inventory_alerts(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db),
                     user: dict = Depends(require_access("inventory_alerts"))):
    """Latest day's rows where stock is below the reorder point (most severe shortfall first)."""
    S = models.SalesTransaction
    def run():
        last = _last_date(db)
        q = (db.query(S).filter(S.date == last, S.inventory_level < S.reorder_point)
             .order_by((S.reorder_point - S.inventory_level).desc()).limit(limit).all())
        return {"date": shift_str(last, _shift(last)) if last else None,
                "alerts": [{"store_id": r.store_id, "product_id": r.product_id, "category": r.category,
                            "stock_level": r.inventory_level, "reorder_point": r.reorder_point,
                            "shortfall": r.reorder_point - r.inventory_level} for r in q]}
    return db_guard(run)


@app.get("/inventory/summary")
def inventory_summary(target_days: int = Query(3, ge=1, le=60), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db),
                      user: dict = Depends(require_access("inventory_alerts"))):
    """Inventory intelligence for the latest day: days of cover, stock status and a suggested reorder quantity.

    days_of_cover = stock / average daily units sold (whole history, per store+product).
    status: critical = under 1 day of cover, low = below the reorder point, overstock = stock above 2.5x the reorder point.
    suggested_reorder_qty = units needed to reach `target_days` of cover (a heuristic, not a supplier lead-time model)."""
    S = models.SalesTransaction

    def run():
        last = db.query(func.max(S.date)).scalar()
        if last is None:
            raise HTTPException(503, "No sales data loaded - run load_data.py")
        avg = (db.query(S.store_id.label("s"), S.product_id.label("p"), func.avg(S.units_sold).label("avg_units"))
               .group_by(S.store_id, S.product_id).subquery())
        rows = (db.query(S.store_id, S.product_id, S.category, S.inventory_level, S.reorder_point, avg.c.avg_units)
                .join(avg, and_(S.store_id == avg.c.s, S.product_id == avg.c.p)).filter(S.date == last).all())
        items, counts, by_cat = [], {"critical": 0, "low": 0, "healthy": 0, "overstock": 0}, {}
        for st, pid, cat, inv, rp, au in rows:
            au = float(au or 0); inv = inv or 0; rp = rp or 0
            cover = inv / au if au > 0 else None
            status = ("critical" if cover is not None and cover < 1 else "low" if inv < rp else "overstock" if inv > 2.5 * rp else "healthy")
            counts[status] += 1
            c = by_cat.setdefault(cat, {"category": cat, "critical": 0, "low": 0, "healthy": 0, "overstock": 0}); c[status] += 1
            if status in ("critical", "low"):
                items.append({"store_id": st, "product_id": pid, "category": cat, "stock_level": inv, "reorder_point": rp,
                              "days_of_cover": round(cover, 2) if cover is not None else None, "status": status,
                              "suggested_reorder_qty": max(0, math.ceil(au * target_days) - inv)})
        items.sort(key=lambda i: (i["days_of_cover"] if i["days_of_cover"] is not None else 1e9))
        return {"date": shift_str(last, _shift(last)), "target_days": target_days, "total_items": len(rows), "status_counts": counts,
                "by_category": sorted(by_cat.values(), key=lambda c: c["category"] or ""), "most_urgent": items[:limit]}
    return db_guard(run)


# ---------------------------------------------------------------- AI modules (ml/outputs)
@app.get("/segments")
def get_segments(user: dict = Depends(require_access("segments"))):
    return read_output("segments.json")


@app.get("/segments/metrics")
def get_segment_metrics(user: dict = Depends(require_access("segments"))):
    return read_output("segmentation_metrics.json")


@app.get("/segments/dendrogram")
def get_dendrogram(user: dict = Depends(require_access("segments"))):
    p = OUTPUTS / "dendrogram.png"
    if not p.exists():
        raise HTTPException(503, "dendrogram.png is not available yet - run ml/segmentation.py")
    return FileResponse(p, media_type="image/png")


@app.get("/forecast/revenue")
def get_revenue_forecast(db: Session = Depends(get_db), user: dict = Depends(require_access("forecast"))):
    data = read_output("forecast.json")
    shift = _shift(db_guard(lambda: _last_date(db)))          # same shift as the sales dates, so history and forecast line up
    return shift_dates_deep(data, shift)


@app.get("/recommendations/{customer_id}")
def get_recommendations(customer_id: str, product: str | None = None, user: dict = Depends(require_access("recommendations"))):
    data = read_output("recommendations.json")
    if customer_id not in data["for_you"]:
        raise HTTPException(404, f"Customer {customer_id} not found")
    out = {"customer_id": customer_id, "recommended_for_you": data["for_you"][customer_id]}
    if product:
        out["frequently_bought_with"] = data["frequently_bought_with"].get(product.upper(), [])
        out["product"] = {"code": product.upper(), "name": data["names"].get(product.upper())}
    return out


@app.get("/recommendations")
def sample_customers(user: dict = Depends(require_access("recommendations"))):
    d = read_output("recommendations.json")
    return {"sample_customers": list(d["for_you"])[:8], "sample_products": list(d["frequently_bought_with"])[:5]}


@app.get("/churn/risk")
def churn_risk(risk: str | None = Query(None, pattern="^(High|Medium|Low) Risk$"), limit: int = Query(25, ge=1, le=200),
               user: dict = Depends(require_access("churn"))):
    df = read_output("churn_predictions.csv")
    m = read_output("churn_metrics.json")
    sub = df if not risk else df[df["retention_risk"] == risk]
    cols = ["customer_id", "churn_probability", "retention_risk", "order_frequency", "inactivity_days", "avg_order_value", "segment"]
    return {"counts": m["risk_counts"], "selected_model": m["selected_model"], "risk_by_segment": m.get("risk_by_segment", {}),
            "customers": json.loads(sub.head(limit)[[c for c in cols if c in sub]].to_json(orient="records"))}


@app.get("/anomalies")
def anomalies(severity: str | None = Query(None, pattern="^(high|medium)$"), limit: int = Query(25, ge=1, le=200), range_: RangeParam = "all",
              db: Session = Depends(get_db), user: dict = Depends(require_access("anomalies"))):
    df = read_output("anomaly_alerts.csv")
    last = db_guard(lambda: _last_date(db))
    start = window_start(last, RANGE_DAYS[range_])
    if start is not None:
        df = df[pd.to_datetime(df["date"]).dt.date >= start]
    shift = _shift(last)
    sub = df if not severity else df[df["severity"] == severity]
    alerts = json.loads(sub.head(limit).to_json(orient="records"))
    for a in alerts:
        if shift and a.get("date"):
            old, new = str(a["date"])[:10], shift_str(a["date"], shift)
            a["date"] = new
            a["message"] = str(a.get("message", "")).replace(old, new, 1)
    return {"total": len(df), "high": int((df["severity"] == "high").sum()), "medium": int((df["severity"] == "medium").sum()), "alerts": alerts}


@app.get("/models/performance")
def model_performance(user: dict = Depends(require_access("model_performance"))):
    """Milestone 4: every module's measured evaluation results, read from the files the ML scripts wrote.
    Sections whose script has not been run are reported as null instead of being invented."""
    def opt(name):
        try:
            return read_output(name)
        except HTTPException:
            return None
    return {"forecasting": opt("forecast_model_comparison.json"), "segmentation": opt("segmentation_metrics.json"),
            "churn": opt("churn_metrics.json"), "recommendations": opt("recsys_eval.json"),
            "anomalies": (opt("anomaly_eval.json") or {}), "data_notes": opt("data_quality.json")}


@app.get("/reports/business")
def download_report(user: dict = Depends(require_access("report_download"))):
    p = OUTPUTS / "business_report.xlsx"
    if not p.exists():
        raise HTTPException(503, "Report not generated yet - run ml/generate_reports.py")
    return FileResponse(p, filename="business_report.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ---------------------------------------------------------------- invoices
@app.post("/invoices", response_model=InvoiceOut, status_code=201)
def create_invoice(body: InvoiceCreate, db: Session = Depends(get_db), user: dict = Depends(require_access("invoice_create"))):
    def run():
        inv = models.Invoice(**body.model_dump(), created_by=user["id"])
        db.add(inv); db.commit(); db.refresh(inv)
        return inv
    return db_guard(run)


@app.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db), user: dict = Depends(require_access("invoice_view"))):
    return db_guard(lambda: db.query(models.Invoice).order_by(models.Invoice.id.desc()).limit(200).all())


@app.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), user: dict = Depends(require_access("invoice_view"))):
    inv = db_guard(lambda: db.get(models.Invoice, invoice_id))
    if not inv:
        raise HTTPException(404, "Invoice not found")
    return inv


@app.patch("/invoices/{invoice_id}", response_model=InvoiceOut)
def update_invoice_status(invoice_id: int, body: InvoiceStatusUpdate, db: Session = Depends(get_db),
                          user: dict = Depends(require_access("invoice_create"))):
    def run():
        inv = db.get(models.Invoice, invoice_id)
        if not inv:
            raise HTTPException(404, "Invoice not found")
        inv.payment_status = body.payment_status
        db.commit(); db.refresh(inv)
        return inv
    return db_guard(run)


# ---------------------------------------------------------------- admin: user management
@app.get("/admin/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), user: dict = Depends(require_access("user_management"))):
    users = db_guard(lambda: db.query(models.User).order_by(models.User.id).all())
    return [UserOut(id=u.id, name=u.name, email=u.email, role=u.role.name) for u in users]


@app.post("/admin/users", response_model=UserOut, status_code=201)
def admin_create_user(body: UserRegister, db: Session = Depends(get_db), user: dict = Depends(require_access("user_management"))):
    return _create_user(body, db)


@app.delete("/admin/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), user: dict = Depends(require_access("user_management"))):
    def run():
        u = db.get(models.User, user_id)
        if not u:
            raise HTTPException(404, "User not found")
        if u.email == user["sub"]:
            raise HTTPException(400, "You cannot delete your own account")
        db.query(models.Invoice).filter(models.Invoice.created_by == u.id).update({"created_by": None})   # keep invoices, drop the link
        db.query(models.PasswordResetToken).filter(models.PasswordResetToken.user_id == u.id).delete()
        db.delete(u); db.commit()
    db_guard(run)
