# Tableau calculated fields

Confirm exact field names in the generated CSV before using these expressions.

**Open vehicle count:** `COUNTD(IF [is_open] = 1 THEN [stock_id] END)`

**Open acquisition cost:** `SUM(IF [is_open] = 1 THEN [acquisition_cost_cad] ELSE 0 END)`

**91+ vehicle count:** `COUNTD(IF [is_open] = 1 AND [age_days] > 90 THEN [stock_id] END)`

**91+ acquisition cost:** `SUM(IF [is_open] = 1 AND [age_days] > 90 THEN [acquisition_cost_cad] ELSE 0 END)`

**Share of aged vehicles:** `[91+ vehicle count] / [Open vehicle count]`

Use snapshot date as a single-value filter. Check output column names against the CSV and rename expressions accordingly. Do not use asking price as acquisition cost.
