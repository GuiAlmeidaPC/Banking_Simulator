import math

import pytest

from app.schemas.loan import AmortizationType
from app.services.loan_calculator import simulate_loan


# ---------------------------------------------------------------------------
# Price (French) regime
# ---------------------------------------------------------------------------
def test_price_classic_30y_mortgage_matches_textbook():
    """$100k at 6% APR for 30y → ~$599.55 level payment, ~$115,838 lifetime interest."""
    result = simulate_loan(
        principal=100_000, annual_interest_rate=6, years=30, funding_cost_rate=0
    )
    assert result.first_payment == pytest.approx(599.55, abs=0.01)
    assert result.last_payment == pytest.approx(599.55, abs=0.01)
    assert result.interest_income == pytest.approx(115_838.19, abs=1.0)
    assert result.total_repayments == pytest.approx(
        result.principal + result.interest_income, abs=0.5
    )


def test_price_zero_interest_rate_is_supported():
    result = simulate_loan(
        principal=12_000, annual_interest_rate=0, years=1, funding_cost_rate=0
    )
    assert result.first_payment == pytest.approx(1000.0)
    assert result.last_payment == pytest.approx(1000.0)
    assert result.total_repayments == pytest.approx(12_000.0)


def test_price_nim_is_annualized_and_close_to_spread():
    result = simulate_loan(
        principal=100_000, annual_interest_rate=6, years=30, funding_cost_rate=0
    )
    assert result.net_interest_margin == pytest.approx(0.06, abs=0.005)


# ---------------------------------------------------------------------------
# SAC regime
# ---------------------------------------------------------------------------
def test_sac_textbook_case():
    """$12,000 at 12% APR (=1%/mo) for 1 year, SAC:
    - constant principal = $1,000/mo
    - month 1 payment = 1000 + 12000*0.01 = $1,120
    - month 12 payment = 1000 + 1000*0.01 = $1,010
    - total interest = (10+20+...+120) = $780
    """
    result = simulate_loan(
        principal=12_000,
        annual_interest_rate=12,
        years=1,
        funding_cost_rate=0,
        amortization=AmortizationType.sac,
        include_schedule=True,
    )
    assert result.first_payment == pytest.approx(1120.0, abs=0.01)
    assert result.last_payment == pytest.approx(1010.0, abs=0.01)
    assert result.interest_income == pytest.approx(780.0, abs=0.01)
    assert result.total_repayments == pytest.approx(12_780.0, abs=0.01)
    assert result.schedule is not None
    # Every principal payment is constant.
    principals = [e.principal for e in result.schedule]
    assert all(p == pytest.approx(1000.0, abs=0.01) for p in principals)


def test_sac_zero_rate_matches_price_zero_rate():
    """With 0% interest both regimes degenerate to equal-principal payments."""
    sac = simulate_loan(
        principal=10_000,
        annual_interest_rate=0,
        years=2,
        funding_cost_rate=0,
        amortization=AmortizationType.sac,
    )
    price = simulate_loan(
        principal=10_000,
        annual_interest_rate=0,
        years=2,
        funding_cost_rate=0,
        amortization=AmortizationType.price,
    )
    assert sac.first_payment == pytest.approx(price.first_payment)
    assert sac.last_payment == pytest.approx(price.last_payment)
    assert sac.total_repayments == pytest.approx(price.total_repayments)


def test_sac_pays_less_interest_than_price_for_same_loan():
    """SAC amortizes principal faster early on, so total interest is lower."""
    common = dict(
        principal=200_000, annual_interest_rate=10, years=20, funding_cost_rate=0
    )
    price = simulate_loan(**common, amortization=AmortizationType.price)
    sac = simulate_loan(**common, amortization=AmortizationType.sac)
    assert sac.interest_income < price.interest_income


def test_sac_first_payment_exceeds_last_payment():
    result = simulate_loan(
        principal=50_000,
        annual_interest_rate=8,
        years=10,
        funding_cost_rate=2,
        amortization=AmortizationType.sac,
    )
    assert result.first_payment > result.last_payment


# ---------------------------------------------------------------------------
# Shared / edge behavior
# ---------------------------------------------------------------------------
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
    assert result.schedule[-1].remaining_balance == 0.0


def test_schedule_omitted_by_default():
    result = simulate_loan(
        principal=10_000, annual_interest_rate=6, years=1, funding_cost_rate=2
    )
    assert result.schedule is None


@pytest.mark.parametrize("regime", [AmortizationType.price, AmortizationType.sac])
def test_totals_consistent_with_schedule(regime):
    result = simulate_loan(
        principal=25_000,
        annual_interest_rate=7,
        years=5,
        funding_cost_rate=3,
        amortization=regime,
        include_schedule=True,
    )
    assert result.schedule is not None
    sum_interest = sum(e.interest for e in result.schedule)
    sum_funding = sum(e.funding_cost for e in result.schedule)
    sum_payment = sum(e.payment for e in result.schedule)
    assert math.isclose(sum_interest, result.interest_income, abs_tol=0.5)
    assert math.isclose(sum_funding, result.funding_cost, abs_tol=0.5)
    assert math.isclose(sum_payment, result.total_repayments, abs_tol=0.5)


@pytest.mark.parametrize("regime", [AmortizationType.price, AmortizationType.sac])
def test_funding_equal_to_interest_yields_zero_nii(regime):
    result = simulate_loan(
        principal=50_000,
        annual_interest_rate=5,
        years=10,
        funding_cost_rate=5,
        amortization=regime,
    )
    assert result.net_interest_income == pytest.approx(0.0, abs=0.01)
