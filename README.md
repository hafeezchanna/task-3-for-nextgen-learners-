# Week 3 — SQL + Program Performance Dashboard

## Files
- `generate_data.py` – builds mock `nextgen.db` (skip if your mentor gave you the real DB)
- `Week3_SQL_Queries.ipynb` – Part A: 5 required queries + 3 bonus, each commented
- `dashboard.py` – Part B: Streamlit dashboard (funnel, completion rate, avg score, top 10, domain filter)

## Run
```bash
pip install -r requirements.txt
python generate_data.py
jupyter notebook Week3_SQL_Queries.ipynb
streamlit run dashboard.py   # opens http://localhost:8501
```

## Demo checklist
1. Default view (All domains)  2. Pick a domain – metrics/charts/leaderboard change  3. Leaderboard visible
