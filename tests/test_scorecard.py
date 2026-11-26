
import pytest

from rcm_benchmarking import BENCHMARK_TARGETS, benchmark_scorecard


def test_lower_is_better_on_and_off_target():
    card = benchmark_scorecard({"avg_days_in_ar": 38.0, "denial_rate_pct": 12.0})
    status = dict(zip(card.metric, card.status))
    assert status["avg_days_in_ar"] == "on target"
    assert status["denial_rate_pct"] == "off target"


def test_higher_is_better_boundary_counts_as_on_target():
    card = benchmark_scorecard({"net_collection_rate_pct": 95.0})
    assert card.loc[0, "status"] == "on target"
    assert card.loc[0, "gap"] == 0.0


def test_gap_sign_and_formatting():
    card = benchmark_scorecard({"clean_claim_rate_pct": 70.7})
    row = card.iloc[0]
    assert row.gap == pytest.approx(-19.3)
    assert row.value == "70.7%"
    assert row.target == ">= 90%"


def test_every_kpi_has_a_target():
    card = benchmark_scorecard({k: 1.0 for k in BENCHMARK_TARGETS})
    assert list(card.metric) == list(BENCHMARK_TARGETS)
    assert not card.isna().any().any()
