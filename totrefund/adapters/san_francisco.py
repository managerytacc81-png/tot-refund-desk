"""
San Francisco Office of the Treasurer & Tax Collector (TTX) TOT Adapter.
Statute: SF Business & Tax Regulations Code § 6.15-1
Rate: 14% TOT
"""

import csv
import os
from typing import List, Optional
from totrefund.adapters.base import TOTRegistryAdapter
from totrefund.models import TOTCertificate


class SFTreasurerAdapter(TOTRegistryAdapter):
    """Adapter for San Francisco Office of the Treasurer & Tax Collector TOT registry."""

    @property
    def jurisdiction_name(self) -> str:
        return "City and County of San Francisco"

    @property
    def statute_reference(self) -> str:
        return "San Francisco Business and Tax Regulations Code § 6.15-1 (3-Year Statutory Lookback)"

    @property
    def default_tot_rate(self) -> float:
        return 0.14  # 14% TOT in San Francisco

    @property
    def refund_form_url(self) -> str:
        return "https://sftreasurer.org/business/taxes-fees/transient-occupancy-tax-tot"

    @property
    def airbnb_vca_date(self) -> str:
        return "2014-10-01"

    def parse_csv_stream(self, stream) -> List[TOTCertificate]:
        """Parse SF TTX open data export CSV format."""
        reader = csv.DictReader(stream)
        certificates: List[TOTCertificate] = []
        for row in reader:
            cert_no = str(row.get("certificate_no") or row.get("ban") or row.get("business_account_number") or "").strip()
            if not cert_no:
                continue

            cert = TOTCertificate(
                certificate_no=cert_no,
                status=str(row.get("status", "Active")).strip(),
                certificate_type=str(row.get("certificate_type") or row.get("naics_code_description", "Hotel / STR")).strip(),
                property_address=str(row.get("property_address") or row.get("street_address", "")).strip(),
                property_city="SAN FRANCISCO",
                property_state="CA",
                property_zip=str(row.get("property_zip") or row.get("source_zip", "")).strip(),
                date_created=str(row.get("date_created") or row.get("business_start_date", "")).strip(),
                jurisdiction=self.jurisdiction_name,
                raw_data=row
            )
            certificates.append(cert)
        return certificates

    def load(self, source: Optional[str] = None) -> List[TOTCertificate]:
        """Load from local CSV export or open-records release."""
        if not source or not os.path.exists(source):
            return []
        with open(source, mode="r", encoding="utf-8-sig") as f:
            return self.parse_csv_stream(f)

    def fetch_live(self) -> List[TOTCertificate]:
        """SF Data portal fallback."""
        return []
