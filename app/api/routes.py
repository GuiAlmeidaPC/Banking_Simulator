from fastapi import APIRouter, Query

from app.schemas.loan import LoanRequest, LoanResponse
from app.services.loan_calculator import simulate_loan

router = APIRouter()


@router.post("/calculate-loan-returns", response_model=LoanResponse)
def calculate_loan(
    loan_request: LoanRequest,
    include_schedule: bool = Query(False, description="Include month-by-month schedule"),
) -> LoanResponse:
    """Simulate a Price-amortized loan and return the bank's economics."""
    return simulate_loan(
        principal=loan_request.principal,
        annual_interest_rate=loan_request.annual_interest_rate,
        years=loan_request.years,
        funding_cost_rate=loan_request.funding_cost_rate,
        include_schedule=include_schedule,
    )
