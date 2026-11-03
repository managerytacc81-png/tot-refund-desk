"""
Adapters for public municipal and county TOT registries.
"""

from totrefund.adapters.base import TOTRegistryAdapter
from totrefund.adapters.san_diego import SanDiegoTreasurerAdapter
from totrefund.adapters.la_county import LACountyTTCAdapter
from totrefund.adapters.san_francisco import SFTreasurerAdapter
from totrefund.adapters.sonoma import SonomaACTTCAdapter

__all__ = [
    "TOTRegistryAdapter",
    "SanDiegoTreasurerAdapter",
    "LACountyTTCAdapter",
    "SFTreasurerAdapter",
    "SonomaACTTCAdapter",
]
