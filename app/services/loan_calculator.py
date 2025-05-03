def calculate_loan_returns(principal: float, annual_interest_rate: float, years: int, funding_cost_rate: float) -> dict:
    """
    Calculate the total repayments, interest income, funding cost, net interest margin (NIM), and principal for an amortizing loan using the Price amortization table.

    - Total Repayments: The total amount the bank receives from the loan (principal + interest income).
    - Interest Income: The income generated from the loan's interest.
    - Funding Cost: The cost incurred by the bank to fund the loan.
    - Net Interest Margin (NIM): The difference between interest income and funding cost, divided by the principal.
    - Net Interest Income (NII): The difference between interest income and interest expense.
    """
    rate = annual_interest_rate / 100 / 12  # Monthly interest rate
    funding_rate = funding_cost_rate / 100 / 12  # Monthly funding cost rate
    months = years * 12  # Total number of payments

    # Calculate monthly payment using the Price amortization formula
    monthly_payment = principal * (rate * (1 + rate) ** months) / ((1 + rate) ** months - 1)

    # Initialize variables for calculations
    total_repayments = 0
    total_interest_income = 0
    total_funding_cost = 0
    remaining_principal = principal

    # Iterate over each month to calculate interest income, funding cost, and principal payments
    for _ in range(months):
        # Interest income for the month
        interest_income = remaining_principal * rate
        # Principal payment for the month
        principal_payment = monthly_payment - interest_income
        # Funding cost for the month
        funding_cost = remaining_principal * funding_rate

        # Update totals
        total_repayments += monthly_payment
        total_interest_income += interest_income
        total_funding_cost += funding_cost

        # Reduce the remaining principal
        remaining_principal -= principal_payment

    # Calculate net interest income (NII)
    net_interest_income = total_interest_income - total_funding_cost

    # Calculate net interest margin (NIM)
    net_interest_margin = net_interest_income / principal

    return {
        "principal": round(principal, 2),
        "total_repayments": round(total_repayments, 2),
        "interest_income": round(total_interest_income, 2),
        "funding_cost": round(total_funding_cost, 2),
        "interest_expense": round(total_funding_cost, 2),
        "net_interest_margin": round(net_interest_margin, 4),  # NIM as a ratio
        "net_interest_income": round(net_interest_income, 2)
    }