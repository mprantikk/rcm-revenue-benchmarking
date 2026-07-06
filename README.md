# 🏥 RCM Revenue Benchmarking (Python + MySQL)

A portfolio project modeling the kind of Revenue Cycle Management (RCM) benchmarking work
behind my Data Operations Manager role at Commure — built with **MySQL** for storage and
**Python** for KPI computation, benchmarking, and reporting. Uses a synthetic claims dataset
(no real patient, provider, or company data).

## 🎯 Objective

Revenue Cycle Management teams live and die by a handful of KPIs. This project stands up a
claims/payments/denials database and a Python script that computes those KPIs, benchmarks them
against standard industry targets, and flags where performance needs attention — the same kind
of scorecard a growth/data ops team would review monthly.

## 🗂️ Project Structure

```
rcm-revenue-benchmarking/
├── README.md                  # This file
├── schema.sql                  # MySQL table definitions
├── seed_data.sql                # Synthetic claims dataset (INSERT statements)
├── benchmarking_queries.sql      # Raw SQL versions of every KPI query
├── rcm_benchmarking.py            # Python script: connects to MySQL, computes KPIs, exports reports
├── requirements.txt                # Python dependencies
└── insights.md                      # Findings from running the analysis
```

## 🧱 Schema Overview

| Table         | Description                                          |
|---------------|-------------------------------------------------------|
| `providers`   | Physicians/providers with specialty and location      |
| `payers`      | Insurance payers, categorized by type (Commercial/Medicare/Medicaid/Self-Pay) |
| `claims`      | Claim headers: billed/allowed amounts, status, resubmissions |
| `payments`    | Payments received against claims                       |
| `denials`     | Denial records with reason codes                         |

See [`schema.sql`](./schema.sql) for full DDL.

## 📊 KPIs Computed

| KPI                      | What it measures                                    | Industry Target |
|---------------------------|-------------------------------------------------------|------------------|
| **Days in AR**             | Avg. days from service to payment                    | < 40 days        |
| **Denial Rate**             | % of claims denied                                    | < 10%            |
| **Clean Claim Rate**         | % of claims paid with zero resubmissions             | > 90%            |
| **Net Collection Rate**       | Total collected ÷ total allowed                     | > 95%            |
| **Charge Lag**                | Avg. days from service to claim submission          | < 5 days         |

Plus supporting breakdowns: denial rate by payer type, top denial reasons, monthly revenue
trend (billed vs. collected), and provider-level collections ranking.

## ▶️ How to Run

**1. Set up MySQL and load the schema + data:**
```bash
mysql -u root -p -e "CREATE DATABASE rcm_benchmarking;"
mysql -u root -p rcm_benchmarking < schema.sql
mysql -u root -p rcm_benchmarking < seed_data.sql
```

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure your DB connection** (environment variables):
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_NAME=rcm_benchmarking
```

**4. Run the benchmarking script:**
```bash
python rcm_benchmarking.py
```

This prints a benchmark scorecard to the console and exports `kpi_scorecard.csv` and
`monthly_revenue_trend.csv`.

## 📈 Sample Finding

> Self-Pay and Medicaid claims run 20-35 days slower in AR and have meaningfully higher denial
> rates than Commercial payers — a pattern that shows up in almost every RCM benchmarking
> exercise and points to where front-end eligibility verification would have the most impact.
> See [`insights.md`](./insights.md) for the full write-up with actual numbers from the dataset.

## 🛠️ Tools & Concepts Used

`MySQL` · `Python` (pandas, mysql-connector-python) · KPI benchmarking · Window functions
(`RANK`) · `DATEDIFF` date math · Conditional aggregation · Denial/AR analysis patterns used
in healthcare Revenue Cycle Management

---
**Author:** [Masud Parvej](https://www.linkedin.com/in/mprantikk) — Data Analytics & Growth Operations
