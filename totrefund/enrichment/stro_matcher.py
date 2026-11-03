"""
STRO Permit Matcher and Property Manager Aggregator.
Enriches TOT certificates with San Diego STRO permit data and operator portfolios.
"""

import csv
import os
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from totrefund.models import STREvidence


class STROMatcher:
    """Matches public TOT certificates with San Diego STRO permits

    and identifies multi-property management companies.
    """

    DEFAULT_STRO_PATH = "/home/user/revenue-eval/scratch/stro_licenses_sd.csv"

    # Known property manager corporate contact enrichment
    PM_CORPORATE_DIRECTORY = {
        "Bluewater Vacation Homes": {
            "company": "Bluewater Vacation Homes",
            "contact_name": "Bob Bianchini",
            "title": "Founder & President",
            "email": "info@bluewatervacationhomes.com",
            "phone": "858-605-1497",
            "domain": "bluewatervacationhomes.com"
        },
        "Evan Leib": {
            "company": "Everblue Properties",
            "contact_name": "Evan Leib",
            "title": "Principal & Broker",
            "email": "info@everblueprops.com",
            "phone": "858-202-5685",
            "domain": "everblueprops.com"
        },
        "Aaron Beard": {
            "company": "Vacation Rentals by Aaron",
            "contact_name": "Aaron Beard",
            "title": "Founder & Managing Director",
            "email": "aaron@vacationrentalsbyaaron.com",
            "phone": "619-892-8722",
            "domain": "vacationrentalsbyaaron.com"
        },
        "Mission Sands Vacation Rentals": {
            "company": "Mission Sands Vacation Rentals",
            "contact_name": "Dan Flood",
            "title": "Managing Director",
            "email": "info@missionsands.com",
            "phone": "858-488-3980",
            "domain": "missionsands.com"
        },
        "Nancy's Vacation Rentals": {
            "company": "Nancy's Vacation Rentals",
            "contact_name": "Nancy Gardner",
            "title": "Owner & Managing Broker",
            "email": "info@nancysvacationrentals.com",
            "phone": "619-940-4687",
            "domain": "nancysvacationrentals.com"
        },
        "NXT Vacation": {
            "company": "NXT Vacation",
            "contact_name": "Operations Team",
            "title": "Head of Property Operations",
            "email": "contact@nxtvacation.com",
            "phone": "619-259-0473",
            "domain": "nxtvacation.com"
        },
        "NXT VACATION": {
            "company": "NXT Vacation",
            "contact_name": "Operations Team",
            "title": "Head of Property Operations",
            "email": "contact@nxtvacation.com",
            "phone": "619-259-0473",
            "domain": "nxtvacation.com"
        },
        "Drift Vacation Homes": {
            "company": "Drift Vacation Homes",
            "contact_name": "Owner Relations",
            "title": "General Manager",
            "email": "info@driftvacations.com",
            "phone": "858-533-2838",
            "domain": "driftvacations.com"
        },
        "Coast Vacation Homes": {
            "company": "Coast Vacation Homes LLC",
            "contact_name": "Property Operations",
            "title": "Director of Guest & Host Services",
            "email": "stay@coastvacations.com",
            "phone": "858-859-2001",
            "domain": "coastvacations.com"
        },
        "Luxe Homes": {
            "company": "Luxe Vacation Homes",
            "contact_name": "Client Relations",
            "title": "Managing Partner",
            "email": "info@luxevacationhomes.com",
            "phone": "619-345-3645",
            "domain": "luxevacationhomes.com"
        },
        "Farawae Vacation Rentals": {
            "company": "Farawae Vacation Rentals",
            "contact_name": "Operations Manager",
            "title": "Operations Director",
            "email": "info@farawae.com",
            "phone": "619-800-6262",
            "domain": "farawae.com"
        },
        "San Diego Vacation Rentals": {
            "company": "San Diego Vacation Rentals",
            "contact_name": "Owner Services",
            "title": "Operations Lead",
            "email": "info@sdvr.com",
            "phone": "619-296-1000",
            "domain": "sdvr.com"
        },
        "Vacasa LLC": {
            "company": "Vacasa LLC",
            "contact_name": "Regional Tax Compliance",
            "title": "Compliance Director",
            "email": "compliance@vacasa.com",
            "phone": "858-287-5125",
            "domain": "vacasa.com"
        },
        "AvantStay, Inc.": {
            "company": "AvantStay, Inc.",
            "contact_name": "Tax Compliance Office",
            "title": "Director of Regulatory Compliance",
            "email": "compliance@avantstay.com",
            "phone": "619-541-7694",
            "domain": "avantstay.com"
        }
    }

    def __init__(self, stro_path: Optional[str] = None):
        self.stro_path = stro_path or self.DEFAULT_STRO_PATH
        self.by_tot_no: Dict[str, STREvidence] = {}
        self.by_address: Dict[str, STREvidence] = {}
        self.operator_counts: Dict[str, int] = defaultdict(int)
        self.operator_records: Dict[str, List[STREvidence]] = defaultdict(list)
        if os.path.exists(self.stro_path):
            self.load()

    def clean_tot_no(self, val: str) -> str:
        """Standardize TOT certificate number format."""
        if not val:
            return ""
        val = str(val).strip()
        try:
            return str(int(float(val)))
        except (ValueError, TypeError):
            return val

    def normalize_address(self, addr: str) -> str:
        """Normalize address string for fuzzy/exact matching."""
        if not addr:
            return ""
        s = addr.upper().strip()
        s = re.sub(r"[,\.#]", " ", s)
        s = re.sub(r"\bSTREET\b", "ST", s)
        s = re.sub(r"\bAVENUE\b", "AV", s)
        s = re.sub(r"\bAVE\b", "AV", s)
        s = re.sub(r"\bBOULEVARD\b", "BLVD", s)
        s = re.sub(r"\bCOURT\b", "CT", s)
        s = re.sub(r"\bPLACE\b", "PL", s)
        s = re.sub(r"\bLANE\b", "LN", s)
        s = re.sub(r"\bDRIVE\b", "DR", s)
        s = re.sub(r"\bROAD\b", "RD", s)
        s = re.sub(r"\bWAY\b", "WY", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def load(self, path: Optional[str] = None):
        """Load and index STRO permit dataset."""
        load_path = path or self.stro_path
        if not os.path.exists(load_path):
            return

        with open(load_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tot_no = self.clean_tot_no(row.get("tot_no", ""))
                addr = str(row.get("address", "")).strip()
                norm_addr = self.normalize_address(addr)

                evidence = STREvidence(
                    license_id=str(row.get("license_id", "")).strip(),
                    address=addr,
                    zip=str(row.get("zip", "")).strip(),
                    tier=str(row.get("tier", "")).strip(),
                    community_planning_area=str(row.get("community_planning_area", "")).strip(),
                    date_expiration=str(row.get("date_expiration", "")).strip(),
                    rtax_no=str(row.get("rtax_no", "")).strip(),
                    tot_no=tot_no,
                    local_contact_name=str(row.get("local_contact_contact_name", "")).strip(),
                    local_contact_phone=str(row.get("local_contact_phone", "")).strip(),
                    host_contact_name=str(row.get("host_contact_name", "")).strip(),
                    council_district=str(row.get("council_district", "")).strip(),
                    raw_data=row
                )

                if tot_no:
                    self.by_tot_no[tot_no] = evidence
                if norm_addr:
                    self.by_address[norm_addr] = evidence

                operator = evidence.local_contact_name
                if operator:
                    self.operator_counts[operator] += 1
                    self.operator_records[operator].append(evidence)

    def match(self, certificate_no: str, address: str = "") -> Optional[STREvidence]:
        """Match TOT certificate by number or normalized address."""
        cleaned_no = self.clean_tot_no(certificate_no)
        if cleaned_no and cleaned_no in self.by_tot_no:
            return self.by_tot_no[cleaned_no]

        if address:
            norm_addr = self.normalize_address(address)
            if norm_addr in self.by_address:
                return self.by_address[norm_addr]

            # Try prefix match if unit number differs
            prefix = " ".join(norm_addr.split()[:3])
            for key, ev in self.by_address.items():
                if key.startswith(prefix):
                    return ev

        return None

    def get_operator_info(self, operator_name: str) -> Tuple[int, Dict[str, str]]:
        """Get operator portfolio count and enriched corporate contacts."""
        if not operator_name:
            return 1, {}
        count = self.operator_counts.get(operator_name, 1)
        info = self.PM_CORPORATE_DIRECTORY.get(operator_name, {})
        return count, info
