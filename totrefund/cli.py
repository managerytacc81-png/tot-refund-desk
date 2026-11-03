"""
CLI interface for the TOT Double-Payment Refund Desk pipeline.
"""

import argparse
import sys
from totrefund.pipeline import TOTRefundPipeline
from totrefund.adapters.san_diego import SanDiegoTreasurerAdapter
from totrefund.adapters.la_county import LACountyTTCAdapter
from totrefund.adapters.san_francisco import SFTreasurerAdapter
from totrefund.adapters.sonoma import SonomaACTTCAdapter


def main():
    parser = argparse.ArgumentParser(
        description="Occupancy-Tax Double-Payment Refund Desk Pipeline (tot-refund-desk)"
    )
    parser.add_argument(
        "--jurisdiction",
        choices=["san_diego", "la_county", "san_francisco", "sonoma"],
        default="san_diego",
        help="Jurisdiction to process (default: san_diego)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Custom source file path for certificate registry"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="Number of top ranked leads to produce (default: 50)"
    )
    parser.add_argument(
        "--cpra",
        action="store_true",
        help="Print California Public Records Act (CPRA) letter template for the jurisdiction"
    )

    args = parser.parse_args()

    adapter_map = {
        "san_diego": SanDiegoTreasurerAdapter(),
        "la_county": LACountyTTCAdapter(),
        "san_francisco": SFTreasurerAdapter(),
        "sonoma": SonomaACTTCAdapter(),
    }
    adapter = adapter_map[args.jurisdiction]

    if args.cpra:
        print(adapter.open_records_template())
        return 0

    pipeline = TOTRefundPipeline(tot_adapter=adapter)
    leads = pipeline.run(cert_source=args.source, top_n=args.top)
    print(f"\n[SUCCESS] Successfully produced {len(leads)} ranked priority leads for {adapter.jurisdiction_name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
