"""
Occupancy-Tax Double-Payment Refund Desk (tot-refund-desk).
Statutory 3-year lookback recovery pipeline for STR hosts and property managers.
"""

from totrefund.models import TOTCertificate, STREvidence, RefundClaimMath, EnrichedLead
from totrefund.adapters.san_diego import SanDiegoTreasurerAdapter
from totrefund.adapters.la_county import LACountyTTCAdapter
from totrefund.adapters.san_francisco import SFTreasurerAdapter
from totrefund.adapters.sonoma import SonomaACTTCAdapter
from totrefund.enrichment.stro_matcher import STROMatcher
from totrefund.enrichment.rate_engine import RateEngine
from totrefund.enrichment.suspicion_scorer import SuspicionScorer
from totrefund.packet.claim_math import ClaimMathEngine
from totrefund.packet.generator import PacketGenerator
from totrefund.pipeline import TOTRefundPipeline

__version__ = "1.0.0"

__all__ = [
    "TOTCertificate",
    "STREvidence",
    "RefundClaimMath",
    "EnrichedLead",
    "SanDiegoTreasurerAdapter",
    "LACountyTTCAdapter",
    "SFTreasurerAdapter",
    "SonomaACTTCAdapter",
    "STROMatcher",
    "RateEngine",
    "SuspicionScorer",
    "ClaimMathEngine",
    "PacketGenerator",
    "TOTRefundPipeline",
]
