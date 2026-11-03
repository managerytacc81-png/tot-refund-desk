"""
Base Adapter interface for Municipal and County TOT Certificate Registries.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from totrefund.models import TOTCertificate


class TOTRegistryAdapter(ABC):
    """Abstract base class for public TOT registry ingestion adapters."""

    @property
    @abstractmethod
    def jurisdiction_name(self) -> str:
        """Name of the city or county jurisdiction."""
        pass

    @property
    @abstractmethod
    def statute_reference(self) -> str:
        """Municipal or county code governing TOT refund lookbacks."""
        pass

    @property
    @abstractmethod
    def default_tot_rate(self) -> float:
        """Standard TOT rate for this jurisdiction."""
        pass

    @property
    @abstractmethod
    def refund_form_url(self) -> str:
        """Official URL for submitting a TOT refund claim."""
        pass

    @property
    @abstractmethod
    def airbnb_vca_date(self) -> str:
        """Date when Airbnb began voluntary collection/remittance in this jurisdiction."""
        pass

    @abstractmethod
    def load(self, source: Optional[str] = None) -> List[TOTCertificate]:
        """Load records from a local file path or cache."""
        pass

    @abstractmethod
    def fetch_live(self) -> List[TOTCertificate]:
        """Fetch live records from the jurisdiction's public open-data endpoint."""
        pass

    def open_records_template(self) -> str:
        """Generate a California Public Records Act (CPRA) request letter template

        for open-records fallback when a bulk registry is not directly downloadable.
        """
        return (
            f"CALIFORNIA PUBLIC RECORDS ACT (CPRA) REQUEST - Gov. Code § 7920.000 et seq.\n"
            f"TO: Custodian of Records, {self.jurisdiction_name}\n"
            f"SUBJECT: Public Registry of Transient Occupancy Tax (TOT) Certificates & Registrations\n\n"
            f"Dear Public Records Officer,\n\n"
            f"Pursuant to the California Public Records Act (Gov. Code § 7920.000 et seq.) and Article I,\n"
            f"Section 3(b) of the California Constitution, I hereby request electronic access to and copies\n"
            f"of public records regarding active and historically registered Transient Occupancy Tax (TOT)\n"
            f"certificates within {self.jurisdiction_name}.\n\n"
            f"Specifically, I request a spreadsheet or delimited text export (CSV, TSV, or XLSX) containing:\n"
            f"1. Certificate / Registration Account Number\n"
            f"2. Business / Operator / Establishment Name\n"
            f"3. Property Street Address, City, State, and Zip Code\n"
            f"4. Certificate Issuance / Registration Date\n"
            f"5. Establishment Category (e.g., Short-Term Rental, Vacation Rental, Hotel, B&B)\n"
            f"6. Registration Status (Active, Inactive, Expired)\n\n"
            f"Please provide the records in their original machine-readable electronic format to\n"
            f"managerytacc81@gmail.com. If any portion of the requested records is exempt from disclosure,\n"
            f"please provide the non-exempt portions and cite the specific statutory exemption.\n\n"
            f"Thank you for your assistance.\n\n"
            f"Sincerely,\n"
            f"Robert Ketler\n"
            f"Occupancy-Tax Double-Payment Refund Desk\n"
            f"Email: managerytacc81@gmail.com | Phone: 330-696-9076\n"
        )
