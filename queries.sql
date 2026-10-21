-- Snapshot date is bound by Python as :as_of. Sales on the date are already sold.
WITH eligible AS (
 SELECT v.*, p.acquired_date, p.acquisition_cost_cad, p.asking_price_cad,
        s.sold_date, s.sale_price_cad,
        CASE WHEN s.sold_date IS NULL OR s.sold_date > :as_of THEN 1 ELSE 0 END AS is_open,
        CAST(julianday(:as_of)-julianday(p.acquired_date) AS INTEGER) AS age_days,
        CAST(julianday(s.sold_date)-julianday(p.acquired_date) AS INTEGER) AS days_to_sale
 FROM vehicles v
 JOIN purchases p USING(stock_id)
 LEFT JOIN sales s ON s.stock_id=v.stock_id AND s.sold_date <= :as_of
 WHERE p.acquired_date <= :as_of
), classified AS (
 SELECT *, CASE WHEN is_open=0 THEN 'Sold'
                WHEN age_days<=30 THEN '0–30'
                WHEN age_days<=60 THEN '31–60'
                WHEN age_days<=90 THEN '61–90'
                ELSE '91+' END AS age_bucket
 FROM eligible
)
SELECT * FROM classified ORDER BY stock_id;
