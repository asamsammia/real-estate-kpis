import pandas as pd
from src.kpi_metrics import (
    rent_roll_health,
    arrears_aging,
    lease_expiries,
    noi_bridge,
)


def test_rent_roll_health_basic():
    df = pd.DataFrame(
        {
            "property_id": ["A", "A", "B"],
            "unit_id": ["A-1", "A-2", "B-1"],
            "is_occupied": [1, 0, 1],
            "monthly_rent": [1000, 1200, 900],
        }
    )
    out = rent_roll_health(df)
    assert set(out["property_id"]) == {"A", "B"}
    a_row = out[out["property_id"] == "A"].iloc[0]
    assert abs(a_row["occupancy_rate"] - 0.5) < 1e-9


def test_arrears_aging_buckets():
    df = pd.DataFrame(
        {
            "tenant_id": ["t1", "t2", "t3", "t4"],
            "days_past_due": [10, 45, 70, 200],
            "balance": [100.0, 50.0, 20.0, 10.0],
        }
    )
    out = arrears_aging(df)
    assert list(out["bucket"]) == ["0-30", "31-60", "61-90", "90+"]
    assert out.loc[out["bucket"] == "0-30", "amount"].iloc[0] == 100.0


def test_lease_expiries_counts():
    leases = pd.DataFrame(
        {
            "lease_id": ["L1", "L2", "L3", "L4"],
            "end_date": ["2025-09-01", "2025-10-01", "2026-01-01", "2025-08-20"],
        }
    )
    out = lease_expiries(leases, as_of="2025-08-01")
    # L4 is before as_of; L1 within 30d; L2 within 60d; L3 beyond 180d
    assert out.loc[out["horizon"] == "30d", "expiring"].iloc[0] == 1
    assert out.loc[out["horizon"] == "60d", "expiring"].iloc[0] == 1


def test_noi_bridge_delta():
    prev = pd.DataFrame(
        {"account": ["Rent", "Repairs"], "amount": [1000.0, 100.0]}
    )
    curr = pd.DataFrame(
        {"account": ["Rent", "Repairs"], "amount": [1100.0, 80.0]}
    )
    out = noi_bridge(prev, curr)
    # Rent delta +100, Repairs delta -20
    assert set(out["account"]) == {"Rent", "Repairs"}
    assert out[out["account"] == "Rent"]["delta"].iloc[0] == 100.0
