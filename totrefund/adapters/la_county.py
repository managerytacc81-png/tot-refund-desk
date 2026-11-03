"""
Los Angeles County Treasurer and Tax Collector (TTC) TOT Registry Adapter.
Statute: LA County Code § 4.72.310
Rate: 14% TOT
"""

import csv
import io
import os
from typing import List, Optional
from totrefund.adapters.base import TOTRegistryAdapter
from totrefund.models import TOTCertificate


class LACountyTTCAdapter(TOTRegistryAdapter):
    """Adapter for LA County Treasurer and Tax Collector TOT registry."""

    @property
    def jurisdiction_name(self) -> str:
        return "Los Angeles County"

    @property
    def statute_reference(self) -> str:
        return "Los Angeles County Code § 4.72.310 (3-Year Statutory Lookback)"

    @property
    def default_tot_rate(self) -> float:
        return 0.14  # 14% TOT in unincorporated LA County

    @property
    def refund_form_url(self) -> str:
        return "https://ttc.lacounty.gov/transient-occupancy-tax-tot/"

    @property
    def airbnb_vca_date(self) -> str:
        return "2016-02-01"

    def parse_csv_stream(self, stream) -> List[TOTCertificate]:
        """Parse open-records TTC export CSV format."""
        reader = csv.DictReader(stream)
        certificates: List[TOTCertificate] = []
        for row in reader:
            cert_no = str(row.get("certificate_no") or row.get("account_number") or row.get("tot_id") or "").strip()
            if not cert_no:
                continue

            cert = TOTCertificate(
                certificate_no=cert_no,
                status=str(row.get("status", "Active")).strip(),
                certificate_type=str(row.get("certificate_type") or row.get("category", "Short-Term Rental")).strip(),
                property_address=str(row.get("property_address") or row.get("address", "")).strip(),
                property_city=str(row.get("property_city") or row.get("city", "LOS ANGELES")).strip(),
                property_state=str(row.get("property_state", "CA")).strip(),
                property_zip=str(row.get("property_zip") or row.get("zip", "")).strip(),
                date_created=str(row.get("date_created") or row.get("issue_date", "")).strip(),
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
        """LA County TTC does not offer an unauthenticated daily bulk download API.

        Returns empty list indicating fallback to open-records CPRA request.
        """
        return []
