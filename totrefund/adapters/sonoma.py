"""
Sonoma County Auditor-Controller-Treasurer-Tax Collector (ACTTC) TOT Adapter.
Statute: Sonoma County Code § 12-19
Rate: 12% - 14% TOT
"""

import csv
import os
from typing import List, Optional
from totrefund.adapters.base import TOTRegistryAdapter
from totrefund.models import TOTCertificate


class SonomaACTTCAdapter(TOTRegistryAdapter):
    """Adapter for Sonoma County ACTTC transient occupancy tax registry.

    Note: Sonoma County audits established pervasive host double-payment
    because Airbnb began remitting on 2015-11-01 without providing itemized
    host-level breakdowns, causing hosts to remit identical tax twice.
    """

    @property
    def jurisdiction_name(self) -> str:
        return "Sonoma County"

    @property
    def statute_reference(self) -> str:
        return "Sonoma County Code § 12-19 (3-Year Statutory Lookback)"

    @property
    def default_tot_rate(self) -> float:
        return 0.12  # 12% TOT base, up to 14% with TID assessment

    @property
    def refund_form_url(self) -> str:
        return "https://sonomacounty.ca.gov/administrative-support-and-fiscal-services/auditor-controller-treasurer-tax-collector/divisions/tax-collector/transient-occupancy-tax"

    @property
    def airbnb_vca_date(self) -> str:
        return "2015-11-01"

    def parse_csv_stream(self, stream) -> List[TOTCertificate]:
        """Parse Sonoma County ACTTC operator list CSV format."""
        reader = csv.DictReader(stream)
        certificates: List[TOTCertificate] = []
        for row in reader:
            cert_no = str(row.get("certificate_no") or row.get("tot_account") or row.get("operator_id") or "").strip()
            if not cert_no:
                continue

            cert = TOTCertificate(
                certificate_no=cert_no,
                status=str(row.get("status", "Active")).strip(),
                certificate_type=str(row.get("certificate_type") or row.get("property_type", "Vacation Rental")).strip(),
                property_address=str(row.get("property_address") or row.get("address", "")).strip(),
                property_city=str(row.get("property_city") or row.get("city", "SANTA ROSA")).strip(),
                property_state="CA",
                property_zip=str(row.get("property_zip") or row.get("zip", "")).strip(),
                date_created=str(row.get("date_created") or row.get("registration_date", "")).strip(),
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
        """Sonoma County ACTTC registry live fetch fallback."""
        return []
