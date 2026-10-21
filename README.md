# Vehicle Inventory & Aging

An operations analytics portfolio project using Python, SQLite SQL, and a local Streamlit dashboard to identify aging inventory and prioritize stock reviews.

**All 400 vehicle records are simulated. These are not BMW records or actual dealership results.** Prices are CAD. The reproducible snapshot is October 20, 2026.

## Findings from the simulation

| Metric | Result |
|---|---:|
| Open vehicles | 129 |
| Acquisition cost of open stock | $4,176,500 |
| Vehicles older than 90 days | 34 (26.36%) |
| Acquisition cost of stock older than 90 days | $1,113,500 |
| Median age of open stock | 55 days |
| Completed sales | 271 |
| Median days to sale among completed sales | 70 days |

The example decision is to review the 34 oldest vehicles for pricing, merchandising, condition, and transfer opportunities. The analysis does not establish that discounting them would improve profit, or estimate realized savings.

## Run locally

Requires Python 3.11 or later. From this folder:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python analyze.py
python -m unittest discover -s tests -v
streamlit run dashboard.py
```

The dashboard includes snapshot date, segment and location filters; inventory and cost metrics; an aging chart; and a downloadable review queue. This project does not include a Power BI file.

To regenerate the same synthetic inputs: `python generate_data.py`. To inspect a historical snapshot: `python analyze.py --as-of 2026-06-30`. This overwrites the output CSVs; run `python analyze.py` to restore the published snapshot.

## Files and data model

| File | Purpose |
|---|---|
| `data/vehicles.csv` | One row per fictional vehicle: stock ID, segment, model year, location |
| `data/purchases.csv` | One acquisition per vehicle: acquisition date, cost and asking price |
| `data/sales.csv` | One completed sale per sold vehicle: sale date and sale price |
| `generate_data.py` | Deterministic synthetic generator, random seed 213 |
| `queries.sql` | Snapshot joins, date arithmetic, and aging classification |
| `analyze.py` | Validation, SQLite execution, window-ranked queue and pandas reconciliation |
| `dashboard.py` | Interactive Streamlit application |
| `results/` | Snapshot, aging and segment summaries, review queue and JSON metrics |
| `tests/` | Boundary and historical-snapshot checks |

`stock_id` joins all three tables. Dates use YYYY-MM-DD. All `*_cad` fields are positive Canadian-dollar amounts. `is_open` is 1 for stock acquired by the snapshot and not sold by that date, otherwise 0. Sales on the snapshot date count as sold. Future acquisitions and future sale details are excluded from historical snapshots.

Age is elapsed calendar days from acquisition to snapshot. Open-stock buckets are 0–30, 31–60, 61–90, and 91+. Completed-sale duration is sale date minus acquisition date. Open-stock age statistics exclude sold vehicles. The review queue uses SQL `ROW_NUMBER`, sorting by descending age, then acquisition cost, then stock ID.

## A one-hour walkthrough

1. **0–10 minutes:** Read the data dictionary and inspect the three CSV tables.
2. **10–25 minutes:** Run the SQL snapshot; explain the joins and sale-date boundary.
3. **25–40 minutes:** Compare aging buckets and cost concentration in the dashboard.
4. **40–50 minutes:** Inspect the review queue and test historical snapshots.
5. **50–60 minutes:** Write a manager recommendation with limitations and next data needs.

## Limits and next steps

Synthetic data demonstrates an analytical workflow, not real market patterns. The 90-day review threshold is illustrative. Acquisition cost excludes reconditioning, financing, tax and other carrying costs; it is not market value or a write-down estimate. Completed-sale duration omits unsold vehicles, so it is not an unbiased inventory-wide time-to-sale estimate. Locations and asking prices are static, not historically versioned. Snapshot dates should stay within the simulated observation period, January 1–October 20, 2026.

With authorized operational records, add condition, price changes, leads, carrying costs, transfers and gross margin. Evaluate actions prospectively before claiming inventory reductions or financial savings.

## Portfolio description

Built a Python and SQL inventory-aging analysis with an interactive Streamlit dashboard; validated inventory snapshots, segmented stock into aging buckets, and generated a prioritized review queue for a simulated 400-vehicle dataset.
