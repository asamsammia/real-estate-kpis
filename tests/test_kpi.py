import pandas as pd
from src.kpi_metrics import arrears_aging


def test_aging_buckets():
    df = pd.DataFrame({
        'days_past_due': [10, 45, 75, 95, 130],
        'amount': [1, 1, 1, 1, 1]
    })
    out = arrears_aging(df)
    assert out['amount'].sum() == 5
