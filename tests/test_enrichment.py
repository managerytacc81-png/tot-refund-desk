"""
Unit tests for STRO matcher, rate engine, and suspicion scoring.
"""

import pytest
from totrefund.enrichment.stro_matcher import STROMatcher
from totrefund.enrichment.rate_engine import RateEngine
from totrefund.enrichment.suspicion_scorer import SuspicionScorer


def test_stro_address_normalization():
    matcher = STROMatcher(stro_path="/nonexistent")
    assert matcher.normalize_address("805 Brighton Ct., San Diego, CA 92109") == "805 BRIGHTON CT SAN DIEGO CA 92109"
    assert matcher.normalize_address("3443 Ocean Front Walk, Unit I") == "3443 OCEAN FRONT WALK UNIT I"
    assert matcher.normalize_address("123 Main Street") == "123 MAIN ST"


def test_rate_engine_san_diego():
    # Coastal high impact (Mission Beach / Pacific Beach / La Jolla)
    rate, label = RateEngine.resolve_rate("San Diego", planning_area="MISSION BEACH", tier="Tier 4")
    assert rate == 0.1375
    assert "13.75%" in label

    # Urban mid impact
    rate_mid, label_mid = RateEngine.resolve_rate("San Diego", planning_area="UPTOWN", tier="Tier 3")
    assert rate_mid == 0.1250

    # General residential / Tier 2
    rate_res, label_res = RateEngine.resolve_rate("San Diego", planning_area="MIRA MESA", tier="Tier 2")
    assert rate_res == 0.1175


def test_rate_engine_other_jurisdictions():
    rate_la, _ = RateEngine.resolve_rate("Los Angeles County")
    assert rate_la == 0.14

    rate_sf, _ = RateEngine.resolve_rate("San Francisco")
    assert rate_sf == 0.14

    rate_sonoma, _ = RateEngine.resolve_rate("Sonoma County")
    assert rate_sonoma == 0.12


def test_rate_engine_gross_estimation():
    # Tier 4 Mission Beach
    gross_t4 = RateEngine.estimate_annual_gross(tier="Tier 4", planning_area="MISSION BEACH")
    assert gross_t4 == 145000.0

    # Coastal Tier 3
    gross_t3 = RateEngine.estimate_annual_gross(tier="Tier 3", planning_area="LA JOLLA")
    assert gross_t3 == 125000.0

    # Tier 2
    gross_t2 = RateEngine.estimate_annual_gross(tier="Tier 2")
    assert gross_t2 == 55000.0


def test_suspicion_scorer_pre_vca_multi_unit():
    # Certificate created in 2008 (pre-2015 VCA), 91 properties managed, Tier 4 Mission Beach
    score, reasons = SuspicionScorer.calculate_score(
        date_created="2008-04-18",
        jurisdiction="City of San Diego",
        operator_property_count=91,
        tier="Tier 4",
        planning_area="MISSION BEACH",
        is_stro_active=True
    )
    assert score == 99.0  # Capped at 99.0
    assert any("predates Airbnb" in r for r in reasons)
    assert any("property manager" in r for r in reasons)
    assert any("TIER 4" in r or "Tier 4" in r for r in reasons)



def test_suspicion_scorer_recent_single_unit():
    # Certificate created in 2024, 1 property
    score, reasons = SuspicionScorer.calculate_score(
        date_created="2024-06-01",
        jurisdiction="City of San Diego",
        operator_property_count=1,
        tier="Tier 2",
        planning_area="CLAIREMONT MESA"
    )
    assert score < 30.0
