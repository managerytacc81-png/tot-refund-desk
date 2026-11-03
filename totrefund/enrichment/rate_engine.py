"""
Zone Rate Engine and STR Gross Revenue Estimator.
Implements San Diego 11.75%-13.75% zoned rates, LA County 14%, and SF 14%.
"""

from typing import Optional, Tuple


class RateEngine:
    """Calculates municipal/county TOT rates and estimates annual STR gross booking receipts."""

    # San Diego high-impact coastal planning areas
    SD_COASTAL_HIGH_IMPACT = {
        "MISSION BEACH",
        "PACIFIC BEACH",
        "LA JOLLA",
        "DOWNTOWN",
        "CENTRE CITY",
        "GASLAMP",
    }

    SD_MID_IMPACT = {
        "OCEAN BEACH",
        "UPTOWN",
        "PENINSULA",
        "POINT LOMA",
        "NORTH PARK",
        "GREATER GOLDEN HILL",
    }

    # Coastal high-yield zip codes
    SD_COASTAL_ZIPS = {"92109", "92037", "92101", "92107", "92106"}

    @classmethod
    def resolve_rate(
        cls,
        jurisdiction: str,
        planning_area: Optional[str] = None,
        zip_code: Optional[str] = None,
        tier: Optional[str] = None
    ) -> Tuple[float, str]:
        """Resolve precise zoned TOT rate and descriptive label."""
        jurisdiction_norm = (jurisdiction or "").strip().lower()

        if "san diego" in jurisdiction_norm:
            area_upper = (planning_area or "").upper().strip()
            zip_clean = (zip_code or "").strip()[:5]
            tier_upper = (tier or "").upper().strip()

            # High-impact coastal tier 4 / tier 3
            if tier_upper == "TIER 4" or area_upper in cls.SD_COASTAL_HIGH_IMPACT or zip_clean in {"92109", "92037"}:
                return 0.1375, "13.75% (10.5% Base TOT + 2.0% TMD Cat A + 1.25% Coastal Zone)"

            # Mid-impact coastal/urban
            if area_upper in cls.SD_MID_IMPACT or zip_clean in cls.SD_COASTAL_ZIPS or tier_upper == "TIER 3":
                return 0.1250, "12.50% (10.5% Base TOT + 2.0% TMD Assessment)"

            # General residential / Tier 2
            return 0.1175, "11.75% (10.5% Base TOT + 1.25% TMD Surcharge)"

        elif "los angeles" in jurisdiction_norm or "la county" in jurisdiction_norm:
            return 0.1400, "14.00% (LA County Title 4 Unincorporated Lodging Tax)"

        elif "san francisco" in jurisdiction_norm:
            return 0.1400, "14.00% (SF TTX Transient Occupancy Tax)"

        elif "sonoma" in jurisdiction_norm:
            return 0.1200, "12.00% (Sonoma County Base TOT + TID Assessment)"

        # Default fallback
        return 0.1200, "12.00% Municipal Lodging Tax"

    @classmethod
    def estimate_annual_gross(
        cls,
        tier: Optional[str] = None,
        planning_area: Optional[str] = None,
        zip_code: Optional[str] = None,
        jurisdiction: str = "San Diego"
    ) -> float:
        """Estimate annual gross STR booking revenue based on permit tier, location, and ADR models."""
        area_upper = (planning_area or "").upper().strip()
        tier_upper = (tier or "").upper().strip()
        zip_clean = (zip_code or "").strip()[:5]

        # Tier 4: Mission Beach whole-home year round (highest ADR & occupancy)
        if tier_upper == "TIER 4" or area_upper == "MISSION BEACH":
            return 145000.0  # ~$430 ADR x 250 nights + cleaning

        # Coastal Tier 3: Pacific Beach, La Jolla whole home
        if area_upper in {"LA JOLLA", "PACIFIC BEACH"} or zip_clean in {"92037", "92109"}:
            return 125000.0  # ~$380 ADR x 245 nights

        # Urban Tier 3: Downtown, Uptown, Ocean Beach whole home
        if tier_upper == "TIER 3" or area_upper in cls.SD_MID_IMPACT or zip_clean in cls.SD_COASTAL_ZIPS:
            return 95000.0   # ~$300 ADR x 240 nights

        # Tier 2: Home sharing / partial residence
        if tier_upper == "TIER 2":
            return 55000.0   # ~$190 ADR x 220 nights

        # General baseline
        return 80000.0
