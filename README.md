# Banking Simulator API

A small FastAPI service that simulates the economics of an amortizing
(Price/French) loan from the bank's perspective: total repayments,
interest income, funding cost, net interest income (NII), and an
annualized net interest margin (NIM).

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Then open:

- http://localhost:8000/ — the simulator UI (form, metrics, amortization chart, schedule table).
- http://localhost:8000/docs — interactive Swagger UI for the API.

## Example

```bash
curl -X POST http://localhost:8000/calculate-loan-returns \
  -H 'Content-Type: application/json' \
  -d '{
    "principal": 100000,
    "annual_interest_rate": 6,
    "years": 30,
    "funding_cost_rate": 2
  }'
```

Add `?include_schedule=true` to also receive the month-by-month
amortization schedule.

## Test

```bash
pytest
```

## Notes on the math

- The schedule uses the standard Price amortization formula:
  `payment = P · r(1+r)ⁿ / ((1+r)ⁿ − 1)`.
- `interest_income` and `funding_cost` are accrued each month on the
  opening outstanding balance.
- `net_interest_income = interest_income − funding_cost`.
- `net_interest_margin` is annualized:
  `NIM = (NII / years) / average_outstanding_balance`.
- A 0% interest rate is supported (degenerate case: equal-principal
  payments).
