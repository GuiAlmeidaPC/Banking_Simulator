from app.schemas.loan import AmortizationEntry, LoanResponse


def simulate_loan(
    principal: float,
    annual_interest_rate: float,
    years: int,
    funding_cost_rate: float,
    include_schedule: bool = False,
) -> LoanResponse:
    """Simulate an amortizing (Price/French) loan from the bank's perspective.

    Returns totals and (optionally) the month-by-month schedule. NIM is
    annualized against the average outstanding balance — the standard
    industry definition.
    """
    months = years * 12
    rate = annual_interest_rate / 100 / 12
    funding_rate = funding_cost_rate / 100 / 12

    if rate == 0:
        monthly_payment = principal / months
    else:
        monthly_payment = principal * (rate * (1 + rate) ** months) / ((1 + rate) ** months - 1)

    total_repayments = 0.0
    total_interest = 0.0
    total_funding = 0.0
    sum_outstanding = 0.0
    remaining = principal
    schedule: list[AmortizationEntry] | None = [] if include_schedule else None

    for m in range(1, months + 1):
        interest = remaining * rate
        principal_payment = monthly_payment - interest
        funding_cost = remaining * funding_rate

        sum_outstanding += remaining
        total_repayments += monthly_payment
        total_interest += interest
        total_funding += funding_cost

        remaining -= principal_payment
        if m == months:
            # Eliminate floating-point residual on the last payment.
            remaining = 0.0

        if schedule is not None:
            schedule.append(
                AmortizationEntry(
                    month=m,
                    payment=round(monthly_payment, 2),
                    interest=round(interest, 2),
                    principal=round(principal_payment, 2),
                    funding_cost=round(funding_cost, 2),
                    remaining_balance=round(max(remaining, 0.0), 2),
                )
            )

    net_interest_income = total_interest - total_funding
    avg_outstanding = sum_outstanding / months
    nim = (net_interest_income / years) / avg_outstanding if avg_outstanding > 0 else 0.0

    return LoanResponse(
        principal=round(principal, 2),
        monthly_payment=round(monthly_payment, 2),
        total_repayments=round(total_repayments, 2),
        interest_income=round(total_interest, 2),
        funding_cost=round(total_funding, 2),
        net_interest_income=round(net_interest_income, 2),
        net_interest_margin=round(nim, 6),
        schedule=schedule,
    )
