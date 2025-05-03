from fastapi import APIRouter
from app.schemas.loan import LoanRequest, LoanResponse
from app.services.loan_calculator import calculate_loan_returns

router = APIRouter()

@router.post("/calculate-loan-returns", response_model=LoanResponse)
def calculate_loan(loan_request: LoanRequest):
    """
    Calculate the total repayments, interest income, funding cost, interest expense, net interest margin, and net interest income for the bank.
    """
    results = calculate_loan_returns(
        principal=loan_request.principal,
        annual_interest_rate=loan_request.annual_interest_rate,
        years=loan_request.years,
        funding_cost_rate=loan_request.funding_cost_rate
    )
    return LoanResponse(**results)