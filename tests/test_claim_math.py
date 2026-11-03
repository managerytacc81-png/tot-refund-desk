"""
Unit tests for claim math and multi-certificate portfolio aggregation.
"""

import pytest
from totrefund.packet.claim_math import ClaimMathEngine


def test_claim_math_engine_standard_3yr():
    math = ClaimMathEngine.calculate_claim(
        certificate_no="518999",
        estimated_annual_gross=145000.0,
        tot_rate=0.1375,
        rate_label="13.75% Coastal Zoned TOT",
        cert_date_str="2008-04-18",
        lookback_years=3.0
    )
    assert math.estimated_annual_tot == 19937.50
    assert math.lookback_years == 3.0
    assert math.total_estimated_overpayment == 59812.50
    assert math.contingency_fee == 14953.12
    assert math.net_owner_recovery == 44859.38


def test_claim_math_engine_portfolio_aggregation():
    claim1 = ClaimMathEngine.calculate_claim("518999", 100000.0, 0.125, "12.5%", "2010-01-01")
    claim2 = ClaimMathEngine.calculate_claim("519000", 120000.0, 0.125, "12.5%", "2012-01-01")

    agg = ClaimMathEngine.aggregate_portfolio([claim1, claim2])
    assert agg["total_certificates"] == 2
    assert agg["total_annual_gross"] == 220000.0
    assert agg["total_annual_tot"] == 27500.0
    assert agg["total_3yr_overpayment"] == 82500.0
    assert agg["total_contingency_fee"] == 20625.0
    assert agg["total_net_owner_recovery"] == 61875.0
