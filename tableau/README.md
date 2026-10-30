# Tableau dashboard extension

This extension uses **simulated** inventory data, not actual dealership records.

## Prepare the data

From the repository root, run:

```bash
python analyze.py
```

Connect Tableau to **`results/snapshot.csv`**. This file contains one row per vehicle acquired by the selected date, including both open and sold vehicles. Do not join the aggregated aging or segment summaries back onto these rows: that can duplicate totals.

For a historical view that preserves the published results:

```bash
python analyze.py --as-of 2026-06-30 --output-dir results/2026-06-30
```

Connect to `results/2026-06-30/snapshot.csv` for that view. Each export represents **one snapshot date**. The CSV has no snapshot-date column; read `as_of` from the adjacent `summary.json` and put it in the dashboard title. To change dates, generate another export and replace or refresh the data source. Do not union snapshots without adding a date column and restricting each view to one date.

## Build the dashboard

1. Check field types: `stock_id`, `segment`, `location`, and `age_bucket` are text; `is_open` and `age_days` are whole numbers; CAD amounts are numeric; `acquired_date` and `sold_date` are dates. Blank sale fields are expected for open stock.
2. Create the fields in [calculated_fields.md](calculated_fields.md).
3. Add cards for open vehicles, open acquisition cost, 91+ vehicles, 91+ acquisition cost, and share of aged vehicles.
4. Build an open-stock aging chart: filter the worksheet to `is_open = 1`, place `age_bucket` on Columns and `COUNTD(stock_id)` on Rows, then manually order 0–30, 31–60, 61–90, 91+.
5. Build location and segment charts using the open-stock measures. Add location and segment filters and apply them to every relevant worksheet using this data source.
6. Build a review table with `stock_id`, `segment`, `location`, `age_days`, acquisition cost, and asking price. Filter to `is_open = 1` and `age_days > 90`. Order by age descending, acquisition cost descending, then stock ID ascending. The exported `review_queue.csv` provides the reference order.
7. If adding completed-sales cards, use their conditional measures without an open-stock filter on those worksheets.
8. Title the dashboard “Simulated Vehicle Inventory — as of 2026-10-20” for the default export. Format amounts as CAD and the aged share as a percentage.
9. Before publishing to Tableau Public, confirm that every connected file is simulated and contains no private dealership data.

## Reconcile before publishing

With location and segment filters cleared, the default snapshot must show:

| Metric | Expected |
|---|---:|
| All acquired vehicles | 400 |
| Open vehicles | 129 |
| Completed sales | 271 |
| Open acquisition cost | CAD 4,176,500 |
| 91+ vehicles | 34 |
| 91+ acquisition cost | CAD 1,113,500 |
| Share of aged open vehicles | 26.36% |
| Median open age | 55 days |
| Median completed-sale duration | 70 days |

For historical exports, reconcile against their own `summary.json`; the default values above will not apply. Check that filters affect every intended card and chart and that sold stock never appears in the review queue.

Acquisition cost is not market value or estimated savings. Completed-sale duration excludes unsold stock and is not an unbiased estimate of time to sale for all vehicles.

**Status:** Build instructions and formulas only; no Tableau workbook or published dashboard is included.
