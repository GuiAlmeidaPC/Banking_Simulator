from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_calculate_loan_returns_basic():
    response = client.post(
        "/calculate-loan-returns",
        json={
            "principal": 100_000,
            "annual_interest_rate": 6,
            "years": 30,
            "funding_cost_rate": 2,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["principal"] == 100_000.0
    assert body["amortization"] == "price"
    assert body["interest_income"] > 0
    assert body["net_interest_income"] > 0
    assert body["schedule"] is None
    assert body["first_payment"] == body["last_payment"]  # Price is level


def test_calculate_loan_with_schedule_query_param():
    response = client.post(
        "/calculate-loan-returns?include_schedule=true",
        json={
            "principal": 10_000,
            "annual_interest_rate": 5,
            "years": 1,
            "funding_cost_rate": 1,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["schedule"] is not None
    assert len(body["schedule"]) == 12


def test_sac_via_api():
    response = client.post(
        "/calculate-loan-returns",
        json={
            "principal": 12_000,
            "annual_interest_rate": 12,
            "years": 1,
            "funding_cost_rate": 0,
            "amortization": "sac",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["amortization"] == "sac"
    assert body["first_payment"] == 1120.0
    assert body["last_payment"] == 1010.0
    assert body["interest_income"] == 780.0


def test_invalid_amortization_rejected():
    response = client.post(
        "/calculate-loan-returns",
        json={
            "principal": 1000,
            "annual_interest_rate": 5,
            "years": 1,
            "funding_cost_rate": 1,
            "amortization": "bogus",
        },
    )
    assert response.status_code == 422


def test_zero_rate_accepted():
    response = client.post(
        "/calculate-loan-returns",
        json={
            "principal": 1000,
            "annual_interest_rate": 0,
            "years": 1,
            "funding_cost_rate": 0,
        },
    )
    assert response.status_code == 200


def test_negative_principal_rejected():
    response = client.post(
        "/calculate-loan-returns",
        json={
            "principal": -100,
            "annual_interest_rate": 5,
            "years": 1,
            "funding_cost_rate": 1,
        },
    )
    assert response.status_code == 422
