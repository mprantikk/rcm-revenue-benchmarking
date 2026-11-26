# RCM Revenue Benchmarking

[![CI](https://github.com/mprantikk/rcm-revenue-benchmarking/actions/workflows/ci.yml/badge.svg)](https://github.com/mprantikk/rcm-revenue-benchmarking/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

A Python + MySQL tool that answers the question every healthcare finance team asks: **why is our money taking so long to arrive?**

It computes the five core Revenue Cycle Management (RCM) KPIs from claims, payments and denials, scores them against industry targets, and breaks the results down by payer type and denial reason. All data is synthetic.

## Results on the sample dataset

1,093 claims from 15 providers and 7 payers, Jan 2023 to Dec 2024.

| KPI | Result | Target | Status |
|---|---:|---:|---|
| Days in AR | 44.4 days | ≤ 40 | Off target |
| Denial rate | 12.7% | ≤ 10% | Off target |
| Clean claim rate | 70.7% | ≥ 90% | Off target |
| Net collection rate | 95.1% | ≥ 95% | On target |
| Charge lag | 5.4 days | ≤ 5 | Off target |

**By payer type**

| Payer type | Claims | Denial rate | Days in AR |
|---|---:|---:|---:|
| Self-Pay | 168 | 19.1% | 64.2 |
| Medicaid | 152 | 16.1% | 56.8 |
| Medicare | 162 | 13.7% | 51.4 |
| Commercial | 611 | 9.9% | 35.1 |

### What the data says

- **Payer mix drives the problem, not provider quality.** Commercial claims meet both the AR and denial targets. Self-Pay takes 83% longer to collect and is denied almost twice as often.
- **Once a claim is paid, collection is healthy** (95.1% of the allowed amount). The money is lost earlier: in denials and slow adjudication.
- **$154K of billed charges were denied.** The two most preventable codes, CO-16 (missing information) and CO-11 (diagnosis/procedure mismatch), account for $60K of that. A pre-submission claim scrubber targets exactly these.
- **Recommended levers:** eligibility and documentation checks before submitting Self-Pay and Medicaid claims, and an aging-AR follow-up queue prioritised by payer type.

More detail in [insights.md](insights.md).

## How it works

```
schema.sql + seed_data.sql ──► MySQL ──► rcm_benchmarking.py ──► console scorecard
                                                │
                                                └──► output/*.csv  (scorecard, payer breakdown,
                                                                    top denials, monthly trend)
```

| KPI | Definition |
|---|---|
| Days in AR | Average days from date of service to payment, paid claims |
| Denial rate | Denied ÷ adjudicated (paid + denied) claims |
| Clean claim rate | Paid on first submission ÷ adjudicated claims |
| Net collection rate | Paid ÷ allowed amount, paid claims |
| Charge lag | Average days from date of service to submission |

## Run it

```bash
git clone https://github.com/mprantikk/rcm-revenue-benchmarking.git
cd rcm-revenue-benchmarking
docker compose up -d                 # MySQL 8 with schema + seed data loaded
pip install -r requirements.txt
cp .env.example .env
python rcm_benchmarking.py           # prints the scorecard, writes output/*.csv
pytest -v                            # unit + integration tests
```

`benchmarking_queries.sql` holds the standalone SQL versions of every metric (by payer, by provider with `RANK()`, by month) for use in a SQL client or BI tool.

## Tests and CI

- **Unit tests** cover the scorecard logic: target direction, boundaries, gap calculation.
- **Integration tests** run every KPI query against the seeded database and check row counts, value ranges, known results and referential integrity (every paid claim has a payment).
- **GitHub Actions** spins up MySQL 8, loads the data, runs the tests and the report, and uploads the CSVs as a build artifact.

## Project structure

```
├── rcm_benchmarking.py        KPI engine and report export
├── schema.sql                 normalised schema with indexes
├── seed_data.sql              synthetic claims data
├── benchmarking_queries.sql   standalone analysis queries
├── insights.md                written findings
├── tests/                     pytest unit + integration tests
├── docker-compose.yml         local MySQL
└── .github/workflows/ci.yml   CI pipeline
```

## License

MIT. Built by [Masud Parvej](https://mprantikk.github.io/).
