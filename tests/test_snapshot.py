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

 def test_review_queue_ties_use_cost_then_stock_id(self):
  p=self.data['purchases']
  p.loc[p.stock_id.isin(['3','4','5','6']),'acquired_date']='2026-07-01'
  p.loc[p.stock_id=='4','acquisition_cost_cad']=30000
  p.loc[p.stock_id=='6','acquisition_cost_cad']=30000
  _,queue=snapshot(self.data,'2026-10-20')
  self.assertEqual(queue.stock_id.tolist(),['4','6','3','5'])
  self.assertEqual(queue.review_rank.tolist(),[1,2,3,4])

 def test_sold_aged_stock_is_excluded_from_review(self):
  self.data['sales']=pd.DataFrame({'stock_id':['6'],'sold_date':['2026-10-19'],'sale_price_cad':[24000]})
  df,queue=snapshot(self.data,'2026-10-20')
  sold=df.set_index('stock_id').loc['6']
  self.assertEqual(sold.age_bucket,'Sold')
  self.assertEqual(sold.days_to_sale,90)
  self.assertTrue(queue.empty)

 def test_future_sale_details_do_not_leak(self):
  baseline,_=snapshot(self.data,'2026-10-20')
  self.data['sales']=pd.DataFrame({'stock_id':['6'],'sold_date':['2026-10-21'],'sale_price_cad':[25000]})
  actual,_=snapshot(self.data,'2026-10-20')
  for column in ['sold_date','sale_price_cad','days_to_sale']:
   self.assertTrue(pd.isna(actual.set_index('stock_id').loc['6',column]))
  pd.testing.assert_frame_equal(
   baseline.drop(columns=['sold_date','sale_price_cad','days_to_sale']),
   actual.drop(columns=['sold_date','sale_price_cad','days_to_sale']))

 def test_published_snapshot_reconciles(self):
  from analyze import load_data
  df,queue=snapshot(load_data(),'2026-10-20')
  active=df[df.is_open==1]
  self.assertEqual(len(df),400)
  self.assertEqual(len(active),129)
  self.assertEqual(active.acquisition_cost_cad.sum(),4176500)
  self.assertEqual(len(queue),34)
  self.assertEqual(queue.acquisition_cost_cad.sum(),1113500)
  self.assertEqual(set(queue.stock_id),set(active.loc[active.age_days>90,'stock_id']))

if __name__=='__main__':unittest.main()
