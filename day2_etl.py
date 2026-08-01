import pandas as pd
import sqlite3
import os

RAW_DIR = "data/raw"
PROC_DIR = "data/processed"
DB_PATH = "bluestock_mf.db"
os.makedirs(PROC_DIR, exist_ok=True)

print("Starting ETL Process...")

# 1. Clean nav_history.csv
print("Cleaning nav_history...")
nav_df = pd.read_csv(f"{RAW_DIR}/02_nav_history.csv")
nav_df['date'] = pd.to_datetime(nav_df['date'], format='%d-%m-%Y', errors='coerce')
nav_df = nav_df.sort_values(by=['amfi_code', 'date'])
# Remove duplicates
nav_df = nav_df.drop_duplicates(subset=['amfi_code', 'date'])
# Validate NAV > 0
nav_df = nav_df[nav_df['nav'] > 0]
# Forward fill missing dates (Resampling per amfi_code to daily frequency is ideal, but ffill on sort is basic)
nav_df['nav'] = nav_df.groupby('amfi_code')['nav'].ffill()
nav_df.to_csv(f"{PROC_DIR}/02_nav_history.csv", index=False)

# 2. Clean investor_transactions.csv
print("Cleaning investor_transactions...")
txn_df = pd.read_csv(f"{RAW_DIR}/08_transactions.csv")
# Standardise transaction_type
txn_map = {'sip': 'SIP', 'LUMP': 'Lumpsum', 'Red': 'Redemption'}
txn_df['transaction_type'] = txn_df['transaction_type'].replace(txn_map)
# Validate amount > 0
txn_df = txn_df[txn_df['amount'] > 0]
# Fix date formats
txn_df['transaction_date'] = pd.to_datetime(txn_df['transaction_date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
# Check KYC status
valid_kyc = ['Verified', 'Pending', 'Rejected']
txn_df['kyc_status'] = txn_df['kyc_status'].apply(lambda x: x if x in valid_kyc else 'Unknown')
txn_df.to_csv(f"{PROC_DIR}/08_transactions.csv", index=False)

# 3. Clean scheme_performance.csv
print("Cleaning scheme_performance...")
perf_df = pd.read_csv(f"{RAW_DIR}/07_scheme_performance.csv")
# Validate returns are numeric, coerce errors to NaN
for col in ['return_1yr', 'return_3yr', 'return_5yr']:
    perf_df[col] = pd.to_numeric(perf_df[col], errors='coerce')
# Check expense_ratio range (0.1% - 2.5%)
perf_df['expense_ratio'] = pd.to_numeric(perf_df['expense_ratio'], errors='coerce')
perf_df = perf_df[(perf_df['expense_ratio'] >= 0.1) & (perf_df['expense_ratio'] <= 2.5)]
perf_df.to_csv(f"{PROC_DIR}/07_scheme_performance.csv", index=False)

# Basic copy for the remaining 7 files to processed directory
files_to_copy = [
    '01_fund_master.csv', '03_aum_by_fund_house.csv', '04_monthly_sip.csv',
    '05_category_inflows.csv', '06_folio_count.csv', '09_holdings.csv', '10_benchmark.csv'
]
dfs = {'02_nav_history.csv': nav_df, '08_transactions.csv': txn_df, '07_scheme_performance.csv': perf_df}

for f in files_to_copy:
    print(f"Processing {f}...")
    df = pd.read_csv(f"{RAW_DIR}/{f}")
    df.to_csv(f"{PROC_DIR}/{f}", index=False)
    dfs[f] = df

# LOAD TO SQLITE
print(f"Loading data to SQLite database {DB_PATH}...")
conn = sqlite3.connect(DB_PATH)

# Load to corresponding tables in star schema
dfs['01_fund_master.csv'].to_sql('dim_fund', conn, if_exists='replace', index=False)
dfs['02_nav_history.csv'].to_sql('fact_nav', conn, if_exists='replace', index=False)
dfs['03_aum_by_fund_house.csv'].to_sql('fact_aum', conn, if_exists='replace', index=False)
dfs['04_monthly_sip.csv'].to_sql('monthly_sip', conn, if_exists='replace', index=False)
dfs['05_category_inflows.csv'].to_sql('category_inflows', conn, if_exists='replace', index=False)
dfs['06_folio_count.csv'].to_sql('folio_count', conn, if_exists='replace', index=False)
dfs['07_scheme_performance.csv'].to_sql('fact_performance', conn, if_exists='replace', index=False)
dfs['08_transactions.csv'].to_sql('fact_transactions', conn, if_exists='replace', index=False)
dfs['09_holdings.csv'].to_sql('holdings', conn, if_exists='replace', index=False)
dfs['10_benchmark.csv'].to_sql('benchmark', conn, if_exists='replace', index=False)

conn.close()
print("ETL complete! Data loaded successfully.")
