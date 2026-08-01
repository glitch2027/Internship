import pandas as pd
import numpy as np
import requests
import datetime
import os

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

# 1. 01_fund_master.csv
print("Generating 01_fund_master.csv...")
url = "https://api.mfapi.in/mf"
response = requests.get(url)
all_funds = response.json()
# Take a subset of 50 funds for manageable data
selected_funds = all_funds[:50]
fund_master_data = []
categories = ['Large Cap', 'Mid Cap', 'Small Cap', 'Debt', 'Liquid', 'Flexi Cap']
fund_houses = ['SBI Mutual Fund', 'HDFC Mutual Fund', 'ICICI Prudential Mutual Fund', 'Nippon India Mutual Fund', 'Axis Mutual Fund', 'Kotak Mutual Fund']
risk_grades = ['Low', 'Moderate', 'High', 'Very High']

for f in selected_funds:
    fund_master_data.append({
        'amfi_code': f['schemeCode'],
        'scheme_name': f['schemeName'],
        'fund_house': np.random.choice(fund_houses),
        'category': np.random.choice(categories),
        'sub_category': 'Equity' if np.random.random() > 0.3 else 'Debt',
        'risk_grade': np.random.choice(risk_grades),
        'launch_date': (datetime.date(2015, 1, 1) + datetime.timedelta(days=np.random.randint(0, 3000))).strftime('%Y-%m-%d')
    })
df_master = pd.DataFrame(fund_master_data)
df_master.to_csv(f"{RAW_DIR}/01_fund_master.csv", index=False)

# 2. 02_nav_history.csv
print("Generating 02_nav_history.csv...")
nav_data = []
for f in selected_funds[:10]: # Fetch history for 10 funds to save time/API calls
    code = f['schemeCode']
    nav_res = requests.get(f"https://api.mfapi.in/mf/{code}")
    if nav_res.status_code == 200:
        hist = nav_res.json().get('data', [])
        for entry in hist[:200]: # last 200 days
            # Introduce anomaly: some dates missing, some NAVs 0 or negative occasionally
            nav_val = float(entry['nav'])
            if np.random.random() < 0.02:
                nav_val = -10.5 # anomaly
            nav_data.append({
                'amfi_code': code,
                'date': entry['date'], # dd-mm-yyyy format usually from API
                'nav': nav_val
            })
df_nav = pd.DataFrame(nav_data)
df_nav.to_csv(f"{RAW_DIR}/02_nav_history.csv", index=False)

# 3. 03_aum_by_fund_house.csv
print("Generating 03_aum_by_fund_house.csv...")
aum_data = []
for fh in fund_houses:
    aum_data.append({
        'fund_house': fh,
        'total_aum_cr': round(np.random.uniform(50000, 500000), 2),
        'report_date': '2023-12-31'
    })
pd.DataFrame(aum_data).to_csv(f"{RAW_DIR}/03_aum_by_fund_house.csv", index=False)

# 4. 04_monthly_sip.csv
print("Generating 04_monthly_sip.csv...")
sip_data = []
months = pd.date_range(start='2023-01-01', periods=12, freq='ME')
for m in months:
    sip_data.append({
        'month': m.strftime('%Y-%m'),
        'total_sip_inflow_cr': round(np.random.uniform(10000, 15000), 2),
        'new_sip_accounts': np.random.randint(500000, 1000000)
    })
pd.DataFrame(sip_data).to_csv(f"{RAW_DIR}/04_monthly_sip.csv", index=False)

# 5. 05_category_inflows.csv
print("Generating 05_category_inflows.csv...")
cat_data = []
for c in categories:
    cat_data.append({
        'category': c,
        'net_inflow_cr': round(np.random.uniform(-1000, 5000), 2),
        'month': '2023-12'
    })
pd.DataFrame(cat_data).to_csv(f"{RAW_DIR}/05_category_inflows.csv", index=False)

