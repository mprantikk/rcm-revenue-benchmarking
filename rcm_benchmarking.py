"""
rcm_benchmarking.py

Connects to the RCM MySQL database, pulls claims/payments/denials data,
computes core Revenue Cycle Management (RCM) KPIs, benchmarks them against
standard industry targets, and exports a summary report.

Usage:
    python rcm_benchmarking.py

Requires:
    pip install mysql-connector-python pandas

Configure your DB connection via environment variables (recommended) or
by editing DB_CONFIG below:
    export DB_HOST=localhost
    export DB_USER=root
    export DB_PASSWORD=yourpassword
    export DB_NAME=rcm_benchmarking
"""

import os
import pandas as pd

try:
    import mysql.connector
except ImportError as e:
    raise SystemExit(
        "mysql-connector-python is required. Install it with:\n"
        "    pip install mysql-connector-python pandas"
    ) from e

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "rcm_benchmarking"),
}

# Standard RCM industry benchmark targets used for the scorecard
BENCHMARK_TARGETS = {
    "avg_days_in_ar": {"target": 40, "direction": "lower_is_better", "unit": "days"},
    "denial_rate_pct": {"target": 10, "direction": "lower_is_better", "unit": "%"},
    "clean_claim_rate_pct": {"target": 90, "direction": "higher_is_better", "unit": "%"},
    "net_collection_rate_pct": {"target": 95, "direction": "higher_is_better", "unit": "%"},
    "avg_charge_lag_days": {"target": 5, "direction": "lower_is_better", "unit": "days"},
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def run_query(conn, sql):
    return pd.read_sql(sql, conn)


def compute_kpis(conn):
    kpis = {}

    kpis["avg_days_in_ar"] = run_query(conn, """
        SELECT ROUND(AVG(DATEDIFF(p.payment_date, c.service_date)), 1) AS v
        FROM claims c JOIN payments p ON p.claim_id = c.claim_id
        WHERE c.claim_status = 'paid'
    """).iloc[0]["v"]

    kpis["denial_rate_pct"] = run_query(conn, """
        SELECT ROUND(100.0 * SUM(CASE WHEN claim_status='denied' THEN 1 ELSE 0 END) / COUNT(*), 1) AS v
        FROM claims
    """).iloc[0]["v"]

    kpis["clean_claim_rate_pct"] = run_query(conn, """
        SELECT ROUND(100.0 * SUM(CASE WHEN claim_status='paid' AND resubmission_count=0 THEN 1 ELSE 0 END)
               / NULLIF(COUNT(*),0), 1) AS v
        FROM claims
    """).iloc[0]["v"]

    kpis["net_collection_rate_pct"] = run_query(conn, """
        SELECT ROUND(100.0 * SUM(p.paid_amount) / NULLIF(SUM(c.allowed_amount),0), 1) AS v
        FROM claims c JOIN payments p ON p.claim_id = c.claim_id
        WHERE c.claim_status = 'paid'
    """).iloc[0]["v"]

    kpis["avg_charge_lag_days"] = run_query(conn, """
        SELECT ROUND(AVG(DATEDIFF(submission_date, service_date)), 1) AS v
        FROM claims
    """).iloc[0]["v"]

    return kpis


def benchmark_scorecard(kpis):
    rows = []
    for metric, value in kpis.items():
        spec = BENCHMARK_TARGETS[metric]
        if spec["direction"] == "lower_is_better":
            status = "✅ On target" if value <= spec["target"] else "⚠️ Above target"
        else:
            status = "✅ On target" if value >= spec["target"] else "⚠️ Below target"
        rows.append({
            "metric": metric,
            "value": f"{value}{spec['unit']}",
            "target": f"{'<' if spec['direction']=='lower_is_better' else '>'} {spec['target']}{spec['unit']}",
            "status": status,
        })
    return pd.DataFrame(rows)


def payer_type_breakdown(conn):
    return run_query(conn, """
        SELECT
            pay.payer_type,
            COUNT(DISTINCT c.claim_id) AS total_claims,
            ROUND(100.0 * SUM(CASE WHEN c.claim_status='denied' THEN 1 ELSE 0 END) / COUNT(*), 1) AS denial_rate_pct
        FROM claims c
        JOIN payers pay ON pay.payer_id = c.payer_id
        GROUP BY pay.payer_type
        ORDER BY denial_rate_pct DESC
    """)


def top_denial_reasons(conn):
    return run_query(conn, """
        SELECT d.denial_code, d.denial_reason, COUNT(*) AS occurrences,
               ROUND(SUM(c.billed_amount), 2) AS billed_amount_impacted
        FROM denials d JOIN claims c ON c.claim_id = d.claim_id
        GROUP BY d.denial_code, d.denial_reason
        ORDER BY occurrences DESC
        LIMIT 5
    """)


def monthly_revenue_trend(conn):
    return run_query(conn, """
        SELECT DATE_FORMAT(c.service_date, '%Y-%m-01') AS month,
               ROUND(SUM(c.billed_amount), 2) AS billed,
               ROUND(SUM(p.paid_amount), 2) AS collected
        FROM claims c
        LEFT JOIN payments p ON p.claim_id = c.claim_id
        GROUP BY 1 ORDER BY 1
    """)


def main():
    conn = get_connection()
    try:
        print("Computing RCM benchmark KPIs...\n")
        kpis = compute_kpis(conn)
        scorecard = benchmark_scorecard(kpis)
        print("=== RCM Benchmark Scorecard ===")
        print(scorecard.to_string(index=False))

        print("\n=== Denial Rate by Payer Type ===")
        print(payer_type_breakdown(conn).to_string(index=False))

        print("\n=== Top 5 Denial Reasons ===")
        print(top_denial_reasons(conn).to_string(index=False))

        trend = monthly_revenue_trend(conn)
        trend.to_csv("monthly_revenue_trend.csv", index=False)
        scorecard.to_csv("kpi_scorecard.csv", index=False)
        print("\nSaved: kpi_scorecard.csv, monthly_revenue_trend.csv")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
