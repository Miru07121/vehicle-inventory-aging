import unittest
from datetime import date, timedelta
import pandas as pd
from analyze import snapshot

class SnapshotTests(unittest.TestCase):
 def setUp(self):
  ages=[0,30,31,60,61,90,91,-1]
  self.ids=[str(i) for i in range(len(ages))]
  self.data={
   'vehicles':pd.DataFrame({'stock_id':self.ids,'segment':'SUV','location':'Main lot','model_year':2024}),
   'purchases':pd.DataFrame({'stock_id':self.ids,'acquired_date':[(date(2026,10,20)-timedelta(days=a)).isoformat() for a in ages],'acquisition_cost_cad':20000,'asking_price_cad':24000}),
   'sales':pd.DataFrame(columns=['stock_id','sold_date','sale_price_cad'])}
 def test_bucket_boundaries_and_future_acquisition(self):
  df,q=snapshot(self.data,'2026-10-20')
  self.assertEqual(df.age_bucket.tolist(),['0–30','0–30','31–60','31–60','61–90','61–90','91+'])
  self.assertEqual(q.stock_id.tolist(),['6'])
 def test_sale_on_snapshot_and_future_sale(self):
  self.data['sales']=pd.DataFrame({'stock_id':['5','6'],'sold_date':['2026-10-20','2026-10-21'],'sale_price_cad':[24000,25000]})
  df,q=snapshot(self.data,'2026-10-20');df=df.set_index('stock_id')
  self.assertEqual(df.loc['5','is_open'],0)
  self.assertEqual(df.loc['5','days_to_sale'],90)
  self.assertEqual(df.loc['6','is_open'],1)
  self.assertTrue(pd.isna(df.loc['6','sale_price_cad']))
  self.assertEqual(q.stock_id.tolist(),['6'])
 def test_empty_snapshot(self):
  df,q=snapshot(self.data,'2025-01-01')
  self.assertTrue(df.empty and q.empty)

if __name__=='__main__':unittest.main()
