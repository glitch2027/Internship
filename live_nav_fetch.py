import requests
import pandas as pd
import json
import os

def fetch_and_save_nav(scheme_code, scheme_name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            df = pd.DataFrame(data['data'])
            # Add scheme code and name for tracking if needed
            df['scheme_code'] = scheme_code
            df['scheme_name'] = scheme_name
            
            file_name = scheme_name.replace(' ', '_').lower()
            file_path = f"data/raw/{file_name}_nav.csv"
            df.to_csv(file_path, index=False)
            print(f"Saved NAV for {scheme_name} ({scheme_code}) to {file_path}. Rows: {len(df)}")
        else:
            print(f"No NAV data found for {scheme_name}")
    else:
        print(f"Failed to fetch data for {scheme_name}. Status code: {response.status_code}")

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    
    schemes = {
        "HDFC Top 100 Direct": 125497,
        "SBI Bluechip": 119551,
        "ICICI Bluechip": 120503,
        "Nippon Large Cap": 118632,
        "Axis Bluechip": 119092,
        "Kotak Bluechip": 120841
    }
    
    print("Fetching NAV data from mfapi.in...\n")
    for name, code in schemes.items():
        fetch_and_save_nav(code, name)
    print("\nFetch complete!")
