"""
Data models for Transient Occupancy Tax (TOT) Double-Payment Refund Desk.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class TOTCertificate:
    """Represents a public municipal/county TOT certificate or registration."""
    certificate_no: str
    status: str
    certificate_type: str
    property_address: str
    property_city: str
    property_state: str
    property_zip: str
    date_created: str
    jurisdiction: str = "San Diego"
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class STREvidence:
    """Represents public short-term rental permit / license evidence."""
    license_id: str
    address: str
    zip: str
    tier: str
    community_planning_area: str
    date_expiration: str
    rtax_no: str
    tot_no: str
    local_contact_name: str
    local_contact_phone: str
    host_contact_name: str
    council_district: str
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefundClaimMath:
    """Financial calculations for a 3-year statutory lookback TOT refund claim."""
    certificate_no: str
    estimated_annual_gross: float
    tot_rate: float
    rate_label: str
    estimated_annual_tot: float
    lookback_years: float = 3.0
    total_estimated_overpayment: float = 0.0
    contingency_rate: float = 0.25
    contingency_fee: float = 0.0
    net_owner_recovery: float = 0.0

    def __post_init__(self):
        if self.estimated_annual_tot == 0.0 and self.estimated_annual_gross > 0.0 and self.tot_rate > 0.0:
            self.estimated_annual_tot = round(self.estimated_annual_gross * self.tot_rate, 2)
        if self.total_estimated_overpayment == 0.0 and self.estimated_annual_tot > 0.0:
            self.total_estimated_overpayment = round(self.estimated_annual_tot * self.lookback_years, 2)
        if self.contingency_fee == 0.0 and self.total_estimated_overpayment > 0.0:
            self.contingency_fee = round(self.total_estimated_overpayment * self.contingency_rate, 2)
            self.net_owner_recovery = round(self.total_estimated_overpayment - self.contingency_fee, 2)


@dataclass
class EnrichedLead:
    """Enriched TOT refund lead with STR permit evidence and suspicion scoring."""
    certificate_no: str
    property_address: str
    city: str
    state: str
    zip: str
    date_created: str
    jurisdiction: str
    owner_name: str
    contact_phone: str
    contact_email: str
    zone_rate: float
    zone_rate_label: str
    estimated_annual_gross: float
    estimated_annual_tot: float
    double_pay_suspicion_score: float
    claim_form_url: str
    statutory_reference: str
    stro_license_id: Optional[str] = None
    tier: Optional[str] = None
    planning_area: Optional[str] = None
    property_manager: Optional[str] = None
    operator_property_count: int = 1
    suspicion_reasons: List[str] = field(default_factory=list)
    claim_math: Optional[RefundClaimMath] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert enriched lead to dictionary format."""
        return {
            "certificate_no": self.certificate_no,
            "property_address": self.property_address,
            "city": self.city,
            "state": self.state,
            "zip": self.zip,
            "date_created": self.date_created,
            "jurisdiction": self.jurisdiction,
            "owner_name": self.owner_name,
            "property_manager": self.property_manager,
            "operator_property_count": self.operator_property_count,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "stro_license_id": self.stro_license_id,
            "tier": self.tier,
            "planning_area": self.planning_area,
            "zone_rate": self.zone_rate,
            "zone_rate_label": self.zone_rate_label,
            "estimated_annual_gross": self.estimated_annual_gross,
            "estimated_annual_tot": self.estimated_annual_tot,
            "double_pay_suspicion_score": self.double_pay_suspicion_score,
            "suspicion_reasons": self.suspicion_reasons,
            "claim_form_url": self.claim_form_url,
            "statutory_reference": self.statutory_reference,
            "claim_math": {
                "estimated_annual_gross": self.claim_math.estimated_annual_gross if self.claim_math else 0.0,
                "tot_rate": self.claim_math.tot_rate if self.claim_math else 0.0,
                "rate_label": self.claim_math.rate_label if self.claim_math else "",
                "estimated_annual_tot": self.claim_math.estimated_annual_tot if self.claim_math else 0.0,
                "lookback_years": self.claim_math.lookback_years if self.claim_math else 3.0,
                "total_estimated_overpayment": self.claim_math.total_estimated_overpayment if self.claim_math else 0.0,
                "contingency_rate": self.claim_math.contingency_rate if self.claim_math else 0.25,
                "contingency_fee": self.claim_math.contingency_fee if self.claim_math else 0.0,
                "net_owner_recovery": self.claim_math.net_owner_recovery if self.claim_math else 0.0
            } if self.claim_math else None
        }
