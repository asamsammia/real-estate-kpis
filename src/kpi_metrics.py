"""
KPI computation utilities for a real-estate portfolio.
All functions are pure and pandas-in/pandas-out so they are easy to test.
"""

from __future__ import annotations

import pandas as pd


def rent_roll_health(tenants: pd.DataFrame) -> pd.DataFrame:
    """
    Compute simple rent-roll health metrics by property.
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
    """
    df = ledger.copy()
    bins = [-1, 30, 60, 90, 10_000]
    labels = ["0-30", "31-60", "61-90", "90+"]
    df["bucket"] = pd.cut(df["days_past_due"], bins=bins, labels=labels)
    out = (
        df.groupby("bucket", as_index=False, observed=True)["balance"]
        .sum()
        .rename(columns={"balance": "amount"})
    )
    out = (
        pd.DataFrame({"bucket": labels})
        .merge(out, on="bucket", how="left")
        .fillna({"amount": 0.0})
    )
    return out


def lease_expiries(leases: pd.DataFrame, as_of: str) -> pd.DataFrame:
    """
    Count leases expiring in disjoint windows from `as_of`:
    (0,30], (30,60], (60,90], (90,180] days.
    """
    df = leases.copy()
    df["end_date"] = pd.to_datetime(df["end_date"])
    ref = pd.to_datetime(as_of)

    # days until expiry; keep only future expiries
    df["days_until"] = (df["end_date"] - ref).dt.days
    df = df[df["days_until"] > 0]

    bins = [0, 30, 60, 90, 180]
    labels = ["30d", "60d", "90d", "180d"]
    df["horizon"] = pd.cut(
        df["days_until"],
        bins=bins,
        labels=labels,
        right=True,
        include_lowest=True,
    )

    out = (
        df.groupby("horizon", as_index=False, observed=True)
        .size()
        .rename(columns={"size": "expiring"})
    )
    out = (
        pd.DataFrame({"horizon": labels})
        .merge(out, on="horizon", how="left")
        .fillna({"expiring": 0})
    )
    out["expiring"] = out["expiring"].astype(int)
    return out


def noi_bridge(pnl_prev: pd.DataFrame, pnl_curr: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a simple NOI bridge (current - previous by line item).
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
    out["direction"] = out["delta"].apply(
        lambda x: "up" if x >= 0 else "down"
    )
    return out
