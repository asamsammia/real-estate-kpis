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
