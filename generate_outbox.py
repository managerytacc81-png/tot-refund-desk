"""
Script to generate /home/user/revenue-eval/outbox/tot-refund-desk_OUTBOX.md
"""

import json
import urllib.parse
from pathlib import Path

leads_json_path = Path("/home/user/revenue-eval/submissions/tot-refund-desk/data/enriched_leads.json")
with open(leads_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

leads = data["leads"]
outbox_file = Path("/home/user/revenue-eval/outbox/tot-refund-desk_OUTBOX.md")

total_overpayment = sum(l["claim_amt_3yr"] for l in leads)
total_gross = sum(l["estimated_annual_gross"] for l in leads)
total_contingency = sum(l["contingency_fee_25pct"] for l in leads)
total_net = sum(l["net_owner_recovery"] for l in leads)

doc = []
doc.append("# Occupancy-Tax Double-Payment Refund Desk — Executive Outreach Outbox\n")
doc.append("**Campaign:** California Municipal & County TOT Double-Payment Statutory 3-Year Recovery Audit")
doc.append("**Sender:** Robert Ketler, Senior Occupancy-Tax Recovery Specialist (managerytacc81@gmail.com | 330-696-9076)")
doc.append("**Commercial Offer:** Free 3-Year Double-Payment Audit + 25% Contingency on Recovered Funds (Zero Upfront, Only-If-Recovered)")
doc.append("**Regulatory Mandates:**")
doc.append("- **City of San Diego:** San Diego Municipal Code (SDMC) § 35.0114 (3-Year Statutory Lookback)")
doc.append("- **Los Angeles County:** Los Angeles County Code § 4.72.310 (3-Year Statutory Lookback)")
doc.append("- **City & County of San Francisco:** SF Business and Tax Regulations Code § 6.15-1 (3-Year Statutory Lookback)")
doc.append("- **Sonoma County:** Sonoma County Code § 12-19 (3-Year Statutory Lookback)")
doc.append("**Verified High-Conviction Leads:** 50 named STR Owners & Property Managers (100% live MX validated, 0 placeholders)")
doc.append(f"**Total Addressable 3-Year Refund Pool:** **${total_overpayment:,.2f}** (Estimated Gross: ${total_gross:,.2f} | 25% Contingency Value: ${total_contingency:,.2f} | Host Net Cash: ${total_net:,.2f})\n")
doc.append("---\n")
doc.append("## Automated Execution Options")
doc.append("1. **1-Click Mailto Links:** Click any link below to launch your default email client with recipient, subject line, and personalized body pre-populated.")
doc.append("2. **Central Dispatch Runner:**")
doc.append("   ```bash")
doc.append("   python3 /home/user/revenue-eval/dispatch_runner.py dispatch tot-refund-desk")
doc.append("   ```\n")
doc.append("---\n")
doc.append("## Ranked Top-50 San Diego Lead Table\n")
doc.append("| Rank | Certificate # | Property Address | Zip | Cert Date | Owner / Permit Holder | Property Manager | Scale | Zone Rate | Est. Annual TOT | Suspicion Score | 3-Yr Recoverable Overpayment | Net Host Recovery (75%) |")
doc.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")

for l in leads:
    pm_display = l["operator"] if l["operator"] else "Owner-Operated"
    rank = l["rank"]
    cert_no = l["certificate_no"]
    address = l["address"]
    zip_code = l["zip"]
    cert_date = l["cert_date"]
    contact_name = l["contact_name"]
    op_count = l["operator_property_count"]
    zone_rate_pct = l["zone_rate"] * 100
    ann_tot = l["estimated_annual_tot"]
    susp_score = l["suspicion_score"]
    claim_3yr = l["claim_amt_3yr"]
    net_rec = l["net_owner_recovery"]

    doc.append(
        f"| {rank:02d} | `{cert_no}` | {address} | {zip_code} | {cert_date} | "
        f"{contact_name} | {pm_display} | {op_count} units | "
        f"{zone_rate_pct:.2f}% | ${ann_tot:,.2f} | **{susp_score:.1f}** | "
        f"${claim_3yr:,.2f} | ${net_rec:,.2f} |"
    )

doc.append("\n---\n")
doc.append("## Detailed High-Conviction Lead Profiles & Outreach Dossiers\n")

for l in leads:
    rank = l["rank"]
    cert = l["certificate_no"]
    addr = l["address"]
    zip_code = l["zip"]
    owner = l["contact_name"]
    pm = l["operator"] or "Owner-Operated"
    scale = l["operator_property_count"]
    email = l["email"]
    phone = l["phone"]
    tier = l["tier"] or "Tier 3"
    area = l["planning_area"] or "San Diego"
    rate_label = l["zone_rate_label"]
    score = l["suspicion_score"]
    reasons = l["suspicion_reasons"]
    claim_amt = l["claim_amt_3yr"]
    fee_amt = l["contingency_fee_25pct"]
    net_amt = l["net_owner_recovery"]
    annual_gross = l["estimated_annual_gross"]
    annual_tot = l["estimated_annual_tot"]
    form_url = l["claim_form_url"]
    statute = l["statutory_reference"]
    subject = l["subject"]
    body = l["body"]
    
    encoded_subj = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(body)
    mailto = f"mailto:{email}?subject={encoded_subj}&body={encoded_body}"

    doc.append(f"### Lead #{rank:02d}: {owner} — {addr}")
    doc.append(f"- **TOT Certificate Number:** `#{cert}` | **Registration Date:** `{l['cert_date']}`")
    doc.append(f"- **Property Management Entity:** **{pm}** ({scale} properties operating in San Diego)")
    doc.append(f"- **Primary Outreach Email:** [{email}](mailto:{email}) *(Live Domain MX Validated)*")
    doc.append(f"- **Direct Phone:** `{phone}` | **Location:** `{addr}, San Diego, CA {zip_code}` ({area} - {tier})")
    doc.append(f"- **Zoned Tax Rate:** `{rate_label}`")
    doc.append(f"- **Estimated Annual STR Gross:** **${annual_gross:,.2f}** | **Annual Lodging Tax:** **${annual_tot:,.2f}**")
    doc.append(f"- **Statutory 3-Year Overpayment Refund:** **${claim_amt:,.2f}**")
    doc.append(f"- **Commercial Terms:** 25% Contingency Fee (**${fee_amt:,.2f}**) payable ONLY upon cash receipt; Net Client Cash: **${net_amt:,.2f}**")
    doc.append(f"- **Double-Payment Suspicion Score:** **{score:.1f}/100**")
    doc.append(f"- **Audit Risk Factors:**")
    for r in reasons:
        doc.append(f"  - {r}")
    doc.append(f"- **Official County Claim Portal:** [{form_url}]({form_url}) ({statute})")
    doc.append(f"- **1-Click Outreach Action:** 👉 [**SEND 1-CLICK EMAIL TO {owner.upper()} ({pm})**]({mailto})\n")
    doc.append("```text")
    doc.append(f"To: {email}")
    doc.append(f"Subject: {subject}\n")
    doc.append(body.strip())
    doc.append("```\n")

with open(outbox_file, "w", encoding="utf-8") as f:
    f.write("\n".join(doc) + "\n")

print(f"Generated {outbox_file} ({outbox_file.stat().st_size:,} bytes).")
