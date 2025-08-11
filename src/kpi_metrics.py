"""
KPI computation utilities for a real-estate portfolio.
All functions are pure and pandas-in/pandas-out so they are easy to test.
"""

from __future__ import annotations

import pandas as pd


def rent_roll_health(tenants: pd.DataFrame) -> pd.DataFrame:
    """
    Compute simple rent-roll health metrics by property.

    Expected columns in `tenants`:
    - property_id (str)
    - unit_id (str)
    - is_occupied (bool or 0/1)
    - monthly_rent (numeric)

    Returns a DataFrame with:
    - property_id
    - occupancy_rate
    - avg_rent
    - total_monthly_rent
    """
    df = tenants.copy()
    df["is_occupied"] = df["is_occupied"].astype(int)
    grp = df.groupby("property_id", as_index=False)
    out = grp.agg(
        units=("unit_id", "count"),
        occupied=("is_occupied", "sum"),
        avg_rent=("monthly_rent", "mean"),
        total_monthly_rent=("monthly_rent", "sum"),
    )
    out["occupancy_rate"] = out["occupied"] / out["units"]
    cols = [
        "property_id",
        "occupancy_rate",
        "avg_rent",
        "total_monthly_rent",
    ]
    return out[cols]


def arrears_aging(ledger: pd.DataFrame) -> pd.DataFrame:
    """
    Build an arrears aging table (0-30, 31-60, 61-90, 90+).

    Expected columns:
    - tenant_id (str)
    - days_past_due (int)
    - balance (numeric)
    """
    df = ledger.copy()
    bins = [-1, 30, 60, 90, 10_000]
    labels = ["0-30", "31-60", "61-90", "90+"]
    df["bucket"] = pd.cut(df["days_past_due"], bins=bins, labels=labels)
    out = (
        df.groupby("bucket", as_index=False)["balance"]
        .sum()
        .rename(columns={"balance": "amount"})
    )
    # ensure all buckets exist even if zero
    out = (
        pd.DataFrame({"bucket": labels})
        .merge(out, on="bucket", how="left")
        .fillna({"amount": 0.0})
    )
    return out


def lease_expiries(leases: pd.DataFrame, as_of: str) -> pd.DataFrame:
    """
    Count leases expiring in the next 30/60/90/180 days from `as_of`.

    Expected columns:
    - lease_id (str)
    - end_date (datetime-like)
    """
    df = leases.copy()
    df["end_date"] = pd.to_datetime(df["end_date"])
    ref = pd.to_datetime(as_of)

    horizons = {
        "30d": 30,
        "60d": 60,
        "90d": 90,
        "180d": 180,
    }
    rows = []
    for label, days in horizons.items():
        cutoff = ref + pd.Timedelta(days=days)
        mask = (df["end_date"] > ref) & (df["end_date"] <= cutoff)
        rows.append({"horizon": label, "expiring": int(mask.sum())})
    return pd.DataFrame(rows)


def noi_bridge(pnl_prev: pd.DataFrame, pnl_curr: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a simple NOI bridge (current - previous by line item).

    Expected columns for both frames:
    - account (str): e.g., "Rent", "Other Income", "Taxes", "Repairs"
    - amount (numeric): positive income, positive expenses

    Returns a DataFrame sorted by absolute impact:
    - account
    - delta
    - direction ("up" if improving NOI, "down" otherwise)
    """
    a = pnl_prev.copy().set_index("account")["amount"]
    b = pnl_curr.copy().set_index("account")["amount"]
    # Align accounts
    all_idx = a.index.union(b.index)
    a = a.reindex(all_idx).fillna(0.0)
    b = b.reindex(all_idx).fillna(0.0)

    delta = b - a
    out = (
        delta.rename("delta")
        .reset_index()
        .sort_values("delta", key=lambda s: s.abs(), ascending=False)
        .reset_index(drop=True)
    )
    # Income up improves NOI; expense up worsens NOI. We don't have account
    # types here, so treat positive delta as "up". Caller can map if needed.
    out["direction"] = out["delta"].apply(lambda x: "up" if x >= 0 else "down")
    return out
