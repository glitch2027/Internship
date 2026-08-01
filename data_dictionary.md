# Mutual Fund Analytics - Data Dictionary

This data dictionary outlines the schema and business definitions for the `bluestock_mf.db` SQLite database.

## Star Schema Overview
The database employs a Star Schema design to enable analytical queries:
- **Dimensions**: `dim_fund`
- **Facts**: `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, `monthly_sip`, `category_inflows`, `folio_count`, `holdings`, `benchmark`

---

## Dimension Tables

### `dim_fund` (Fund Master)
Contains the core metadata for all mutual funds.
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `amfi_code` | INTEGER (PK) | Unique identifier assigned by AMFI (Primary Key). |
| `scheme_name` | TEXT | Full name of the mutual fund scheme. |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC). |
| `category` | TEXT | Broad category (e.g., Large Cap, Mid Cap, Debt). |
| `sub_category` | TEXT | Specific focus area (e.g., Equity). |
| `risk_grade` | TEXT | Risk classification (Low, Moderate, High, Very High). |
| `launch_date` | DATE | Inception date of the scheme. |

---

## Fact Tables

### `fact_nav` (Net Asset Value History)
Records the daily historical prices for the funds.
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `nav_id` | INTEGER (PK) | Auto-incremented primary key. |
| `amfi_code` | INTEGER (FK) | References `dim_fund.amfi_code`. |
| `date` | DATE | Date of the NAV record. |
| `nav` | REAL | The Net Asset Value price on that date. |

### `fact_transactions` (Investor Transactions)
Contains individual transaction records. (Note: Synthetic data for analytical purposes).
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `transaction_id` | TEXT (PK) | Unique transaction string. |
| `amfi_code` | INTEGER (FK) | References `dim_fund.amfi_code`. |
| `investor_id` | TEXT | Unique ID for the retail/corporate investor. |
| `transaction_type`| TEXT | 'SIP', 'Lumpsum', or 'Redemption'. |
| `amount` | REAL | Value of the transaction. (Cleaned: > 0). |
| `transaction_date`| DATE | Formatted as YYYY-MM-DD. |
| `kyc_status` | TEXT | 'Verified', 'Pending', 'Rejected'. |

### `fact_performance` (Fund Returns & Ratios)
Contains annualized returns and expense metrics.
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `performance_id` | INTEGER (PK) | Auto-incremented primary key. |
| `amfi_code` | INTEGER (FK) | References `dim_fund.amfi_code`. |
| `expense_ratio` | REAL | Percentage fee charged by the fund (Range 0.1 - 2.5). |
| `return_1yr` | REAL | 1-Year annualized return (%). |
| `return_3yr` | REAL | 3-Year annualized return (%). |
| `return_5yr` | REAL | 5-Year annualized return (%). |

### `fact_aum` (Assets Under Management)
Aggregated AUM data grouped by the AMC / Fund House.
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `aum_id` | INTEGER (PK) | Auto-incremented primary key. |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC). |
| `total_aum_cr` | REAL | Total AUM in Crores (INR). |
| `report_date` | DATE | End-of-period reporting date. |
