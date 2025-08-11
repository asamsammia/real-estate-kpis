import pandas as pd

def arrears_aging(ar: pd.DataFrame) -> pd.DataFrame:
    bins = [0,30,60,90,120,9999]
    labels = ['0-30','31-60','61-90','91-120','120+']
    ar = ar.copy()
    ar['bucket'] = pd.cut(ar['days_past_due'], bins=bins, labels=labels, right=True)
    return ar.groupby('bucket', as_index=False)['amount'].sum()