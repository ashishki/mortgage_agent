# tests/test_extractor.py
import pytest
from modules.extractor import Extractor

@pytest.fixture
def extractor():
    # Configure a dummy lender with a single regex for StatementDate
    lenders_cfg = [{
        "name": "dummy",
        "regex_patterns": {
            "StatementDate": r"Statement Date[:\s]+(?P<value>\d{1,2}/\d{1,2}/\d{4})",
            "AmountPrincipal": r"Principal[:\s]+\$(?P<value>[\d,]+\.\d{2})",
        }
    }]
    llm_cfg = {"model": "gpt-4", "api_key": "test", "temperature": 0.0}
    return Extractor(lenders_cfg, llm_cfg)


def test_extract_with_regex_finds_fields(extractor):
    text = "Statement Date: 02/20/2025\nPrincipal: $2,500.00"
    res = extractor.extract_with_regex(text)
    assert res.get("StatementDate") == "02/20/2025"
    assert res.get("AmountPrincipal") == "2,500.00"


def test_needs_llm_when_missing_fields(extractor):
    # Only StatementDate present, Principal missing
    regex_res = {"StatementDate": "02/20/2025"}
    assert extractor._needs_llm(regex_res) is True


def test_no_llm_needed_when_all_present(extractor):
    regex_res = {"StatementDate": "02/20/2025", "AmountPrincipal": "2,500.00"}
    assert extractor._needs_llm(regex_res) is False


def test_merge_results_prefers_regex(extractor):
    regex = {"FieldA": "foo"}
    llm = {"FieldA": "bar", "FieldB": "baz"}
    merged = extractor.merge_results(regex, llm)
    assert merged["FieldA"] == "foo"
    assert merged["FieldB"] == "baz"


def test_extract_calls_llm_when_needed(monkeypatch, extractor):
    # Monkeypatch regex to return missing principal and llm to provide it
    monkeypatch.setattr(extractor, 'extract_with_regex', lambda t: {"StatementDate": "01/01/2025"})
    monkeypatch.setattr(extractor, 'extract_with_llm', lambda t: {"StatementDate": "01/01/2025", "AmountPrincipal": "500.00"})
    monkeypatch.setattr(extractor, '_needs_llm', lambda r: True)
    record = extractor.extract("dummy text")
    # Should include both fields
    assert record["StatementDate"] == "01/01/2025"
    assert record["AmountPrincipal"] == "500.00"


def test_extract_skips_llm_when_not_needed(monkeypatch, extractor):
    # Regex returns full set
    mock_res = {"StatementDate": "01/01/2025", "AmountPrincipal": "500.00"}
    monkeypatch.setattr(extractor, 'extract_with_regex', lambda t: mock_res)
    monkeypatch.setattr(extractor, 'extract_with_llm', lambda t: {"ShouldNot": "used"})
    monkeypatch.setattr(extractor, '_needs_llm', lambda r: False)
    record = extractor.extract("dummy text")
    # Should equal regex result
    assert record["StatementDate"] == "01/01/2025"
    assert record["AmountPrincipal"] == "500.00"
    assert "ShouldNot" not in record
