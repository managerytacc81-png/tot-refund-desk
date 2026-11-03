"""
Unit tests for data models.
"""

import pytest
from totrefund.models import TOTCertificate, STREvidence, RefundClaimMath, EnrichedLead


def test_tot_certificate_model():
    cert = TOTCertificate(
        certificate_no="519340",
        status="1.0",
        certificate_type="7.0",
        property_address="805 BRIGHTON CT",
        property_city="SAN DIEGO",
        property_state="CA",
        property_zip="92109",
        date_created="2008-04-18"
    )
    assert cert.certificate_no == "519340"
    assert cert.property_zip == "92109"
    assert cert.jurisdiction == "San Diego"


def test_str_evidence_model():
    ev = STREvidence(
        license_id="STR-01594L",
        address="3450 Dwight St",
        zip="92104",
        tier="Tier 2",
        community_planning_area="NORTH PARK",
        date_expiration="2027-04-30",
        rtax_no="2021528231",
        tot_no="644416",
        local_contact_name="Jason Goyanko",
        local_contact_phone="5714285354",
        host_contact_name="Jason Goyanko",
        council_district="3"
    )
    assert ev.license_id == "STR-01594L"
    assert ev.tier == "Tier 2"
    assert ev.community_planning_area == "NORTH PARK"


def test_refund_claim_math_auto_calculation():
    # 100k gross, 13.75% rate, 3 yr lookback
    math = RefundClaimMath(
        certificate_no="518999",
        estimated_annual_gross=100000.0,
        tot_rate=0.1375,
        rate_label="13.75% Coastal Zoned TOT",
        estimated_annual_tot=0.0
    )
    assert math.estimated_annual_tot == 13750.0
    assert math.total_estimated_overpayment == 41250.0  # 13750 * 3
    assert math.contingency_fee == 10312.50           # 41250 * 0.25
    assert math.net_owner_recovery == 30937.50        # 41250 * 0.75


def test_enriched_lead_serialization():
    math = RefundClaimMath(
        certificate_no="518999",
        estimated_annual_gross=145000.0,
        tot_rate=0.1375,
        rate_label="13.75% Coastal Zoned TOT",
        estimated_annual_tot=19937.50
    )
    lead = EnrichedLead(
        certificate_no="518999",
        property_address="743 SAN FERNANDO PL",
        city="San Diego",
        state="CA",
        zip="92109",
        date_created="2008-04-18",
        jurisdiction="City of San Diego",
        owner_name="Deanna Thomason",
        contact_phone="858-859-2001",
        contact_email="stay@coastvacations.com",
        zone_rate=0.1375,
        zone_rate_label="13.75% Coastal",
        estimated_annual_gross=145000.0,
        estimated_annual_tot=19937.50,
        double_pay_suspicion_score=99.0,
        claim_form_url="https://www.sandiego.gov/treasurer/taxesfees/tot",
        statutory_reference="SDMC § 35.0114",
        claim_math=math
    )
    data = lead.to_dict()
    assert data["certificate_no"] == "518999"
    assert data["double_pay_suspicion_score"] == 99.0
    assert data["claim_math"]["total_estimated_overpayment"] == 59812.50
    assert data["claim_math"]["contingency_fee"] == 14953.12
    assert data["claim_math"]["net_owner_recovery"] == 44859.38
