# Duka Sales Exploration and Agent Network Clean-Up

**Ramadhan Fatuma Soud**

1 Million Devs for Africa Software Engineering course - 1 Million Devs Cohort

PLP Data Analytics with Python. Assignment 3 (Week 3).

## Summary of both engagements

**Engagement 1: Duka Electronics.** Duka Electronics is a Kenyan electronics retailer with five branches. The Head of Sales asked for answers on the January to June 2026 sales ahead of the leadership meeting. The notebook `duka_sales_exploration.ipynb` inspects the 1,000 orders and builds five columns: `revenue`, `month`, `weekday`, `is_weekend` and `price_band`. It then ranks branches and products and compares weekends with weekdays. It finds the best and worst months and exports the Premium online orders from Nairobi and Mombasa. The workbook `excel/duka_branch_summary.xlsx` rebuilds the branch totals with SUMIFS and XLOOKUP and a PivotTable. The notebook checks that the workbook totals match pandas.

**Engagement 2: Mobile money agent network.** A mobile money provider runs 20 agents across five counties. The regional manager wanted deposit and withdrawal totals from a legacy extract that holds injected quality problems. The notebook `agent_cleanup.ipynb` audits the extract across six data quality dimensions. It cleans the data with `clean_agent_data()` from `cleaning_pipeline.py` and merges the agent register. It then builds a county summary and a weekly pivot table. A Data Quality Report closes the notebook.

## Executive Summary (Duka Electronics)

- Nairobi earned KES 26.1M of the KES 71.8M half-year revenue and holds a 36.4% share that is almost double Mombasa in second place.
- Laptops brought in KES 41.5M or 57.9% of revenue even though Tablets led unit sales at 691 units.
- Weekend orders average KES 71,972 and weekday orders average KES 71,724 so order value stays flat across the week.
- April was the best month at KES 13.5M and June the worst at KES 10.9M which puts April 24.0% above June.
- Premium online orders from Nairobi and Mombasa total 83 orders worth KES 10.2M and deliver 14.2% of revenue from 8.3% of orders.

## Agent data before and after cleaning

| Measure | Rows |
|---|---|
| Rows before cleaning | 612 |
| Rows after cleaning | 600 |
| Rows removed | 12 |

The 12 removed rows are 11 exact duplicates and 1 repeated `txn_id`. The pipeline imputed 20 missing amounts and flagged them in `amount_imputed`. It flagged 40 amounts as outliers in `is_outlier`. Five of them share the value KES 250,000 and wait for a ledger check. Seven transactions point to agent AG099 and keep the county label Unknown.

## Files

| Path | Content |
|---|---|
| `generate_data.py` | Both dataset generators: Duka Electronics (seed 2026) and the agent network (seed 44) |
| `duka_sales_exploration.ipynb` | Engagement 1 notebook |
| `excel/duka_branch_summary.xlsx` | SUMIFS branch table and XLOOKUP region column and PivotTable |
| `outputs/premium_online_coast_capital.csv` | Premium online orders from Nairobi and Mombasa |
| `cleaning_pipeline.py` | The function `clean_agent_data(txns, agents)` that returns `clean_df` and `log` |
| `agent_cleanup.ipynb` | Engagement 2 notebook |
| `outputs/agent_transactions_clean.csv` | Clean agent transactions |
| `requirements.txt` | pandas and numpy and openpyxl |

## How to regenerate the data and run the notebooks

1. Install the libraries with `pip install -r requirements.txt`.
2. Open a terminal in the repository folder and run `python generate_data.py`. The script writes `duka_sales.csv` and `agents.csv` and `agent_transactions.csv` next to itself. The seeds stay at 2026 and 44.
3. Open `duka_sales_exploration.ipynb` and choose Restart then Run All. The notebook writes `outputs/premium_online_coast_capital.csv`.
4. Open `agent_cleanup.ipynb` and choose Restart then Run All. The notebook imports `cleaning_pipeline.py` and writes `outputs/agent_transactions_clean.csv`.

The raw generated CSV files stay out of the repository through `.gitignore`. The generator recreates them in one command.