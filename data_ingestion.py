import os
import glob
import pandas as pd

def load_and_summarize_datasets(raw_dir="data/raw"):
    # Only load the 10 provided CSVs (which are numbered 01_ to 10_)
    # This prevents loading the live NAV fetched CSVs which don't have this prefix
    csv_files = [f for f in glob.glob(os.path.join(raw_dir, "*.csv")) 
                 if os.path.basename(f)[:2].isdigit() and os.path.basename(f)[2] == '_']
    
    if len(csv_files) != 10:
        print(f"Expected 10 core CSV datasets, but found {len(csv_files)} in {raw_dir}")
        if not csv_files:
            return {}

    print(f"Found {len(csv_files)} CSV files. Loading and summarizing...\n")
    
    datasets = {}
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path)
            datasets[file_name] = df
            print(f"--- Dataset: {file_name} ---")
            print(f"Shape: {df.shape}")
            print(f"Data Types:\n{df.dtypes}\n")
            print(f"Head:\n{df.head()}\n")
            
            # Simple anomaly detection: missing values or empty dataframe
            if df.empty:
                print(f"Anomaly: {file_name} is empty.\n")
            if df.isnull().values.any():
                print(f"Anomaly: {file_name} contains missing values.\n")
                
        except Exception as e:
            print(f"Failed to load {file_name}: {e}\n")
            
    return datasets

def explore_fund_master(df):
    print("\n--- Exploring Fund Master ---")
    if 'fund_house' in df.columns:
        print(f"Unique Fund Houses ({len(df['fund_house'].unique())}):\n", df['fund_house'].unique()[:5], "...")
    if 'category' in df.columns:
        print(f"Unique Categories:\n", df['category'].unique())
    if 'sub_category' in df.columns:
        print(f"Unique Sub-Categories:\n", df['sub_category'].unique())
    if 'risk_grade' in df.columns:
        print(f"Unique Risk Grades:\n", df['risk_grade'].unique())
    
    if 'amfi_code' in df.columns:
        print("\nAMFI Code Structure (First 5):")
        print(df['amfi_code'].head())
        print(f"AMFI Code type: {df['amfi_code'].dtype}")

def validate_amfi_codes(fund_master, nav_history):
    print("\n--- Validating AMFI Codes ---")
    if 'amfi_code' not in fund_master.columns or 'amfi_code' not in nav_history.columns:
        print("Error: 'amfi_code' column missing from one of the datasets.")
        return
        
    master_codes = set(fund_master['amfi_code'].dropna().astype(str))
    nav_codes = set(nav_history['amfi_code'].dropna().astype(str))
    
    missing_in_nav = master_codes - nav_codes
    
    print(f"Total AMFI codes in fund_master: {len(master_codes)}")
    print(f"Total AMFI codes in nav_history: {len(nav_codes)}")
    print(f"Codes in fund_master but missing in nav_history: {len(missing_in_nav)}")
    
    print("\n--- Data Quality Summary ---")
    if len(missing_in_nav) == 0:
        print("Excellent: All AMFI codes in fund_master exist in nav_history.")
    else:
        print(f"Issue: {len(missing_in_nav)} AMFI codes from fund_master are missing in nav_history.")
        print(f"Sample missing codes: {list(missing_in_nav)[:5]}")

if __name__ == "__main__":
    datasets = load_and_summarize_datasets()
    
    # Try to extract fund_master and nav_history if they exist (case-insensitive)
    fund_master_df = None
    nav_history_df = None
    
    for name, df in datasets.items():
        if "fund_master" in name.lower():
            fund_master_df = df
        elif "nav_history" in name.lower():
            nav_history_df = df
            
    if fund_master_df is not None:
        explore_fund_master(fund_master_df)
    else:
        print("\nNotice: fund_master.csv not found, skipping fund master exploration.")
        
    if fund_master_df is not None and nav_history_df is not None:
        validate_amfi_codes(fund_master_df, nav_history_df)
    else:
        print("\nNotice: Need both fund_master.csv and nav_history.csv to validate AMFI codes.")
