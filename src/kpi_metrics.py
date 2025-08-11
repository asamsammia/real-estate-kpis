import pandas as pd


def arrears_aging(ar: pd.DataFrame) -> pd.DataFrame:
    """Aggregate accounts receivable into aging buckets.

    Parameters
    ----------
    ar : pd.DataFrame
        Must contain columns: 'days_past_due' (int) and 'amount' (numeric).
    """
    bins = [0, 30, 60, 90, 120, 9_999]
    labels = ['0-30', '31-60', '61-90', '91-120', '120+']

    ar = ar.copy()
    ar['bucket'] = pd.cut(
        ar['days_past_due'],
        bins=bins,
        labels=labels,
        right=True
    )
    return (
        ar.groupby('bucket', as_index=True)['amount']
          .sum()
          .reset_index()
    )
