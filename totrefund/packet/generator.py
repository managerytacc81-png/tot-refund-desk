"""
Lead Packet and Claim Documentation Generator.
Produces claim math, county refund claim URLs, pre-drafted claim filings, and executive outreach letters.
"""

import urllib.parse
from typing import Dict, Any, Optional
from totrefund.models import EnrichedLead


class PacketGenerator:
    """Generates official refund packets, claim filings, and outreach materials."""

    SENDER_NAME = "Robert Ketler"
    SENDER_EMAIL = "managerytacc81@gmail.com"
    SENDER_PHONE = "330-696-9076"
    SENDER_TITLE = "Senior Occupancy-Tax Recovery Specialist"

    @classmethod
    def generate_packet(cls, lead: EnrichedLead) -> Dict[str, Any]:
        """Generate a complete per-lead claim and outreach packet."""
        math = lead.claim_math
        claim_amt = math.total_estimated_overpayment if math else 0.0
        fee_amt = math.contingency_fee if math else 0.0
        net_amt = math.net_owner_recovery if math else 0.0
        annual_tot = math.estimated_annual_tot if math else 0.0
        annual_gross = math.estimated_annual_gross if math else 0.0

        claim_doc = cls.generate_claim_document(lead)
        outreach_letter = cls.generate_outreach_letter(lead)
        email_subject = cls.generate_email_subject(lead)
        mailto_link = cls.generate_mailto_link(lead, email_subject, outreach_letter)

        return {
            "certificate_no": lead.certificate_no,
            "property_address": lead.property_address,
            "owner_name": lead.owner_name,
            "property_manager": lead.property_manager,
            "operator_property_count": lead.operator_property_count,
            "contact_email": lead.contact_email,
            "contact_phone": lead.contact_phone,
            "jurisdiction": lead.jurisdiction,
            "statutory_reference": lead.statutory_reference,
            "claim_form_url": lead.claim_form_url,
            "estimated_annual_gross": annual_gross,
            "zone_rate_label": lead.zone_rate_label,
            "estimated_annual_tot": annual_tot,
            "total_estimated_overpayment": claim_amt,
            "contingency_fee": fee_amt,
            "net_owner_recovery": net_amt,
            "double_pay_suspicion_score": lead.double_pay_suspicion_score,
            "suspicion_reasons": lead.suspicion_reasons,
            "email_subject": email_subject,
            "outreach_letter": outreach_letter,
            "claim_document": claim_doc,
            "mailto_link": mailto_link
        }

    @classmethod
    def generate_email_subject(cls, lead: EnrichedLead) -> str:
        """Generate an executive high-conviction email subject line."""
        target_entity = lead.property_manager or lead.owner_name or lead.property_address
        claim_amt = lead.claim_math.total_estimated_overpayment if lead.claim_math else 0.0
        return f"TOT Double-Payment Audit: {target_entity} (${claim_amt:,.2f} Estimated 3-Year Overpayment Recovery)"

    @classmethod
    def generate_outreach_letter(cls, lead: EnrichedLead) -> str:
        """Generate a personalized executive outreach letter with zero-upfront contingency hook."""
        salutation_name = lead.owner_name
        if lead.property_manager and lead.property_manager != lead.owner_name:
            salutation_name = f"{lead.owner_name} / {lead.property_manager} Management Team"

        math = lead.claim_math
        claim_amt = math.total_estimated_overpayment if math else 0.0
        annual_tot = math.estimated_annual_tot if math else 0.0
        annual_gross = math.estimated_annual_gross if math else 0.0
        net_amt = math.net_owner_recovery if math else 0.0

        pm_note = ""
        if lead.operator_property_count >= 3:
            pm_note = (
                f"\nBecause you manage a portfolio of {lead.operator_property_count} short-term rental properties in "
                f"{lead.jurisdiction}, your systematic double-remittance risk spans all active certificates, representing "
                f"a substantially larger multi-unit cash recovery pool.\n"
            )

        letter = (
            f"Dear {salutation_name},\n\n"
            f"I am contacting you regarding your Transient Occupancy Tax (TOT) registration for "
            f"{lead.property_address} (Certificate #{lead.certificate_no}) in {lead.jurisdiction}.\n\n"
            f"According to municipal records, your TOT certificate was registered on {lead.date_created}. "
            f"Following the implementation of marketplace voluntary collection agreements, major platforms "
            f"(Airbnb and VRBO) began collecting and remitting lodging taxes directly on short-term bookings. "
            f"However, municipal tax audits (including recent findings across California counties) confirm that "
            f"hundreds of operators continued to report total gross booking receipts on their municipal returns and "
            f"paid the {lead.zone_rate_label} lodging tax directly to the City/County Treasurer.\n\n"
            f"Because platforms remit anonymized lump-sum checks without per-host itemization, hosts routinely paid "
            f"lodging tax twice on the exact same revenue.\n{pm_note}\n"
            f"PRELIMINARY 3-YEAR DOUBLE-PAYMENT AUDIT SUMMARY:\n"
            f"• Property Address: {lead.property_address}, {lead.city}, {lead.state} {lead.zip}\n"
            f"• TOT Certificate / STRO Permit: #{lead.certificate_no} | {lead.stro_license_id or 'Active'}\n"
            f"• Applicable Tax Rate: {lead.zone_rate_label}\n"
            f"• Estimated Annual Gross Receipts: ${annual_gross:,.2f}\n"
            f"• Estimated Annual Municipal TOT: ${annual_tot:,.2f}\n"
            f"• Statutory 3-Year Recoverable Overpayment: ${claim_amt:,.2f}\n"
            f"• Net Host Recovery (after 25% contingency): ${net_amt:,.2f}\n\n"
            f"CRITICAL DEADLINE URGENCY:\n"
            f"Under {lead.statutory_reference}, taxpayers are legally entitled to a full cash refund of erroneously "
            f"collected or double-paid TOT. However, claims are governed by a strict, rolling 3-year statute of limitations. "
            f"With each passing quarter, older overpayments expire permanently and become unrecoverable.\n\n"
            f"OUR COMMERCIAL ENGAGEMENT:\n"
            f"We provide a 100% turnkey, risk-free audit desk:\n"
            f"1. Zero Upfront Fees: We reconcile your platform payout reports against official municipal filing dockets at zero initial cost.\n"
            f"2. Pre-Drafted Claim Packet: We assemble the formal verified claim docket and submit directly under {lead.statutory_reference}.\n"
            f"3. 25% Contingency Only: You pay only 25% of the cash refund successfully recovered and received from the Treasurer; if there is no recovery, you owe nothing.\n\n"
            f"To review your pre-drafted claim packet or authorize our desk to begin your platform reconciliation, please reply directly to this email or call our desk at {cls.SENDER_PHONE}.\n\n"
            f"Best regards,\n\n"
            f"{cls.SENDER_NAME}\n"
            f"{cls.SENDER_TITLE}\n"
            f"Occupancy-Tax Double-Payment Refund Desk\n"
            f"Email: {cls.SENDER_EMAIL} | Direct: {cls.SENDER_PHONE}\n"
        )
        return letter

    @classmethod
    def generate_claim_document(cls, lead: EnrichedLead) -> str:
        """Generate a formal pre-drafted municipal refund claim filing document."""
        math = lead.claim_math
        claim_amt = math.total_estimated_overpayment if math else 0.0
        annual_tot = math.estimated_annual_tot if math else 0.0
        annual_gross = math.estimated_annual_gross if math else 0.0

        doc = (
            f"================================================================================\n"
            f"CLAIM FOR REFUND OF ERRONEOUSLY / DOUBLE-PAID TRANSIENT OCCUPANCY TAX\n"
            f"Pursuant to {lead.statutory_reference}\n"
            f"================================================================================\n\n"
            f"FILING AGENCY: {lead.jurisdiction} Office of the Treasurer / Tax Collector\n"
            f"OFFICIAL CLAIM FORM PORTAL: {lead.claim_form_url}\n\n"
            f"1. CLAIMANT INFORMATION\n"
            f"   Claimant Name / Entity: {lead.owner_name}\n"
            f"   Designated Representative: {lead.property_manager or lead.owner_name}\n"
            f"   Establishment Address: {lead.property_address}, {lead.city}, {lead.state} {lead.zip}\n"
            f"   TOT Certificate Number: {lead.certificate_no}\n"
            f"   STRO License / Registration: {lead.stro_license_id or 'Active'}\n"
            f"   Contact Phone: {lead.contact_phone}\n"
            f"   Contact Email: {lead.contact_email}\n\n"
            f"2. STATUTORY BASIS OF CLAIM\n"
            f"   This claim is timely submitted pursuant to {lead.statutory_reference}, providing that\n"
            f"   any tax, interest, or penalty erroneously, illegally, or redundantly collected or\n"
            f"   received by the Treasurer shall be refunded upon filing a verified claim within three\n"
            f"   (3) years from the date of payment.\n\n"
            f"3. FACTUAL STATEMENT OF DOUBLE-PAYMENT & GROSS OVERPAYMENT\n"
            f"   a. During the 36-month statutory lookback period, Claimant operated an active short-term\n"
            f"      rental at the subject property listed on online hosting platforms (including Airbnb and VRBO).\n"
            f"   b. Pursuant to applicable marketplace collection agreements, hosting platforms collected\n"
            f"      applicable Transient Occupancy Tax directly from guests and remitted bulk tax payments\n"
            f"      to {lead.jurisdiction}.\n"
            f"   c. Concurrently, Claimant filed periodic municipal TOT returns and remitted payment directly\n"
            f"      from host payouts, resulting in duplicate tax remittance on identical gross receipts.\n"
            f"   d. Furthermore, platform rate errors during local zone rate restructuring (effective\n"
            f"      May 1, 2025) caused misallocation of TMD and coastal zone rates, compounding the overpayment.\n\n"
            f"4. ACCOUNTING & COMPUTATION OF REFUND DEMAND\n"
            f"   • Applicable Combined Tax Rate: {lead.zone_rate_label}\n"
            f"   • Baseline Annual Taxable Gross Receipts: ${annual_gross:,.2f}\n"
            f"   • Annual Overpaid Lodging Tax: ${annual_tot:,.2f}\n"
            f"   • Statutory 3-Year Refund Demand Total: ${claim_amt:,.2f}\n\n"
            f"5. VERIFICATION & ATTESTATION\n"
            f"   Claimant hereby certifies under penalty of perjury under the laws of the State of\n"
            f"   California that the foregoing statements are true and correct, and requests the issuance\n"
            f"   of a warrant in the amount of ${claim_amt:,.2f} payable to Claimant.\n\n"
            f"DATED: ________________________        CLAIMANT: _____________________________________\n"
            f"                                                 Authorized Signature / Title\n"
        )
        return doc

    @classmethod
    def generate_mailto_link(cls, lead: EnrichedLead, subject: str, body: str) -> str:
        """Create URL-encoded mailto action link for 1-click dispatch."""
        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(body)
        return f"mailto:{lead.contact_email}?subject={encoded_subject}&body={encoded_body}"
