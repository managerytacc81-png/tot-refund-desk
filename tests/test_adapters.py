"""
Unit tests for TOT registry adapters.
"""

import io
import pytest
from totrefund.adapters.san_diego import SanDiegoTreasurerAdapter
from totrefund.adapters.la_county import LACountyTTCAdapter
from totrefund.adapters.san_francisco import SFTreasurerAdapter
from totrefund.adapters.sonoma import SonomaACTTCAdapter


def test_san_diego_adapter_clean_cert():
    adapter = SanDiegoTreasurerAdapter()
    assert adapter.clean_cert_no("519340.0") == "519340"
    assert adapter.clean_cert_no("12345") == "12345"
    assert adapter.clean_cert_no("") == ""


def test_san_diego_adapter_parse_stream():
    adapter = SanDiegoTreasurerAdapter()
    sample_csv = io.StringIO(
        '"certificate_no","status","certificate_type","property_address","property_city","property_state","property_zip","date_created"\n'
        '"519340.0","1.0","7.0","805 BRIGHTON CT","SAN DIEGO","CA","92109","2008-04-18"\n'
    )
    records = adapter.parse_csv_stream(sample_csv)
    assert len(records) == 1
    assert records[0].certificate_no == "519340"
    assert records[0].property_address == "805 BRIGHTON CT"
    assert records[0].property_zip == "92109"
    assert records[0].jurisdiction == "City of San Diego"


def test_san_diego_adapter_properties():
    adapter = SanDiegoTreasurerAdapter()
    assert adapter.airbnb_vca_date == "2015-06-01"
    assert "35.0114" in adapter.statute_reference
    assert "sandiego.gov" in adapter.refund_form_url
    template = adapter.open_records_template()
    assert "CALIFORNIA PUBLIC RECORDS ACT" in template
    assert "City of San Diego" in template


def test_la_county_adapter():
    adapter = LACountyTTCAdapter()
    assert adapter.jurisdiction_name == "Los Angeles County"
    assert adapter.default_tot_rate == 0.14
    assert adapter.airbnb_vca_date == "2016-02-01"
    assert "4.72.310" in adapter.statute_reference

    sample_csv = io.StringIO(
        "certificate_no,status,category,address,city,zip,issue_date\n"
        "LA-9921,Active,Vacation Rental,1001 Canyon Rd,Malibu,90265,2015-01-10\n"
    )
    records = adapter.parse_csv_stream(sample_csv)
    assert len(records) == 1
    assert records[0].certificate_no == "LA-9921"
    assert records[0].property_city == "Malibu"


def test_san_francisco_adapter():
    adapter = SFTreasurerAdapter()
    assert adapter.jurisdiction_name == "City and County of San Francisco"
    assert adapter.default_tot_rate == 0.14
    assert adapter.airbnb_vca_date == "2014-10-01"
    assert "6.15-1" in adapter.statute_reference

    sample_csv = io.StringIO(
        "ban,status,street_address,source_zip,business_start_date\n"
        "SF-TOT-882,Active,450 Mission St,94105,2013-05-01\n"
    )
    records = adapter.parse_csv_stream(sample_csv)
    assert len(records) == 1
    assert records[0].certificate_no == "SF-TOT-882"
    assert records[0].property_city == "SAN FRANCISCO"


def test_sonoma_county_adapter():
    adapter = SonomaACTTCAdapter()
    assert adapter.jurisdiction_name == "Sonoma County"
    assert adapter.default_tot_rate == 0.12
    assert adapter.airbnb_vca_date == "2015-11-01"
    assert "12-19" in adapter.statute_reference

    sample_csv = io.StringIO(
        "tot_account,status,address,city,zip,registration_date\n"
        "SON-3312,Active,1200 Russian River Rd,Guerneville,95446,2014-08-15\n"
    )
    records = adapter.parse_csv_stream(sample_csv)
    assert len(records) == 1
    assert records[0].certificate_no == "SON-3312"
    assert records[0].property_city == "Guerneville"
