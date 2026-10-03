# Consumer Transaction Data Analysis

A local data analytics web app that transforms raw transaction CSV files into interactive dashboards, business reports, and Excel exports instantly.

## What It Does

- Cleans and validates transaction data, including duplicate, date, amount, and status checks.
- Analyses revenue, trends, customer behaviour, order status, and high-value anomalies.
- Exports interactive charts, a cleaned CSV, and a three-sheet Excel report.

## Tech Stack

| Technology | Purpose |
| --- | --- |
| Python 3.11+ | Application and workflow runtime |
| Pandas | Data cleaning, analysis, and exports |
| NumPy | Numerical processing and anomaly detection |
| Matplotlib | Static dashboard generation |
| Plotly | Interactive charts |
| Streamlit | Local web application |
| openpyxl | Excel report generation |
| Oracle SQL | Reporting query examples |

## Project Structure

```text
Consumer Transaction Data Analysis/
|-- app.py                    # Streamlit upload and dashboard application
|-- analysis.py               # Logged summaries and anomaly analysis
|-- config.py                 # Shared paths, thresholds, categories, and styling
|-- data_cleaning.py          # Validation, type conversion, and cleaning rules
|-- dashboard.py              # Static Matplotlib dashboard generator
|-- export_to_excel.py        # Three-sheet Excel export workflow
|-- generate_data.py          # Reproducible sample data generator
|-- index.html                # Offline browser dashboard
|-- queries.sql               # Five Oracle-compatible reporting queries
|-- requirements.txt          # Pinned Python dependencies
|-- sample_transactions.csv   # Small 12-row INR showcase file
|-- test_transactions.csv     # 100-row INR test fixture
|-- README.md                 # Project documentation
```

## Requirements

- Python 3.11 or higher
- pip

## Installation

```powershell
git clone <repository-url>
cd "Consumer Transaction Data Analysis"
python -m pip install -r requirements.txt
```

## How to Run

```powershell
python -m streamlit run app.py
```

The browser opens automatically. Upload a CSV, wait for the analysis to finish, then review the dashboard and download the results.

For a quick showcase, upload `sample_transactions.csv` from the repository. For a larger local check, upload `test_transactions.csv`.

## Input File Format

| Column | Description |
| --- | --- |
| `txn_id` | Unique transaction identifier |
| `customer_id` | Customer identifier |
| `category` | Product or service category |
| `amount` | Numeric transaction amount |
| `status` | Transaction status such as `COMPLETED`, `PENDING`, or `CANCELLED` |
| `order_date` | Transaction date |

The optional `currency` or `currency_code` column is auto-detected when present. If it is missing, the app provides a manual currency selector.

## What You Get After Upload

1. Data Health Score
2. KPI Cards
3. Revenue Charts
4. Monthly Trends
5. Customer Analysis
6. Anomaly Detection
7. Cleaned CSV download
8. Excel report download

## SQL Queries

`queries.sql` contains 5 Oracle-compatible queries for the same dataset.

## Test File

Use `sample_transactions.csv` for a quick showcase or `test_transactions.csv` for a 100-row verification of the complete upload and analysis workflow.

## Screenshots

![Dashboard](transaction_dashboard.png)

## Author

Aakash Kataria | MCA — Kurukshetra University | Data Analytics Project
