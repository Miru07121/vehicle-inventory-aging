# Tableau dashboard extension

This extension uses the existing **synthetic** inventory snapshot, not actual dealership records.

## Build in Tableau Public
1. Run `python analyze.py` at the repository root.
2. Open Tableau Public Desktop and connect to `results/inventory_snapshot.csv` (inspect the output filenames and use the snapshot-level CSV produced by analyze.py).
3. Set the snapshot CSV as an extract.
4. Create KPI cards: count of open stock, acquisition cost of open stock, 91+ day count, 91+ day cost.
5. Create a bar chart of open vehicle count by age bucket; sort 0–30, 31–60, 61–90, 91+.
6. Create stacked bars by location and segment; a stock review table sorted by age descending.
7. Add location and segment filters; ensure all views use open stock for current inventory metrics.
8. Publish to Tableau Public only after verifying the dataset is synthetic. Add the published URL here.

## Quality checks
- Expected open stock at the published 2026-10-20 snapshot: 129.
- Expected 91+ day stock: 34.
- Expected open acquisition cost: CAD 4,176,500.
- Expected 91+ day acquisition cost: CAD 1,113,500.
- Do not sum snapshot metrics across multiple snapshot dates.
- Do not claim actual dealership savings or operational outcomes.

## Dashboard layout
Top: four KPI cards. Middle: aging distribution and inventory acquisition cost by age bucket. Bottom: location/segment breakdown and sortable priority queue.

**Status:** Tableau build specification and calculated-field guide; a published Tableau workbook is not yet included.
