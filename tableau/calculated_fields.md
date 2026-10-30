# Tableau calculated fields

Use these expressions with `snapshot.csv`, at one row per acquired vehicle. Keep the field names below when referencing one calculated field from another.

## Inventory KPIs

**Open vehicle count**
```text
COUNTD(IF [is_open] = 1 THEN [stock_id] END)
```

**Open acquisition cost**
```text
SUM(IF [is_open] = 1 THEN [acquisition_cost_cad] ELSE 0 END)
```

**91+ vehicle count**
```text
COUNTD(IF [is_open] = 1 AND [age_days] > 90 THEN [stock_id] END)
```

**91+ acquisition cost**
```text
SUM(IF [is_open] = 1 AND [age_days] > 90 THEN [acquisition_cost_cad] ELSE 0 END)
```

**Share of aged vehicles**
```text
IF [Open vehicle count] > 0 THEN
    [91+ vehicle count] / [Open vehicle count]
END
```

Format this ratio as a percentage with two decimals. Do not multiply by 100 as well. An inventory with no open vehicles returns NULL (display as “—”), because the share is undefined.

**Median open age**
```text
MEDIAN(IF [is_open] = 1 THEN [age_days] END)
```

## Completed sales

**Completed sale count**
```text
COUNTD(IF [is_open] = 0 THEN [stock_id] END)
```

**Median completed-sale days**
```text
MEDIAN(IF [is_open] = 0 THEN [days_to_sale] END)
```

Do not apply an `is_open = 1` worksheet or data-source filter to completed-sales cards. The conditional calculations keep open and sold populations separate. Sales on the snapshot date count as completed; future sales are excluded by the Python/SQL export.

## Review and reconciliation

- The review threshold is strictly greater than 90 days: age 90 is excluded and age 91 is included.
- Location and segment filters should apply to all relevant worksheets so the share uses the same filtered population in both numerator and denominator.
- Use acquisition cost for cost exposure; asking price is a different measure.
- For the default export, check 129 open vehicles, 34 aged vehicles, a 26.36% aged share, median open age of 55 days, and median completed-sale duration of 70 days.
- For empty populations, count measures should be zero and median/share measures should be blank. A completely empty source may render no marks; do not label an undefined median or share as zero.
- There is no snapshot-date column in the current CSV. Use one export at a time and label the date from its adjacent `summary.json`.
