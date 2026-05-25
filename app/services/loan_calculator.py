from app.schemas.loan import AmortizationEntry, AmortizationType, LoanResponse


def simulate_loan(
    principal: float,
    annual_interest_rate: float,
    years: int,
    funding_cost_rate: float,
    amortization: AmortizationType = AmortizationType.price,
    include_schedule: bool = False,
) -> LoanResponse:
    """Simulate an amortizing loan from the bank's perspective.

    Supports two amortization regimes:

    - **Price** (French): constant total monthly payment; interest portion
      shrinks and principal portion grows over time.
    - **SAC** (Sistema de Amortização Constante): constant principal portion
      each month; total payment is highest at month 1 and decreases linearly.

    NIM is annualized against the average outstanding balance.
    """
    months = years * 12
    rate = annual_interest_rate / 100 / 12
    funding_rate = funding_cost_rate / 100 / 12

    if amortization == AmortizationType.price:
        if rate == 0:
            level_payment = principal / months
        else:
            level_payment = principal * (rate * (1 + rate) ** months) / ((1 + rate) ** months - 1)
        constant_principal = None
    else:
        level_payment = None
        constant_principal = principal / months

    total_repayments = 0.0
    total_interest = 0.0
    total_funding = 0.0
    sum_outstanding = 0.0
    first_payment = 0.0
    last_payment = 0.0
    remaining = principal
    schedule: list[AmortizationEntry] | None = [] if include_schedule else None

    for m in range(1, months + 1):
        interest = remaining * rate
        if amortization == AmortizationType.price:
            payment = level_payment
            principal_payment = payment - interest
        else:
            principal_payment = constant_principal
            payment = principal_payment + interest

        funding_cost = remaining * funding_rate

        sum_outstanding += remaining
        total_repayments += payment
        total_interest += interest
        total_funding += funding_cost

        if m == 1:
            first_payment = payment
        if m == months:
            last_payment = payment

        remaining -= principal_payment
        if m == months:
            remaining = 0.0

        if schedule is not None:
            schedule.append(
                AmortizationEntry(
                    month=m,
                    payment=round(payment, 2),
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
        amortization=amortization,
        first_payment=round(first_payment, 2),
        last_payment=round(last_payment, 2),
        total_repayments=round(total_repayments, 2),
        interest_income=round(total_interest, 2),
        funding_cost=round(total_funding, 2),
        net_interest_income=round(net_interest_income, 2),
        net_interest_margin=round(nim, 6),
        schedule=schedule,
    )
