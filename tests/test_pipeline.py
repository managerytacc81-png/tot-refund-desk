"""
Integration tests for the end-to-end TOTRefundPipeline.
"""

import tempfile
import pytest
from pathlib import Path
from totrefund.pipeline import TOTRefundPipeline
from totrefund.adapters.san_diego import SanDiegoTreasurerAdapter
from totrefund.enrichment.stro_matcher import STROMatcher


def test_pipeline_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pipeline = TOTRefundPipeline(
            tot_adapter=SanDiegoTreasurerAdapter(),
            stro_matcher=STROMatcher(),
            base_dir=str(tmp_path)
        )

        leads = pipeline.run(top_n=10)
        assert len(leads) == 10
        assert (tmp_path / "data" / "top50_leads.csv").exists()
        assert (tmp_path / "data" / "enriched_leads.json").exists()
        assert (tmp_path / "data" / "top50_leads.md").exists()
        assert (tmp_path / "data" / "claim_packets").exists()

        # Check ranking order
        for i in range(len(leads) - 1):
            assert leads[i].double_pay_suspicion_score >= leads[i+1].double_pay_suspicion_score
