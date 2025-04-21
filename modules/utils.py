# modules/utils.py
"""
Utility helpers for date/currency normalization and logging.
"""

import logging
from dateutil import parser as date_parser
import re

def setup_logging(level: str = "INFO"):
    """
    Configure root logger formatting and level.
    
    Args:
        level: Logging level string (e.g. "DEBUG", "INFO").
    """
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(levelname)s %(message)s",
    )

def normalize_date(date_str: str) -> str:
    """
    Parse and reformat a date string to ISO yyyy-mm-dd.
    
    Args:
        date_str: Raw date text.
    Returns:
        ISO-formatted date string.
    """
    dt = date_parser.parse(date_str)
    return dt.date().isoformat()

def parse_currency(curr_str: str) -> float:
    """
    Convert currency text like "$1,234.56" or "3.75%" to float.
    
    Args:
        curr_str: Raw currency or percentage string.
    Returns:
        Numeric value.
    """
    s = re.sub(r"[^\d\.]", "", str(curr_str))
    return float(s)
