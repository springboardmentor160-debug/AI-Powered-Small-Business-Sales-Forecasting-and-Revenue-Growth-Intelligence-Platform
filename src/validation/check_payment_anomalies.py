import pandas as pd
from pathlib import Path

# ============================================================
# MARKETMIND AI — PHASE 2
# PAYMENT ANOMALY CHECK
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = BASE_DIR / "data" / "processed" / "order_payments_clean.csv"

print("=" * 70)
print("MARKETMIND AI — PHASE 2")
print("PAYMENT ANOMALY CHECK")
print("=" * 70)

df = pd.read_csv(FILE)

# ------------------------------------------------------------
# 1. INVALID INSTALLMENTS
# ------------------------------------------------------------

print("\n[1] INVALID PAYMENT INSTALLMENTS")
print("-" * 50)

bad_installments = df[df["payment_installments"] <= 0]

print("Invalid rows:", len(bad_installments))

if len(bad_installments) > 0:
    print("\nAnomalous records:")
    print(bad_installments.to_string(index=False))
else:
    print("✓ No invalid installments found")


# ------------------------------------------------------------
# 2. ZERO PAYMENT VALUES
# ------------------------------------------------------------

print("\n[2] ZERO PAYMENT VALUES")
print("-" * 50)

zero_payment = df[df["payment_value"] == 0]

print("Zero-payment rows:", len(zero_payment))

if len(zero_payment) > 0:
    print(zero_payment.to_string(index=False))


# ------------------------------------------------------------
# 3. NEGATIVE PAYMENT VALUES
# ------------------------------------------------------------

print("\n[3] NEGATIVE PAYMENT VALUES")
print("-" * 50)

negative_payment = df[df["payment_value"] < 0]

print("Negative-payment rows:", len(negative_payment))


# ------------------------------------------------------------
# 4. PAYMENT TYPE CHECK
# ------------------------------------------------------------

print("\n[4] PAYMENT TYPES")
print("-" * 50)

print(df["payment_type"].value_counts(dropna=False))


# ------------------------------------------------------------
# 5. FINAL DECISION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PAYMENT ANOMALY CHECK SUMMARY")
print("=" * 70)

if len(bad_installments) == 0:
    print("✓ Payment installments: PASS")
else:
    print(
        f"⚠ Invalid payment installments: "
        f"{len(bad_installments)}"
    )

if len(negative_payment) == 0:
    print("✓ Negative payment values: PASS")
else:
    print(
        f"⚠ Negative payment values: "
        f"{len(negative_payment)}"
    )

print("\n" + "=" * 70)
print("PAYMENT CHECK COMPLETE")
print("=" * 70)