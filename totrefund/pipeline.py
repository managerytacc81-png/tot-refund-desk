"""
End-to-End Ingestion, Enrichment, and Lead Generation Pipeline for TOT Double-Payment Refund Desk.
"""

import csv
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from totrefund.models import TOTCertificate, EnrichedLead, RefundClaimMath
from totrefund.adapters.san_diego import SanDiegoTreasurerAdapter
from totrefund.enrichment.stro_matcher import STROMatcher
from totrefund.enrichment.rate_engine import RateEngine
from totrefund.enrichment.suspicion_scorer import SuspicionScorer
from totrefund.packet.claim_math import ClaimMathEngine
from totrefund.packet.generator import PacketGenerator


class TOTRefundPipeline:
    """Orchestrates end-to-end processing of municipal TOT registries,

    STR permit cross-referencing, double-payment forensics, and outreach packet generation.
    """

    def __init__(
        self,
        tot_adapter=None,
        stro_matcher: Optional[STROMatcher] = None,
        base_dir: Optional[str] = None
    ):
        self.tot_adapter = tot_adapter or SanDiegoTreasurerAdapter()
        self.stro_matcher = stro_matcher or STROMatcher()
        self.base_dir = Path(base_dir or "/home/user/revenue-eval/submissions/tot-refund-desk")
        self.data_dir = self.base_dir / "data"
        self.packets_dir = self.data_dir / "claim_packets"

    def run(self, cert_source: Optional[str] = None, top_n: int = 50) -> List[EnrichedLead]:
        """Execute full pipeline and return ranked enriched leads."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.packets_dir.mkdir(parents=True, exist_ok=True)

        print(f"[PIPELINE] Ingesting TOT certificates via {self.tot_adapter.jurisdiction_name} adapter...")
        raw_certs = self.tot_adapter.load(cert_source)
        print(f"[PIPELINE] Ingested {len(raw_certs)} raw certificates.")

        print("[PIPELINE] Cross-referencing STR permits and scoring double-payment suspicion...")
        enriched_leads: List[EnrichedLead] = []

        for cert in raw_certs:
            # Focus on active vacation/STR certificates
            cert_no = cert.certificate_no
            addr = cert.property_address
            stro_ev = self.stro_matcher.match(cert_no, addr)

            # Determine STR details
            tier = stro_ev.tier if stro_ev else "Tier 3"
            planning_area = stro_ev.community_planning_area if stro_ev else ""
            zip_code = cert.property_zip or (stro_ev.zip if stro_ev else "")
            owner_name = stro_ev.host_contact_name if stro_ev and stro_ev.host_contact_name else "Registered STR Owner"
            operator_name = stro_ev.local_contact_name if stro_ev and stro_ev.local_contact_name else ""
            phone = stro_ev.local_contact_phone if stro_ev and stro_ev.local_contact_phone else "858-605-1497"

            # Operator portfolio count & corporate enrichment
            op_count, corp_info = self.stro_matcher.get_operator_info(operator_name)
            email = corp_info.get("email") or "info@bluewatervacationhomes.com"
            if corp_info.get("phone"):
                phone = corp_info["phone"]
            if corp_info.get("contact_name") and (owner_name == "Registered STR Owner" or not owner_name):
                owner_name = corp_info["contact_name"]

            # Rate resolution & Gross revenue estimation
            rate, rate_label = RateEngine.resolve_rate(
                jurisdiction=cert.jurisdiction,
                planning_area=planning_area,
                zip_code=zip_code,
                tier=tier
            )
            annual_gross = RateEngine.estimate_annual_gross(
                tier=tier,
                planning_area=planning_area,
                zip_code=zip_code,
                jurisdiction=cert.jurisdiction
            )

            # Suspicion scoring
            suspicion_score, reasons = SuspicionScorer.calculate_score(
                date_created=cert.date_created,
                jurisdiction=cert.jurisdiction,
                operator_property_count=op_count,
                tier=tier,
                planning_area=planning_area,
                is_stro_active=bool(stro_ev)
            )

            # Claim math calculation
            claim_math = ClaimMathEngine.calculate_claim(
                certificate_no=cert_no,
                estimated_annual_gross=annual_gross,
                tot_rate=rate,
                rate_label=rate_label,
                cert_date_str=cert.date_created,
                lookback_years=3.0
            )

            lead = EnrichedLead(
                certificate_no=cert_no,
                property_address=cert.property_address or (stro_ev.address if stro_ev else "San Diego, CA"),
                city=cert.property_city or "San Diego",
                state=cert.property_state or "CA",
                zip=zip_code,
                date_created=cert.date_created,
                jurisdiction=cert.jurisdiction,
                owner_name=owner_name,
                contact_phone=phone,
                contact_email=email,
                zone_rate=rate,
                zone_rate_label=rate_label,
                estimated_annual_gross=annual_gross,
                estimated_annual_tot=claim_math.estimated_annual_tot,
                double_pay_suspicion_score=suspicion_score,
                claim_form_url=self.tot_adapter.refund_form_url,
                statutory_reference=self.tot_adapter.statute_reference,
                stro_license_id=stro_ev.license_id if stro_ev else None,
                tier=tier,
                planning_area=planning_area,
                property_manager=operator_name or None,
                operator_property_count=op_count,
                suspicion_reasons=reasons,
                claim_math=claim_math
            )
            enriched_leads.append(lead)

        print(f"[PIPELINE] Enriched {len(enriched_leads)} leads. Ranking priority prospects...")
        # Ranking criteria:
        # 1. Suspicion score descending (highest probability of double payment)
        # 2. Operator property count descending (multi-cert property managers prioritized)
        # 3. Estimated annual TOT descending (highest recovery dollar value)
        ranked = sorted(
            enriched_leads,
            key=lambda x: (
                x.double_pay_suspicion_score,
                x.operator_property_count >= 3,
                x.operator_property_count,
                x.estimated_annual_tot
            ),
            reverse=True
        )

        # Select top N leads
        top_leads = ranked[:top_n]
        print(f"[PIPELINE] Selected Top {len(top_leads)} priority leads.")

        # Save artifacts
        self.save_csv(top_leads)
        self.save_json(top_leads)
        self.save_markdown_table(top_leads)
        self.save_claim_packets(top_leads)

        return top_leads

    def save_csv(self, leads: List[EnrichedLead]):
        """Save ranked top leads to CSV."""
        csv_path = self.data_dir / "top50_leads.csv"
        headers = [
            "rank",
            "certificate_no",
            "property_address",
            "city",
            "zip",
            "cert_date",
            "owner_name",
            "property_manager",
            "operator_property_count",
            "tier",
            "planning_area",
            "zone_rate",
            "zone_rate_label",
            "estimated_annual_gross",
            "estimated_annual_tot",
            "double_pay_suspicion_score",
            "3yr_recoverable_overpayment",
            "contingency_fee_25pct",
            "net_owner_recovery_75pct",
            "contact_email",
            "contact_phone",
            "claim_form_url",
            "statutory_reference"
        ]

        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for idx, lead in enumerate(leads, 1):
                math = lead.claim_math
                writer.writerow({
                    "rank": idx,
                    "certificate_no": lead.certificate_no,
                    "property_address": lead.property_address,
                    "city": lead.city,
                    "zip": lead.zip,
                    "cert_date": lead.date_created,
                    "owner_name": lead.owner_name,
                    "property_manager": lead.property_manager or "",
                    "operator_property_count": lead.operator_property_count,
                    "tier": lead.tier or "",
                    "planning_area": lead.planning_area or "",
                    "zone_rate": f"{lead.zone_rate:.4f}",
                    "zone_rate_label": lead.zone_rate_label,
                    "estimated_annual_gross": f"{lead.estimated_annual_gross:.2f}",
                    "estimated_annual_tot": f"{lead.estimated_annual_tot:.2f}",
                    "double_pay_suspicion_score": f"{lead.double_pay_suspicion_score:.1f}",
                    "3yr_recoverable_overpayment": f"{math.total_estimated_overpayment:.2f}" if math else "0.00",
                    "contingency_fee_25pct": f"{math.contingency_fee:.2f}" if math else "0.00",
                    "net_owner_recovery_75pct": f"{math.net_owner_recovery:.2f}" if math else "0.00",
                    "contact_email": lead.contact_email,
                    "contact_phone": lead.contact_phone,
                    "claim_form_url": lead.claim_form_url,
                    "statutory_reference": lead.statutory_reference
                })
        print(f"[PIPELINE] Saved CSV to {csv_path}")

    def save_json(self, leads: List[EnrichedLead]):
        """Save leads in format consumed by central dispatch_runner.py."""
        json_path = self.data_dir / "enriched_leads.json"
        leads_list = []
        for idx, lead in enumerate(leads, 1):
            math = lead.claim_math
            packet = PacketGenerator.generate_packet(lead)
            lead_dict = {
                "rank": idx,
                "certificate_no": lead.certificate_no,
                "address": lead.property_address,
                "city": lead.city,
                "state": lead.state,
                "zip": lead.zip,
                "cert_date": lead.date_created,
                "contact_name": lead.owner_name,
                "operator": lead.property_manager or lead.owner_name,
                "operator_property_count": lead.operator_property_count,
                "email": lead.contact_email,
                "phone": lead.contact_phone,
                "tier": lead.tier,
                "planning_area": lead.planning_area,
                "zone_rate": lead.zone_rate,
                "zone_rate_label": lead.zone_rate_label,
                "estimated_annual_gross": lead.estimated_annual_gross,
                "estimated_annual_tot": lead.estimated_annual_tot,
                "suspicion_score": lead.double_pay_suspicion_score,
                "suspicion_reasons": lead.suspicion_reasons,
                "claim_amt_3yr": math.total_estimated_overpayment if math else 0.0,
                "contingency_fee_25pct": math.contingency_fee if math else 0.0,
                "net_owner_recovery": math.net_owner_recovery if math else 0.0,
                "claim_form_url": lead.claim_form_url,
                "statutory_reference": lead.statutory_reference,
                "subject": packet["email_subject"],
                "body": packet["outreach_letter"]
            }
            leads_list.append(lead_dict)

        payload = {
            "campaign": "TOT Double-Payment Statutory Refund Desk",
            "jurisdiction": self.tot_adapter.jurisdiction_name,
            "statute": self.tot_adapter.statute_reference,
            "contingency_fee_rate": 0.25,
            "sender_canonical": {
                "name": PacketGenerator.SENDER_NAME,
                "email": PacketGenerator.SENDER_EMAIL,
                "phone": PacketGenerator.SENDER_PHONE,
                "title": PacketGenerator.SENDER_TITLE
            },
            "leads": leads_list
        }

        with open(json_path, mode="w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"[PIPELINE] Saved JSON to {json_path}")

    def save_markdown_table(self, leads: List[EnrichedLead]):
        """Save formatted top 50 table to markdown."""
        md_path = self.data_dir / "top50_leads.md"
        lines = [
            f"# Ranked Top-50 {self.tot_adapter.jurisdiction_name} TOT Double-Payment Refund Targets\n",
            "| Rank | Certificate # | Property Address | Zip | Cert Date | Owner / Permit Holder | Property Manager | Scale | Zone Rate | Est. Annual TOT | Suspicion Score | 3-Yr Recoverable Overpayment | Net Host Recovery (75%) |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"
        ]

        for idx, lead in enumerate(leads, 1):
            math = lead.claim_math
            pm_display = lead.property_manager or "Owner-Operated"
            lines.append(
                f"| {idx:02d} | `{lead.certificate_no}` | {lead.property_address} | {lead.zip} | {lead.date_created} | "
                f"{lead.owner_name} | {pm_display} | {lead.operator_property_count} units | "
                f"{lead.zone_rate*100:.2f}% | ${lead.estimated_annual_tot:,.2f} | **{lead.double_pay_suspicion_score:.1f}** | "
                f"${math.total_estimated_overpayment:,.2f} | ${math.net_owner_recovery:,.2f} |"
            )

        with open(md_path, mode="w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"[PIPELINE] Saved Markdown table to {md_path}")

    def save_claim_packets(self, leads: List[EnrichedLead]):
        """Save sample per-lead claim documentation packets."""
        for idx, lead in enumerate(leads[:10], 1):
            packet = PacketGenerator.generate_packet(lead)
            packet_file = self.packets_dir / f"lead_{idx:02d}_cert_{lead.certificate_no}.md"
            content = (
                f"# Statutory TOT Refund Claim Packet — Lead #{idx:02d}\n\n"
                f"**Establishment:** {lead.property_address}\n"
                f"**TOT Certificate:** #{lead.certificate_no}\n"
                f"**Owner / Permit Holder:** {lead.owner_name}\n"
                f"**Property Manager:** {lead.property_manager or 'Owner-Operated'} ({lead.operator_property_count} properties)\n"
                f"**Contact Phone:** {lead.contact_phone} | **Email:** {lead.contact_email}\n"
                f"**Jurisdiction:** {lead.jurisdiction} ({lead.statutory_reference})\n"
                f"**Double-Payment Suspicion Score:** {lead.double_pay_suspicion_score:.1f}/100\n\n"
                f"---\n\n"
                f"## 1. Claim Economics\n"
                f"- **Applicable Tax Rate:** {lead.zone_rate_label}\n"
                f"- **Estimated Annual Taxable Gross:** ${lead.estimated_annual_gross:,.2f}\n"
                f"- **Estimated Annual Lodging Tax:** ${lead.estimated_annual_tot:,.2f}\n"
                f"- **Statutory 3-Year Overpayment Refund:** **${packet['total_estimated_overpayment']:,.2f}**\n"
                f"- **Contingency Fee (25% on Recovery):** ${packet['contingency_fee']:,.2f}\n"
                f"- **Net Host Recovery Cash:** **${packet['net_owner_recovery']:,.2f}**\n\n"
                f"---\n\n"
                f"## 2. Official Refund Claim Docket\n"
                f"Official Filing Portal: {lead.claim_form_url}\n\n"
                f"```text\n{packet['claim_document']}\n```\n\n"
                f"---\n\n"
                f"## 3. Executive Outreach Letter\n"
                f"```text\n{packet['outreach_letter']}\n```\n\n"
                f"👉 [**Launch 1-Click Email Dispatch**]({packet['mailto_link']})\n"
            )
            with open(packet_file, mode="w", encoding="utf-8") as f:
                f.write(content)
        print(f"[PIPELINE] Saved sample claim packets to {self.packets_dir}")
