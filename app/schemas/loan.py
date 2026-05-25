from enum import Enum

from pydantic import BaseModel, Field


class AmortizationType(str, Enum):
    """Supported amortization regimes."""

    price = "price"  # French/Price system: constant total payment
    sac = "sac"      # Sistema de Amortização Constante: constant principal


class LoanRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan amount (principal)")
    annual_interest_rate: float = Field(
        ..., ge=0, lt=100, description="Annual interest rate in percent (0 allowed)"
    )
    years: int = Field(..., gt=0, le=100, description="Loan duration in years")
    funding_cost_rate: float = Field(
        ..., ge=0, lt=100, description="Funding cost rate in percent (0 allowed)"
    )
    amortization: AmortizationType = Field(
        AmortizationType.price, description="Amortization regime: 'price' or 'sac'"
    )


class AmortizationEntry(BaseModel):
    month: int
    payment: float
    interest: float
    principal: float
    funding_cost: float
    remaining_balance: float


class LoanResponse(BaseModel):
    principal: float
    amortization: AmortizationType
    first_payment: float
    last_payment: float
    total_repayments: float
    interest_income: float
    funding_cost: float
    net_interest_income: float
    net_interest_margin: float = Field(
        ..., description="Annualized NII / average outstanding balance"
    )
    schedule: list[AmortizationEntry] | None = None
