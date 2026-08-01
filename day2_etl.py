import pandas as pd
from sqlalchemy import create_engine
import os

RAW_DIR = "data/raw"
PROC_DIR = "data/processed"
DB_PATH = "bluestock_mf.db"
os.makedirs(PROC_DIR, exist_ok=True)

print("Starting ETL Process...\n")

def print_row_verification(name, raw_df, proc_df):
    print(f"[{name}] Raw Rows: {len(raw_df)} | Cleaned Rows: {len(proc_df)}")
    if len(raw_df) != len(proc_df):
        print(f" -> Removed {len(raw_df) - len(proc_df)} anomalous rows.")

# 1. Clean nav_history.csv
print("Cleaning nav_history...")
raw_nav = pd.read_csv(f"{RAW_DIR}/02_nav_history.csv")
nav_df = raw_nav.copy()
nav_df['date'] = pd.to_datetime(nav_df['date'], format='%d-%m-%Y', errors='coerce')
nav_df = nav_df.sort_values(by=['amfi_code', 'date'])
nav_df = nav_df.drop_duplicates(subset=['amfi_code', 'date'])
nav_df = nav_df[nav_df['nav'] > 0]
nav_df['nav'] = nav_df.groupby('amfi_code')['nav'].ffill()
nav_df.to_csv(f"{PROC_DIR}/02_nav_history.csv", index=False)
print_row_verification("02_nav_history.csv", raw_nav, nav_df)

# 2. Clean investor_transactions.csv
print("Cleaning investor_transactions...")
raw_txn = pd.read_csv(f"{RAW_DIR}/08_transactions.csv")
txn_df = raw_txn.copy()
txn_map = {'sip': 'SIP', 'LUMP': 'Lumpsum', 'Red': 'Redemption'}
txn_df['transaction_type'] = txn_df['transaction_type'].replace(txn_map)
txn_df = txn_df[txn_df['amount'] > 0]
txn_df['transaction_date'] = pd.to_datetime(txn_df['transaction_date'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
valid_kyc = ['Verified', 'Pending', 'Rejected']
txn_df['kyc_status'] = txn_df['kyc_status'].apply(lambda x: x if x in valid_kyc else 'Unknown')
txn_df.to_csv(f"{PROC_DIR}/08_transactions.csv", index=False)
print_row_verification("08_transactions.csv", raw_txn, txn_df)

# 3. Clean scheme_performance.csv
print("Cleaning scheme_performance...")
raw_perf = pd.read_csv(f"{RAW_DIR}/07_scheme_performance.csv")
perf_df = raw_perf.copy()
for col in ['return_1yr', 'return_3yr', 'return_5yr']:
    perf_df[col] = pd.to_numeric(perf_df[col], errors='coerce')
perf_df['expense_ratio'] = pd.to_numeric(perf_df['expense_ratio'], errors='coerce')
perf_df = perf_df[(perf_df['expense_ratio'] >= 0.1) & (perf_df['expense_ratio'] <= 2.5)]
perf_df.to_csv(f"{PROC_DIR}/07_scheme_performance.csv", index=False)
print_row_verification("07_scheme_performance.csv", raw_perf, perf_df)

# Copy the rest
files_to_copy = [
    '01_fund_master.csv', '03_aum_by_fund_house.csv', '04_monthly_sip.csv',
    '05_category_inflows.csv', '06_folio_count.csv', '09_holdings.csv', '10_benchmark.csv'
]
dfs = {'02_nav_history.csv': nav_df, '08_transactions.csv': txn_df, '07_scheme_performance.csv': perf_df}

print("\nProcessing remaining files...")
for f in files_to_copy:
    df = pd.read_csv(f"{RAW_DIR}/{f}")
    df.to_csv(f"{PROC_DIR}/{f}", index=False)
    dfs[f] = df
    print_row_verification(f, df, df)

# Generate dim_date table
print("\nGenerating dim_date dimension...")
date_rng = pd.date_range(start='2020-01-01', end='2024-12-31', freq='D')
dim_date = pd.DataFrame({
    'date_id': date_rng.strftime('%Y-%m-%d'),
    'year': date_rng.year,
    'month': date_rng.month,
    'day': date_rng.day,
    'day_of_week': date_rng.day_name(),
    'is_weekend': date_rng.dayofweek >= 5
})

# LOAD TO SQLITE via SQLAlchemy
print(f"\nLoading data to SQLite database {DB_PATH} using SQLAlchemy...")
engine = create_engine(f'sqlite:///{DB_PATH}')

dim_date.to_sql('dim_date', engine, if_exists='replace', index=False)
dfs['01_fund_master.csv'].to_sql('dim_fund', engine, if_exists='replace', index=False)
dfs['02_nav_history.csv'].to_sql('fact_nav', engine, if_exists='replace', index=False)
dfs['03_aum_by_fund_house.csv'].to_sql('fact_aum', engine, if_exists='replace', index=False)
dfs['04_monthly_sip.csv'].to_sql('monthly_sip', engine, if_exists='replace', index=False)
dfs['05_category_inflows.csv'].to_sql('category_inflows', engine, if_exists='replace', index=False)
dfs['06_folio_count.csv'].to_sql('folio_count', engine, if_exists='replace', index=False)
dfs['07_scheme_performance.csv'].to_sql('fact_performance', engine, if_exists='replace', index=False)
dfs['08_transactions.csv'].to_sql('fact_transactions', engine, if_exists='replace', index=False)
dfs['09_holdings.csv'].to_sql('holdings', engine, if_exists='replace', index=False)
dfs['10_benchmark.csv'].to_sql('benchmark', engine, if_exists='replace', index=False)

print("ETL complete! Data loaded successfully with explicit row verifications.")
