"""
rcm_benchmarking.py

Connects to the RCM MySQL database, computes core Revenue Cycle Management
(RCM) KPIs, benchmarks them against industry targets, breaks results down by
payer type and denial reason, and exports CSV reports.

Usage:
    cp .env.example .env        # set DB credentials
    python rcm_benchmarking.py  # prints the scorecard, writes CSVs to ./output
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional; plain env vars work too
    pass

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "output"))

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "rcm_benchmarking"),
}

# Industry benchmark targets used for the scorecard
BENCHMARK_TARGETS = {
    "avg_days_in_ar": {"target": 40, "direction": "lower_is_better", "unit": " days"},
    "denial_rate_pct": {"target": 10, "direction": "lower_is_better", "unit": "%"},
    "clean_claim_rate_pct": {"target": 90, "direction": "higher_is_better", "unit": "%"},
    "net_collection_rate_pct": {"target": 95, "direction": "higher_is_better", "unit": "%"},
    "avg_charge_lag_days": {"target": 5, "direction": "lower_is_better", "unit": " days"},
}

KPI_QUERIES = {
    # Days from date of service to payment, for paid claims
    "avg_days_in_ar": """
        SELECT ROUND(AVG(DATEDIFF(p.payment_date, c.service_date)), 1)
        FROM claims c JOIN payments p ON p.claim_id = c.claim_id
        WHERE c.claim_status = 'paid'
    """,
    # Share of adjudicated claims (paid or denied) that were denied
    "denial_rate_pct": """
        SELECT ROUND(100.0 * SUM(claim_status = 'denied') / COUNT(*), 1)
        FROM claims
        WHERE claim_status IN ('paid', 'denied')
    """,
    # Paid on first submission, as a share of adjudicated claims
    "clean_claim_rate_pct": """
        SELECT ROUND(100.0 * SUM(claim_status = 'paid' AND resubmission_count = 0)
                     / NULLIF(COUNT(*), 0), 1)
        FROM claims
        WHERE claim_status IN ('paid', 'denied')
    """,
    # Collected vs. contractually allowed, for paid claims
    "net_collection_rate_pct": """
        SELECT ROUND(100.0 * SUM(p.paid_amount) / NULLIF(SUM(c.allowed_amount), 0), 1)
        FROM claims c JOIN payments p ON p.claim_id = c.claim_id
        WHERE c.claim_status = 'paid'
    """,
    # Days from date of service to claim submission
    "avg_charge_lag_days": """
        SELECT ROUND(AVG(DATEDIFF(submission_date, service_date)), 1)
        FROM claims
    """,
}

PAYER_BREAKDOWN_SQL = """
    SELECT
        pay.payer_type,
        COUNT(*) AS total_claims,
        ROUND(100.0 * SUM(c.claim_status = 'denied')
              / NULLIF(SUM(c.claim_status IN ('paid', 'denied')), 0), 1) AS denial_rate_pct,
        ROUND(AVG(CASE WHEN c.claim_status = 'paid'
                       THEN DATEDIFF(p.payment_date, c.service_date) END), 1) AS avg_days_in_ar
    FROM claims c
    JOIN payers pay ON pay.payer_id = c.payer_id
    LEFT JOIN payments p ON p.claim_id = c.claim_id
    GROUP BY pay.payer_type
    ORDER BY denial_rate_pct DESC
"""

TOP_DENIALS_SQL = """
    SELECT d.denial_code, d.denial_reason, COUNT(*) AS occurrences,
           ROUND(SUM(c.billed_amount), 2) AS billed_amount_at_risk
    FROM denials d JOIN claims c ON c.claim_id = d.claim_id
    GROUP BY d.denial_code, d.denial_reason
    ORDER BY occurrences DESC, billed_amount_at_risk DESC
    LIMIT 5
"""

MONTHLY_TREND_SQL = """
    SELECT DATE_FORMAT(c.service_date, '%Y-%m') AS month,
           COUNT(*) AS claims,
           ROUND(SUM(c.billed_amount), 2) AS billed,
           ROUND(COALESCE(SUM(p.paid_amount), 0), 2) AS collected
    FROM claims c
    LEFT JOIN payments p ON p.claim_id = c.claim_id
    GROUP BY 1
    ORDER BY 1
"""


def get_connection():
    try:
        import mysql.connector
    except ImportError as exc:
        raise SystemExit(
            "mysql-connector-python is required: pip install -r requirements.txt"
        ) from exc
    return mysql.connector.connect(**DB_CONFIG)


def run_query(conn, sql: str) -> pd.DataFrame:
    cur = conn.cursor()
    try:
        cur.execute(sql)
        columns = [c[0] for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        cur.close()


def run_scalar(conn, sql: str) -> float:
    value = run_query(conn, sql).iat[0, 0]
    return float(value) if value is not None else float("nan")


def compute_kpis(conn) -> dict[str, float]:
    return {name: run_scalar(conn, sql) for name, sql in KPI_QUERIES.items()}


def benchmark_scorecard(kpis: dict[str, float]) -> pd.DataFrame:
    """Compare each KPI with its target. Pure function, unit-tested."""
    rows = []
    for metric, value in kpis.items():
        spec = BENCHMARK_TARGETS[metric]
        lower_better = spec["direction"] == "lower_is_better"
        on_target = value <= spec["target"] if lower_better else value >= spec["target"]
        rows.append(
            {
                "metric": metric,
                "value": f"{value:g}{spec['unit']}",
                "target": f"{'<=' if lower_better else '>='} {spec['target']}{spec['unit']}",
                "status": "on target" if on_target else "off target",
                "gap": round(value - spec["target"], 1),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    conn = get_connection()
    try:
        kpis = compute_kpis(conn)
        scorecard = benchmark_scorecard(kpis)
        payers = run_query(conn, PAYER_BREAKDOWN_SQL)
        denials = run_query(conn, TOP_DENIALS_SQL)
        trend = run_query(conn, MONTHLY_TREND_SQL)
    finally:
        conn.close()

    print("=== RCM Benchmark Scorecard ===")
    print(scorecard.to_string(index=False))
    print("\n=== By Payer Type ===")
    print(payers.to_string(index=False))
    print("\n=== Top 5 Denial Reasons ===")
    print(denials.to_string(index=False))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    scorecard.to_csv(OUTPUT_DIR / "kpi_scorecard.csv", index=False)
    payers.to_csv(OUTPUT_DIR / "payer_breakdown.csv", index=False)
    denials.to_csv(OUTPUT_DIR / "top_denials.csv", index=False)
    trend.to_csv(OUTPUT_DIR / "monthly_revenue_trend.csv", index=False)
    print(f"\nSaved 4 CSV reports to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
