"""Run validated SQLite snapshot analysis on simulated data.

Keep historical exports separate from the published snapshot:
    python analyze.py --as-of 2026-06-30 --output-dir results/2026-06-30
"""
from pathlib import Path
import argparse, json, sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parent
AS_OF='2026-10-20'

def load_data():
 data={n:pd.read_csv(ROOT/'data'/f'{n}.csv') for n in ['vehicles','purchases','sales']}
 for name,df in data.items():
  if df.isna().any().any() or df.stock_id.duplicated().any():raise ValueError(f'{name}: missing values or duplicate IDs')
 if set(data['vehicles'].stock_id)!=set(data['purchases'].stock_id):raise ValueError('Vehicle/purchase keys differ')
 if not set(data['sales'].stock_id)<=set(data['vehicles'].stock_id):raise ValueError('Unknown sold vehicle')
 p=data['purchases'];s=data['sales']
 pd.to_datetime(p.acquired_date,format='%Y-%m-%d',errors='raise')
 pd.to_datetime(s.sold_date,format='%Y-%m-%d',errors='raise')
 if (p[['acquisition_cost_cad','asking_price_cad']]<=0).any().any() or (s.sale_price_cad<=0).any():raise ValueError('Nonpositive price')
 joined=p.merge(s,on='stock_id')
 if (joined.sold_date<joined.acquired_date).any():raise ValueError('Sale before acquisition')
 return data

def snapshot(data,as_of):
 pd.to_datetime(as_of,format='%Y-%m-%d',errors='raise')
 with sqlite3.connect(':memory:') as conn:
  for name,df in data.items():df.to_sql(name,conn,index=False)
  result=pd.read_sql_query((ROOT/'queries.sql').read_text(),conn,params={'as_of':as_of})
  # Exported review list uses a window rank with deterministic tie-breaking.
  result.to_sql('snapshot',conn,index=False)
  priority=pd.read_sql_query('''SELECT stock_id, segment, location, age_days,
  acquisition_cost_cad, asking_price_cad,
  ROW_NUMBER() OVER (ORDER BY age_days DESC, acquisition_cost_cad DESC, stock_id) AS review_rank
  FROM snapshot WHERE is_open=1 AND age_days>90 ORDER BY review_rank''',conn)
 return result,priority

def main(as_of=AS_OF, output_dir=None):
 data=load_data();df,priority=snapshot(data,as_of)
 active=df[df.is_open==1].copy();sold=df[df.is_open==0].copy()
 # Independently reconcile SQL's active population and acquisition cost in pandas.
 p=data['purchases'];s=data['sales']
 expected=p[(p.acquired_date<=as_of)&~p.stock_id.isin(s.loc[s.sold_date<=as_of,'stock_id'])]
 assert set(active.stock_id)==set(expected.stock_id)
 assert active.acquisition_cost_cad.sum()==expected.acquisition_cost_cad.sum()
 summary={'data_type':'SIMULATED; not actual dealership results','as_of':as_of,
 'vehicles_acquired':len(df),'open_vehicles':len(active),'sold_vehicles':len(sold),
 'open_cost_cad':int(active.acquisition_cost_cad.sum()),
 'over_90_units':int((active.age_days>90).sum()),
 'over_90_cost_cad':int(active.loc[active.age_days>90,'acquisition_cost_cad'].sum()),
 'over_90_share_pct':round(float((active.age_days>90).mean()*100),2) if len(active) else None,
 'median_open_age_days':float(active.age_days.median()) if len(active) else None,
 'median_sold_days':float(sold.days_to_sale.median()) if len(sold) else None}
 out=Path(output_dir) if output_dir is not None else ROOT/'results'
 out.mkdir(parents=True,exist_ok=True)
 df.to_csv(out/'snapshot.csv',index=False)
 priority.to_csv(out/'review_queue.csv',index=False)
 active.groupby('age_bucket',sort=False).agg(units=('stock_id','size'),cost_cad=('acquisition_cost_cad','sum')).reindex(['0–30','31–60','61–90','91+'],fill_value=0).to_csv(out/'aging_summary.csv')
 active.groupby('segment').agg(units=('stock_id','size'),median_age_days=('age_days','median'),cost_cad=('acquisition_cost_cad','sum')).to_csv(out/'segment_summary.csv')
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
 return summary
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--as-of',default=AS_OF)
 parser.add_argument('--output-dir',type=Path,help='Export folder (default: results beside this script). Relative paths use the current working directory; existing exports in the selected folder are overwritten.')
 args=parser.parse_args()
 main(args.as_of,args.output_dir)
