"""Generate fictional dealership records, independent of any employer."""
from pathlib import Path
from datetime import date, timedelta
import csv, random
ROOT=Path(__file__).resolve().parent
AS_OF=date(2026,10,20)
def main():
 r=random.Random(213)
 vehicles=[]; purchases=[]; sales=[]
 for i in range(1,401):
  stock=f'SIM-{i:04d}'
  segment=r.choice(['Sedan','SUV','Truck','Hatchback'])
  cost=r.randrange(15000,55001,500)
  acquired=AS_OF-timedelta(days=r.randint(0,292))
  duration=r.randint(8,180)
  sold=acquired+timedelta(days=duration)
  vehicles.append([stock,segment,r.randint(2018,2025),r.choice(['North lot','South lot','Main lot'])])
  purchases.append([stock,acquired.isoformat(),cost,round(cost*r.uniform(1.08,1.22))])
  if sold<=AS_OF:sales.append([stock,sold.isoformat(),round(cost*r.uniform(.97,1.17))])
 for name,cols,rows in [
 ('vehicles',['stock_id','segment','model_year','location'],vehicles),
 ('purchases',['stock_id','acquired_date','acquisition_cost_cad','asking_price_cad'],purchases),
 ('sales',['stock_id','sold_date','sale_price_cad'],sales)]:
  with (ROOT/'data'/f'{name}.csv').open('w',newline='') as f:
   w=csv.writer(f);w.writerow(cols);w.writerows(rows)
if __name__=='__main__':main()
