"""Runs the real KPI queries against the seeded MySQL database.

Skipped automatically when no database is reachable (e.g. a laptop without
Docker running). CI always provides one.
"""

import pytest

import rcm_benchmarking as rcm


@pytest.fixture(scope="module")
def conn():
    try:
        c = rcm.get_connection()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"MySQL not reachable: {exc}")
    yield c
    c.close()


def test_seed_row_counts(conn):
    counts = rcm.run_query(
        conn,
        "SELECT (SELECT COUNT(*) FROM claims) AS claims,"
        " (SELECT COUNT(*) FROM payments) AS payments,"
        " (SELECT COUNT(*) FROM denials) AS denials",
    ).iloc[0]
    assert (counts.claims, counts.payments, counts.denials) == (1093, 942, 137)


def test_kpis_are_in_plausible_ranges(conn):
    k = rcm.compute_kpis(conn)
    assert 0 < k["avg_days_in_ar"] < 120
    assert 0 <= k["denial_rate_pct"] <= 100
    assert 0 <= k["clean_claim_rate_pct"] <= 100
    assert 50 <= k["net_collection_rate_pct"] <= 110
    assert 0 <= k["avg_charge_lag_days"] < 30


def test_known_results(conn):
    k = rcm.compute_kpis(conn)
    assert k["avg_days_in_ar"] == 44.4
    assert k["denial_rate_pct"] == 12.7
    assert k["net_collection_rate_pct"] == 95.1


def test_every_paid_claim_has_a_payment(conn):
    orphans = rcm.run_scalar(
        conn,
        "SELECT COUNT(*) FROM claims c LEFT JOIN payments p ON p.claim_id = c.claim_id"
        " WHERE c.claim_status = 'paid' AND p.payment_id IS NULL",
    )
    assert orphans == 0


def test_payer_breakdown_covers_all_payer_types(conn):
    df = rcm.run_query(conn, rcm.PAYER_BREAKDOWN_SQL)
    assert set(df.payer_type) == {"Commercial", "Medicare", "Medicaid", "Self-Pay"}
    assert df.total_claims.sum() == 1093
