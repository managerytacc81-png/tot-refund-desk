"""
San Diego City Treasurer TOT Registry Adapter.
Endpoint: https://seshat.datasd.org/tot_establishments/tot_establishments_datasd.csv
"""

import csv
import io
import os
import urllib.request
from typing import List, Optional
from totrefund.adapters.base import TOTRegistryAdapter
from totrefund.models import TOTCertificate


class SanDiegoTreasurerAdapter(TOTRegistryAdapter):
    """Adapter for City of San Diego Office of the City Treasurer TOT registry."""

    DEFAULT_CACHE_PATH = "/home/user/revenue-eval/scratch/tot_establishments_sd.csv"
    LIVE_CSV_URL = "https://seshat.datasd.org/tot_establishments/tot_establishments_datasd.csv"

    @property
    def jurisdiction_name(self) -> str:
        return "City of San Diego"

    @property
    def statute_reference(self) -> str:
        return "San Diego Municipal Code (SDMC) § 35.0114 (3-Year Statutory Lookback)"

    @property
    def default_tot_rate(self) -> float:
        return 0.105  # Base 10.5%, plus TMD up to 13.75%

    @property
    def refund_form_url(self) -> str:
        return "https://www.sandiego.gov/treasurer/taxesfees/tot"

    @property
    def airbnb_vca_date(self) -> str:
        return "2015-06-01"

    def clean_cert_no(self, val: str) -> str:
        """Strip floating point notation from certificate numbers."""
        if not val:
            return ""
        val = str(val).strip()
        try:
            return str(int(float(val)))
        except (ValueError, TypeError):
            return val

    def parse_csv_stream(self, stream) -> List[TOTCertificate]:
        """Parse CSV rows into TOTCertificate models."""
        reader = csv.DictReader(stream)
        certificates: List[TOTCertificate] = []
        for row in reader:
            cert_no = self.clean_cert_no(row.get("certificate_no", ""))
            if not cert_no:
                continue

            cert = TOTCertificate(
                certificate_no=cert_no,
                status=str(row.get("status", "")).strip(),
                certificate_type=str(row.get("certificate_type", "")).strip(),
                property_address=str(row.get("property_address", "")).strip(),
                property_city=str(row.get("property_city", "SAN DIEGO")).strip(),
                property_state=str(row.get("property_state", "CA")).strip(),
                property_zip=str(row.get("property_zip", "")).strip(),
                date_created=str(row.get("date_created", "")).strip(),
                jurisdiction=self.jurisdiction_name,
                raw_data=row
            )
            certificates.append(cert)
        return certificates

    def load(self, source: Optional[str] = None) -> List[TOTCertificate]:
        """Load from local CSV path, falling back to cached scratch file."""
        path = source or self.DEFAULT_CACHE_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"TOT establishments file not found at {path}")

        with open(path, mode="r", encoding="utf-8-sig") as f:
            return self.parse_csv_stream(f)

    def fetch_live(self) -> List[TOTCertificate]:
        """Fetch live CSV from data.sandiego.gov endpoint."""
        req = urllib.request.Request(
            self.LIVE_CSV_URL,
            headers={"User-Agent": "Mozilla/5.0 (Autonomous-TOT-Auditor/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8-sig")
            return self.parse_csv_stream(io.StringIO(content))
