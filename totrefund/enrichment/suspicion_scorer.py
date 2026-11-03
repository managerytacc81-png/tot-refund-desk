"""
Double-Payment Suspicion Scoring Engine.
Identifies STR operators at highest risk of duplicate TOT remittance.
"""

from typing import List, Optional, Tuple


class SuspicionScorer:
    """Calculates double-payment suspicion score (0-100) based on statutory

    filing habits, platform remittance timeline, and portfolio scale.
    """

    AIRBNB_VCA_DATES = {
        "San Diego": "2015-06-01",
        "City of San Diego": "2015-06-01",
        "Los Angeles County": "2016-02-01",
        "City and County of San Francisco": "2014-10-01",
        "Sonoma County": "2015-11-01",
    }

    ZONE_RATE_CHANGE_DATE = "2025-05-01"

    @classmethod
    def calculate_score(
        cls,
        date_created: str,
        jurisdiction: str,
        operator_property_count: int = 1,
        tier: Optional[str] = None,
        planning_area: Optional[str] = None,
        is_stro_active: bool = True
    ) -> Tuple[float, List[str]]:
        """Score an operator's probability of paying TOT twice on platform bookings."""
        score = 0.0
        reasons: List[str] = []

        vca_date = cls.AIRBNB_VCA_DATES.get(jurisdiction, "2015-06-01")
        cert_date = (date_created or "").strip()

        # 1. Timeline relative to platform remittance agreement
        if cert_date and cert_date < vca_date:
            score += 40.0
            reasons.append(
                f"TOT certificate issued ({cert_date}) prior to platform remittance date ({vca_date}); "
                f"established quarterly municipal filing routine predates Airbnb tax collection"
            )
        elif cert_date and cert_date < "2020-01-01":
            score += 25.0
            reasons.append(
                f"Pre-2020 active registration ({cert_date}); multi-year direct filing history with City Treasurer"
            )
        elif cert_date and cert_date < "2023-01-01":
            score += 15.0
            reasons.append(f"Multi-year active TOT registration ({cert_date})")

        # 2. Portfolio scale / Property Management automation
        if operator_property_count >= 10:
            score += 25.0
            reasons.append(
                f"High-volume property manager ({operator_property_count} managed properties); "
                f"automated PMS bookkeeping routinely reports gross receipts and double-remits TOT"
            )
        elif operator_property_count >= 3:
            score += 20.0
            reasons.append(
                f"Multi-property operator ({operator_property_count} properties); commercial-scale filing risk"
            )

        # 3. Whole-Home STR status
        tier_upper = (tier or "").upper().strip()
        if tier_upper in {"TIER 4", "TIER 3"}:
            score += 15.0
            reasons.append(f"Whole-home short-term rental ({tier_upper}); high booking frequency across Airbnb/VRBO")
        elif tier_upper == "TIER 2":
            score += 8.0
            reasons.append("Active home-share permit (Tier 2)")

        # 4. Coastal / Tourist Density
        area_upper = (planning_area or "").upper().strip()
        if area_upper in {"MISSION BEACH", "PACIFIC BEACH", "LA JOLLA", "DOWNTOWN"}:
            score += 10.0
            reasons.append(f"Located in prime tourist corridor ({area_upper}); elevated annual gross lodging revenue")

        # 5. Zoned TOT rate change transition
        if cert_date and cert_date < cls.ZONE_RATE_CHANGE_DATE:
            score += 10.0
            reasons.append(
                f"Active across San Diego zoned TOT rate transition ({cls.ZONE_RATE_CHANGE_DATE}); "
                f"platform rate calculation discrepancies created host overpayment"
            )

        # Cap score at 99.0
        final_score = min(score, 99.0)
        return round(final_score, 1), reasons
