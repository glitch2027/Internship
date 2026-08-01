-- dim_fund
CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT,
    fund_house TEXT,
    category TEXT,
    sub_category TEXT,
    risk_grade TEXT,
    launch_date DATE
);

-- dim_date (typically generated in a data warehouse, we create a simplified version)
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week TEXT,
    is_weekend BOOLEAN
);

-- fact_nav
CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    date DATE,
    nav REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date_id)
);

-- fact_transactions
CREATE TABLE fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    amfi_code INTEGER,
    investor_id TEXT,
    transaction_type TEXT,
    amount REAL,
    transaction_date DATE,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date_id)
);

-- fact_performance
CREATE TABLE fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    expense_ratio REAL,
    return_1yr REAL,
    return_3yr REAL,
    return_5yr REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_aum
CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT,
    total_aum_cr REAL,
    report_date DATE,
    FOREIGN KEY (report_date) REFERENCES dim_date(date_id)
);
