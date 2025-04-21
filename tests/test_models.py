# tests/test_models.py
import pytest
from modules.models import StatementRecord
from datetime import date


def test_statement_record_fields_parsing():
    """
    Verify that all fields are correctly parsed and normalized:
    - Dates → datetime.date
    - Amounts and rates → float
    - String values passed unchanged
    """
    raw = {
        "StatementFileName": "stmt1.pdf",
        "StatementDate": "01/15/2025",
        "MostRecentPaymentAmount": "$1,234.56",
        "AmountPrincipal": "2,000.00",
        "AmountInterest": "150.50",
        "AmountTaxInsurance": "$75.25",
        "AmountUnpaidBalance": "10,000.00",
        "AmountInterestRate": "3.75%",
        "PastDueAmount": "$200.00",
        "LinkToStatement": "https://drive.google.com/file/d/ABC123/view",
        "PropertyAddress": "123 Main St, Anytown, USA",
    }

    rec = StatementRecord(**raw)

    assert rec.StatementFileName == "stmt1.pdf"
    assert rec.StatementDate == date(2025, 1, 15)
    assert rec.MostRecentPaymentAmount == 1234.56
    assert rec.AmountPrincipal == 2000.00
    assert rec.AmountInterest == 150.50
    assert rec.AmountTaxInsurance == 75.25
    assert rec.AmountUnpaidBalance == 10000.00
    # Remove '%' sign and parse interest rate as float
    assert abs(rec.AmountInterestRate - 3.75) < 1e-6
    assert rec.PastDueAmount == 200.00
    assert rec.LinkToStatement == "https://drive.google.com/file/d/ABC123/view"
    assert rec.PropertyAddress == "123 Main St, Anytown, USA"
