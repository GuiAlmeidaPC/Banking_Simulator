import math

import pytest

from app.services.loan_calculator import simulate_loan


def test_classic_30y_mortgage_matches_textbook():
    """$100k at 6% APR for 30y → ~$599.55/mo, ~$115,838 lifetime interest."""
    result = simulate_loan(
        principal=100_000, annual_interest_rate=6, years=30, funding_cost_rate=0
    )
    assert result.monthly_payment == pytest.approx(599.55, abs=0.01)
    assert result.interest_income == pytest.approx(115_838.19, abs=1.0)
    assert result.total_repayments == pytest.approx(
        result.principal + result.interest_income, abs=0.5
    )


def test_zero_interest_rate_is_supported():
    result = simulate_loan(
        principal=12_000, annual_interest_rate=0, years=1, funding_cost_rate=0
    )
    assert result.monthly_payment == pytest.approx(1000.0)
    assert result.interest_income == pytest.approx(0.0)
    assert result.total_repayments == pytest.approx(12_000.0)
    assert result.net_interest_income == pytest.approx(0.0)
    assert result.net_interest_margin == pytest.approx(0.0)


def test_funding_equal_to_interest_yields_zero_nii():
    result = simulate_loan(
        principal=50_000, annual_interest_rate=5, years=10, funding_cost_rate=5
    )
    assert result.net_interest_income == pytest.approx(0.0, abs=0.01)
    assert result.net_interest_margin == pytest.approx(0.0, abs=1e-6)


def test_funding_higher_than_interest_yields_negative_nii():
    result = simulate_loan(
        principal=10_000, annual_interest_rate=3, years=5, funding_cost_rate=4
    )
    assert result.net_interest_income < 0
    assert result.net_interest_margin < 0


def test_nim_is_annualized_and_close_to_spread():
    """For an amortizing loan with no funding cost, annualized NIM should
    approximate the nominal annual rate (in this case, 6%)."""
    result = simulate_loan(
        principal=100_000, annual_interest_rate=6, years=30, funding_cost_rate=0
    )
    # Avg balance ~ half of principal over the life; total interest / years / avg ~ rate.
    assert result.net_interest_margin == pytest.approx(0.06, abs=0.005)


def test_schedule_is_populated_when_requested():
    result = simulate_loan(
        principal=10_000,
        annual_interest_rate=6,
        years=1,
        funding_cost_rate=2,
        include_schedule=True,
    )
    assert result.schedule is not None
    assert len(result.schedule) == 12
    assert result.schedule[0].month == 1
    assert result.schedule[-1].remaining_balance == 0.0
    # Interest portion should decrease month over month for a fixed payment.
    interests = [e.interest for e in result.schedule]
    assert all(earlier >= later for earlier, later in zip(interests, interests[1:]))


def test_schedule_omitted_by_default():
    result = simulate_loan(
        principal=10_000, annual_interest_rate=6, years=1, funding_cost_rate=2
    )
    assert result.schedule is None


def test_totals_consistent_with_schedule():
    result = simulate_loan(
        principal=25_000,
        annual_interest_rate=7,
        years=5,
        funding_cost_rate=3,
        include_schedule=True,
    )
    assert result.schedule is not None
    sum_interest = sum(e.interest for e in result.schedule)
    sum_funding = sum(e.funding_cost for e in result.schedule)
    sum_payment = sum(e.payment for e in result.schedule)
    # Schedule values are rounded to cents, so allow small tolerance.
    assert math.isclose(sum_interest, result.interest_income, abs_tol=0.5)
    assert math.isclose(sum_funding, result.funding_cost, abs_tol=0.5)
    assert math.isclose(sum_payment, result.total_repayments, abs_tol=0.5)
