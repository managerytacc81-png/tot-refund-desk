"""
Unit tests for packet generator and executive outreach letter creation.
"""

import pytest
from totrefund.models import EnrichedLead, RefundClaimMath
from totrefund.packet.generator import PacketGenerator


@pytest.fixture
def sample_lead():
    math = RefundClaimMath(
        certificate_no="518999",
        estimated_annual_gross=145000.0,
        tot_rate=0.1375,
        rate_label="13.75% Coastal Zoned TOT",
        estimated_annual_tot=19937.50,
        lookback_years=3.0,
        total_estimated_overpayment=59812.50,
        contingency_rate=0.25,
        contingency_fee=14953.12,
        net_owner_recovery=44859.38
    )
    return EnrichedLead(
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
        zone_rate_label="13.75% Coastal Zoned TOT",
        estimated_annual_gross=145000.0,
        estimated_annual_tot=19937.50,
        double_pay_suspicion_score=99.0,
        claim_form_url="https://www.sandiego.gov/treasurer/taxesfees/tot",
        statutory_reference="San Diego Municipal Code § 35.0114",
        stro_license_id="STR-01234L",
        tier="Tier 4",
        planning_area="MISSION BEACH",
        property_manager="Coast Vacation Homes",
        operator_property_count=91,
        suspicion_reasons=["Registered prior to Airbnb VCA", "91 managed units"],
        claim_math=math
    )


def test_packet_generator_structure(sample_lead):
    packet = PacketGenerator.generate_packet(sample_lead)
    assert packet["certificate_no"] == "518999"
    assert packet["total_estimated_overpayment"] == 59812.50
    assert packet["contingency_fee"] == 14953.12
    assert packet["net_owner_recovery"] == 44859.38
    assert "Deanna Thomason" in packet["outreach_letter"]
    assert "Coast Vacation Homes" in packet["email_subject"]
    assert "59,812.50" in packet["email_subject"]
    assert "mailto:" in packet["mailto_link"]
    assert "stay@coastvacations.com" in packet["mailto_link"]


def test_packet_claim_document_contents(sample_lead):
    doc = PacketGenerator.generate_claim_document(sample_lead)
    assert "CLAIM FOR REFUND" in doc
    assert "San Diego Municipal Code § 35.0114" in doc
    assert "743 SAN FERNANDO PL" in doc
    assert "59,812.50" in doc
    assert "penalty of perjury" in doc