# 6. 06_folio_count.csv
print("Generating 06_folio_count.csv...")
folio_data = []
for f in selected_funds:
    folio_data.append({
        'amfi_code': f['schemeCode'],
        'retail_folios': np.random.randint(1000, 500000),
        'corporate_folios': np.random.randint(10, 5000),
        'report_date': '2023-12-31'
    })
pd.DataFrame(folio_data).to_csv(f"{RAW_DIR}/06_folio_count.csv", index=False)

# 7. 07_scheme_performance.csv
print("Generating 07_scheme_performance.csv...")
perf_data = []
for f in selected_funds:
    # Introduce anomalies in expense_ratio (e.g. 5.5% which is invalid) and return values as strings
    exp_ratio = round(np.random.uniform(0.1, 3.0), 2)
    if np.random.random() < 0.05:
        exp_ratio = 5.5 # Anomaly
        
    ret_1y = round(np.random.uniform(-5.0, 30.0), 2)
    if np.random.random() < 0.05:
        ret_1y = "Error" # Anomaly
        
    perf_data.append({
        'amfi_code': f['schemeCode'],
        'expense_ratio': exp_ratio,
        'return_1yr': ret_1y,
        'return_3yr': round(np.random.uniform(5.0, 25.0), 2),
        'return_5yr': round(np.random.uniform(7.0, 20.0), 2)
    })
pd.DataFrame(perf_data).to_csv(f"{RAW_DIR}/07_scheme_performance.csv", index=False)

# 8. 08_transactions.csv
print("Generating 08_transactions.csv...")
txn_data = []
txn_types = ['SIP', 'Lumpsum', 'Redemption', 'sip', 'LUMP', 'Red'] # Intentional formatting anomalies
kyc_status = ['Verified', 'Pending', 'Rejected', 'N/A']

for _ in range(1000):
    amount = round(np.random.uniform(-5000, 100000), 2) # Anomalies: negative amounts
    txn_data.append({
        'transaction_id': f"TXN{np.random.randint(100000, 999999)}",
        'amfi_code': np.random.choice([f['schemeCode'] for f in selected_funds]),
        'investor_id': f"INV{np.random.randint(1000, 9999)}",
        'transaction_type': np.random.choice(txn_types),
        'amount': amount,
        'transaction_date': (datetime.date(2023, 1, 1) + datetime.timedelta(days=np.random.randint(0, 365))).strftime('%d/%m/%Y'), # Different date format
        'kyc_status': np.random.choice(kyc_status)
    })
pd.DataFrame(txn_data).to_csv(f"{RAW_DIR}/08_transactions.csv", index=False)

# 9. 09_holdings.csv
print("Generating 09_holdings.csv...")
holdings_data = []
stocks = ['Reliance Industries', 'TCS', 'HDFC Bank', 'Infosys', 'ICICI Bank', 'ITC']
for f in selected_funds:
    num_holdings = np.random.randint(2, 5)
    for _ in range(num_holdings):
        holdings_data.append({
            'amfi_code': f['schemeCode'],
            'stock_name': np.random.choice(stocks),
            'allocation_percentage': round(np.random.uniform(1.0, 15.0), 2)
        })
pd.DataFrame(holdings_data).to_csv(f"{RAW_DIR}/09_holdings.csv", index=False)

# 10. 10_benchmark.csv
print("Generating 10_benchmark.csv...")
bench_data = []
indices = ['NIFTY 50', 'BSE SENSEX', 'NIFTY Bank', 'NIFTY Midcap 100']
for i in indices:
    bench_data.append({
        'index_name': i,
        'return_1yr': round(np.random.uniform(10.0, 25.0), 2),
        'return_3yr': round(np.random.uniform(12.0, 20.0), 2),
        'return_5yr': round(np.random.uniform(10.0, 18.0), 2)
    })
pd.DataFrame(bench_data).to_csv(f"{RAW_DIR}/10_benchmark.csv", index=False)

print("All 10 CSV datasets generated in data/raw!")
