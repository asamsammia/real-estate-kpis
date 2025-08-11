# Real Estate KPI Dashboard

Portfolio-level KPIs: rent roll health, arrears aging, lease expiries, NOI bridge.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

## Structure
- `src/kpi_metrics.py` – compute KPIs from tenant/lease tables
- `notebooks/dashboard_story.ipynb` – outline and visuals
- `powerbi/` and `tableau/` – templates/placeholders

## Sample usage
```python
import pandas as pd
from src.kpi_metrics import rent_roll_health, arrears_aging, lease_expiries, noi_bridge

tenants = pd.read_csv('data/sample_tenants.csv')
ledger = pd.read_csv('data/sample_ledger.csv')
leases = pd.read_csv('data/sample_leases.csv')

print(rent_roll_health(tenants))
print(arrears_aging(ledger))
print(lease_expiries(leases, as_of='2025-08-01'))
```
