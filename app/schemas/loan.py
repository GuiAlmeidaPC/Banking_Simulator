from pydantic import BaseModel, Field

class LoanRequest(BaseModel):
    principal: float = Field(..., gt=0, description="The loan amount (principal)")
    annual_interest_rate: float = Field(..., gt=0, description="Annual interest rate in percentage")
    years: int = Field(..., gt=0, description="Loan duration in years")
    funding_cost_rate: float = Field(..., gt=0, description="Funding cost rate in percentage")

class LoanResponse(BaseModel):
    principal: float
    total_repayments: float
    interest_income: float
    funding_cost: float
    interest_expense: float
    net_interest_margin: float
    net_interest_income: float