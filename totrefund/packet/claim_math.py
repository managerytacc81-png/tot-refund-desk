"""
Claim Math Engine for TOT Statutory Lookback Claims.
Calculates 3-year overpayment, 25% contingency fee, and net host recovery.
"""

from typing import Dict, List, Optional
from datetime import datetime
from totrefund.models import RefundClaimMath


class ClaimMathEngine:
    """Calculates financial claim values under the 3-year municipal lookback statute."""

    DEFAULT_LOOKBACK_YEARS = 3.0
    DEFAULT_CONTINGENCY_FEE_PCT = 0.25

    @classmethod
    def calculate_claim(
        cls,
        certificate_no: str,
        estimated_annual_gross: float,
        tot_rate: float,
        rate_label: str,
        cert_date_str: Optional[str] = None,
        lookback_years: float = 3.0
    ) -> RefundClaimMath:
        """Calculate single property 3-year refund claim economics."""
        # Calculate annual TOT
        annual_tot = round(estimated_annual_gross * tot_rate, 2)

        # Check if cert date is newer than 3 years
        effective_lookback = lookback_years
        if cert_date_str:
            try:
                cert_dt = datetime.strptime(cert_date_str.strip()[:10], "%Y-%m-%d")
                now_dt = datetime.now()
                years_active = (now_dt - cert_dt).days / 365.25
                if years_active < effective_lookback:
                    effective_lookback = max(0.5, round(years_active, 1))
            except Exception:
                pass

        total_overpayment = round(annual_tot * effective_lookback, 2)
        contingency_fee = round(total_overpayment * cls.DEFAULT_CONTINGENCY_FEE_PCT, 2)
        net_owner = round(total_overpayment - contingency_fee, 2)

        return RefundClaimMath(
            certificate_no=certificate_no,
            estimated_annual_gross=estimated_annual_gross,
            tot_rate=tot_rate,
            rate_label=rate_label,
            estimated_annual_tot=annual_tot,
            lookback_years=effective_lookback,
            total_estimated_overpayment=total_overpayment,
            contingency_rate=cls.DEFAULT_CONTINGENCY_FEE_PCT,
            contingency_fee=contingency_fee,
            net_owner_recovery=net_owner
        )

    @classmethod
    def aggregate_portfolio(
        cls,
        claims: List[RefundClaimMath]
    ) -> Dict[str, float]:
        """Aggregate financial totals across a property manager's multi-certificate portfolio."""
        total_annual_gross = sum(c.estimated_annual_gross for c in claims)
        total_annual_tot = sum(c.estimated_annual_tot for c in claims)
        total_overpayment = sum(c.total_estimated_overpayment for c in claims)
        contingency_fee = sum(c.contingency_fee for c in claims)
        net_owner = sum(c.net_owner_recovery for c in claims)

        return {
            "total_certificates": len(claims),
            "total_annual_gross": round(total_annual_gross, 2),
            "total_annual_tot": round(total_annual_tot, 2),
            "total_3yr_overpayment": round(total_overpayment, 2),
            "total_contingency_fee": round(contingency_fee, 2),
            "total_net_owner_recovery": round(net_owner, 2),
        }
