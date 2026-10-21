"""Local dashboard. Start with: streamlit run dashboard.py"""
import streamlit as st
import pandas as pd
from datetime import date
from analyze import load_data,snapshot
st.set_page_config(page_title='Vehicle Inventory & Aging',layout='wide')
st.title('Vehicle Inventory & Aging')
st.warning('Simulated dealership data • Portfolio demonstration • Not BMW records')
st.caption('Review aging stock and acquisition cost exposure. Amounts are CAD.')
as_of=st.sidebar.date_input('Snapshot date',date(2026,10,20),min_value=date(2026,1,1),max_value=date(2026,10,20))
df,queue=snapshot(load_data(),as_of.isoformat())
segments=st.sidebar.multiselect('Segments',sorted(df.segment.unique()),default=sorted(df.segment.unique()))
locations=st.sidebar.multiselect('Locations',sorted(df.location.unique()),default=sorted(df.location.unique()))
df=df[df.segment.isin(segments)&df.location.isin(locations)]
active=df[df.is_open==1];sold=df[df.is_open==0]
a,b,c,d=st.columns(4)
a.metric('Open vehicles',len(active));b.metric('Acquisition cost',f'${active.acquisition_cost_cad.sum():,.0f}')
c.metric('Older than 90 days',int((active.age_days>90).sum()))
d.metric('Median open age',f'{active.age_days.median():.0f} days' if len(active) else '—')
st.subheader('Age distribution of open stock')
counts=active.groupby('age_bucket').size().reindex(['0–30','31–60','61–90','91+'],fill_value=0)
st.bar_chart(counts,x_label='Age bucket in days',y_label='Vehicles')
st.subheader('Review queue • oldest first')
review=queue[queue.stock_id.isin(active.stock_id)].drop(columns='review_rank').reset_index(drop=True)
review.insert(0,'filtered_rank',range(1,len(review)+1))
st.dataframe(review,hide_index=True,use_container_width=True)
st.download_button('Download filtered review queue',review.to_csv(index=False),'review_queue.csv','text/csv')
st.subheader('Completed sales')
st.write(f'{len(sold)} vehicles sold by the selected date. Median days to sale: '+(f'{sold.days_to_sale.median():.0f}' if len(sold) else 'not available'))
st.caption('Completed sales exclude unsold vehicles and can bias time-to-sale comparisons. Acquisition cost is not market value. The 90-day threshold is an illustrative policy, not an industry benchmark. Filters apply to all metrics.')
