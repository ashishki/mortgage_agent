# modules/models.py
from pydantic import BaseModel, field_validator
from datetime import date
import re

class StatementRecord(BaseModel):
    StatementFileName: str
    StatementDate: date
    MostRecentPaymentAmount: float
    AmountPrincipal: float
    AmountInterest: float
    AmountTaxInsurance: float
    AmountUnpaidBalance: float
    AmountInterestRate: float
    PastDueAmount: float
    LinkToStatement: str
    PropertyAddress: str

    @field_validator("StatementDate", mode="before")
    @classmethod
    def parse_date(cls, v):
        """
        Parse date strings like "MM/DD/YYYY" or ISO into datetime.date.
        """
        from dateutil import parser
        return parser.parse(v).date()

    @field_validator(
        "MostRecentPaymentAmount",
        "AmountPrincipal",
        "AmountInterest",
        "AmountTaxInsurance",
        "AmountUnpaidBalance",
        "AmountInterestRate",
        "PastDueAmount",
        mode="before"
    )
    @classmethod
    def parse_number(cls, v):
        """
        Remove non-numeric characters (including $, commas, %)
        and convert to float.
        """
        s = re.sub(r"[^0-9.]", "", str(v))
        return float(s)
