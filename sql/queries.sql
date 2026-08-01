-- 1. Top 5 funds by AUM
SELECT 
    f.fund_house, 
    SUM(a.total_aum_cr) as total_aum
FROM dim_fund f
JOIN fact_aum a ON f.fund_house = a.fund_house
GROUP BY f.fund_house
ORDER BY total_aum DESC
LIMIT 5;

-- 2. Average NAV per month for a specific fund (e.g. HDFC Top 100 which is 125497)
SELECT 
    strftime('%Y-%m', date) as month,
    AVG(nav) as average_nav
FROM fact_nav
WHERE amfi_code = 125497
GROUP BY month
ORDER BY month DESC;

-- 3. Total SIP Inflows by Month (from monthly_sip table)
SELECT 
    month, 
    total_sip_inflow_cr 
FROM monthly_sip 
ORDER BY month DESC;

-- 4. Transactions grouped by KYC status
SELECT 
    kyc_status, 
    COUNT(transaction_id) as txn_count, 
    SUM(amount) as total_volume
FROM fact_transactions
GROUP BY kyc_status;

-- 5. Funds with expense_ratio < 1%
SELECT 
    f.scheme_name, 
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;

-- 6. Highest 1-year return across all funds
SELECT 
    f.scheme_name, 
    p.return_1yr 
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_1yr DESC
LIMIT 5;

-- 7. Redemption vs Lumpsum volume comparison
SELECT 
    transaction_type, 
    COUNT(transaction_id) as txn_count, 
    SUM(amount) as total_amount
FROM fact_transactions
WHERE transaction_type IN ('Redemption', 'Lumpsum')
GROUP BY transaction_type;

-- 8. Total AUM by Fund Category (using average AUM representation)
SELECT 
    f.category, 
    COUNT(f.amfi_code) as total_funds
FROM dim_fund f
GROUP BY f.category;

-- 9. Volatility (Max - Min NAV) over the past month for a given fund
SELECT 
    amfi_code,
    MAX(nav) - MIN(nav) as volatility_spread
FROM fact_nav
GROUP BY amfi_code;

-- 10. Investor count per fund based on transactions
SELECT 
    f.scheme_name, 
    COUNT(DISTINCT t.investor_id) as unique_investors
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
GROUP BY f.scheme_name
ORDER BY unique_investors DESC
LIMIT 5;
