
"""2024 GFZ Kp + Aurorasaurus daily reported-sighting comparison.
Run from project root: python src/fetch_and_process.py
No API key needed. Requires requests, pandas, pyarrow, matplotlib.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RAW, PROCESSED, FIGURES = (ROOT/'data'/'raw', ROOT/'data'/'processed', ROOT/'figures')
for folder in (RAW, PROCESSED, FIGURES): folder.mkdir(parents=True, exist_ok=True)
YEAR = 2024
START, END = f'{YEAR}-01-01T00:00:00Z', f'{YEAR}-12-31T23:59:59Z'
GFZ_URL = 'https://kp.gfz.de/app/json/'
AURORA_FILE = RAW/'web_observations_2014-08-01_to_2025-08-02_cleaned.csv'
ZENODO_FILE_URL = 'https://zenodo.org/records/16783265/files/web_observations_2014-08-01_to_2025-08-02_cleaned.csv?download=1'

def save_parquet(frame, filename, source):
    table = pa.Table.from_pandas(frame, preserve_index=False)
    meta = dict(table.schema.metadata or {})
    meta.update({b'source':source.encode(), b'retrieved_utc':datetime.now(timezone.utc).isoformat().encode()})
    pq.write_table(table.replace_schema_metadata(meta), PROCESSED/filename)

def get_kp():
    print('Downloading GFZ Kp 2024 (no API key)...')
    resp = requests.get(GFZ_URL, params={'start':START,'end':END,'index':'Kp'}, timeout=120)
    resp.raise_for_status()
    payload=resp.json()
    if not isinstance(payload,dict) or not all(k in payload for k in ('datetime','Kp','status')):
        raise ValueError('GFZ API response missing expected datetime, Kp, status fields')
    if len(set(map(len,(payload['datetime'],payload['Kp'],payload['status']))))!=1:
        raise ValueError('GFZ API returned mismatched array lengths')
    (RAW/'kp_2024.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    df=pd.DataFrame({'datetime':pd.to_datetime(payload['datetime'],utc=True,errors='coerce'),
                     'kp':pd.to_numeric(payload['Kp'],errors='coerce'),'status':payload['status']})
    if df[['datetime','kp']].isna().any().any():raise ValueError('GFZ Kp contains missing/unparseable records')
    df=df.sort_values('datetime').reset_index(drop=True)
    if df['datetime'].duplicated().any() or not df['kp'].between(0,9).all():
        raise ValueError('Duplicate GFZ timestamps or Kp outside [0,9]')
    expected=pd.date_range('2024-01-01', '2024-12-31 21:00',freq='3h',tz='UTC')
    if len(df)!=len(expected) or not df['datetime'].equals(pd.Series(expected,name='datetime')):
        raise ValueError(f'Unexpected Kp coverage: {len(df)} records, expected {len(expected)}. Inspect raw JSON.')
    df['date']=df['datetime'].dt.date
    df['hour']=df['datetime'].dt.hour
    df['storm_interval']=df['kp']>=5
    df['month']=df['datetime'].dt.strftime('%Y-%m')
    df['activity_category']=pd.cut(df['kp'],[-0.01,2,3,4,5,9.01],right=False,
      labels=['Quiet','Unsettled','Active','Minor disturbance','Storm-level']).astype(str)
    df.to_csv(PROCESSED/'kp_2024.csv',index=False)
    save_parquet(df,'kp_2024.parquet','GFZ Helmholtz Centre for Geosciences; https://kp.gfz.de/en/data; CC BY 4.0')
    daily=df.groupby('date').agg(kp_daily_max=('kp','max'),kp_daily_mean=('kp','mean'),
        storm_intervals=('storm_interval','sum')).reset_index()
    daily['date']=pd.to_datetime(daily['date'])
    daily['month']=daily['date'].dt.strftime('%Y-%m')
    monthly=df.groupby('month').agg(kp_monthly_mean=('kp','mean'),kp_monthly_max=('kp','max'),
        storm_intervals=('storm_interval','sum')).reset_index()
    return df,daily,monthly

def get_aurora():
    if not AURORA_FILE.exists():
        print('Downloading Aurorasaurus cleaned CSV from Zenodo...')
        try:
            with requests.get(ZENODO_FILE_URL,stream=True,timeout=120) as r:
                r.raise_for_status()
                with AURORA_FILE.open('wb') as out:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk:out.write(chunk)
        except Exception as exc:
            AURORA_FILE.unlink(missing_ok=True)
            raise RuntimeError('Aurorasaurus download failed. Download the CLEANED CSV manually from '
                               'https://zenodo.org/records/16783265 and place it at data/raw/'
                               +AURORA_FILE.name) from exc
    aur=pd.read_csv(AURORA_FILE,low_memory=False)
    (PROCESSED/'aurorasaurus_column_names.txt').write_text('\n'.join(aur.columns),encoding='utf-8')
    # The published cleaned dataset describes time_start as observation start timestamp.
    timecol=next((c for c in aur.columns if c.lower()=='time_start'),None)
    if timecol is None:
        raise ValueError('Cannot locate time_start. Inspect data/processed/aurorasaurus_column_names.txt')
    aur['observation_utc']=pd.to_datetime(aur[timecol],utc=True,errors='coerce')
    aur=aur[(aur['observation_utc']>=pd.Timestamp('2024-01-01',tz='UTC')) &
            (aur['observation_utc']<pd.Timestamp('2025-01-01',tz='UTC'))].copy()
    aur['date']=aur['observation_utc'].dt.date
    aur['month']=aur['observation_utc'].dt.strftime('%Y-%m')
    # Each row is a cleaned submitted report, NOT an independently verified aurora occurrence.
    aur['report_count']=1
    aur.to_csv(PROCESSED/'aurora_reports_2024.csv',index=False)
    daily=aur.groupby('date').size().rename('aurora_report_count').reset_index()
    daily['date']=pd.to_datetime(daily['date'])
    return aur,daily

def main():
    kp,daily,monthly=get_kp()
    aur,aur_daily=get_aurora()
    merged=daily.merge(aur_daily,on='date',how='left')
    merged['aurora_report_count']=merged['aurora_report_count'].fillna(0).astype(int)
    merged['month']=merged['date'].dt.strftime('%Y-%m')
    merged['storm_day']=merged['kp_daily_max']>=5
    merged.to_csv(PROCESSED/'kp_aurora_daily_2024.csv',index=False)
    save_parquet(merged,'kp_aurora_daily_2024.parquet','GFZ Kp + Aurorasaurus cleaned citizen reports, Zenodo 10.5281/zenodo.16783265')
    aur_month=merged.groupby('month')['aurora_report_count'].sum().reset_index()
    monthly=monthly.merge(aur_month,on='month',how='left')
    monthly.to_csv(PROCESSED/'kp_aurora_monthly_2024.csv',index=False)
    pearson=merged['kp_daily_max'].corr(merged['aurora_report_count'],method='pearson')
    spearman=merged['kp_daily_max'].corr(merged['aurora_report_count'],method='spearman')
    summary={'year':2024,'kp_intervals':len(kp),'kp_days':len(daily),
        'kp_mean':round(float(kp.kp.mean()),3),'kp_max':float(kp.kp.max()),
        'storm_intervals':int(kp.storm_interval.sum()),'aurora_report_rows_2024':len(aur),
        'days_with_reports':int((merged.aurora_report_count>0).sum()),
        'daily_pearson_kp_max_vs_report_count':None if pd.isna(pearson) else round(float(pearson),4),
        'daily_spearman_kp_max_vs_report_count':None if pd.isna(spearman) else round(float(spearman),4),
        'caution':'Report count is not a count of all auroras; reporting depends on observer coverage, weather, and daylight.'}
    (PROCESSED/'kp_summary_2024.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    fig,ax=plt.subplots(figsize=(12,4))
    ax.plot(merged['date'],merged['kp_daily_max'],linewidth=0.9)
    ax.axhline(5,linestyle='--',linewidth=1,label='Storm threshold (Kp=5)')
    ax.set(ylabel='Daily maximum Kp',title='Geomagnetic activity in 2024 (GFZ)')
    ax.legend();fig.autofmt_xdate();fig.tight_layout();fig.savefig(FIGURES/'kp_daily_max_2024.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    ax.scatter(merged['kp_daily_max'],merged['aurora_report_count'],alpha=0.45,s=16)
    ax.set(xlabel='Daily maximum Kp',ylabel='Aurorasaurus report count',
           title='2024 daily Kp vs citizen-reported aurora sightings')
    fig.tight_layout();fig.savefig(FIGURES/'kp_vs_aurora_2024.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,4))
    ax.bar(monthly['month'],monthly['aurora_report_count'])
    ax.set(ylabel='Aurorasaurus reports',title='Monthly reported aurora sightings, 2024')
    ax.tick_params(axis='x',rotation=45);fig.tight_layout();fig.savefig(FIGURES/'aurora_reports_monthly_2024.png',dpi=180);plt.close(fig)
    print('SUCCESS: 2024 GFZ and Aurorasaurus datasets processed.')
    print(json.dumps(summary,indent=2))
    print('Import kp_2024.parquet, kp_aurora_daily_2024.csv, and kp_aurora_monthly_2024.csv into Power BI.')

if __name__=='__main__':main()
