# modules/extractor.py
"""
Extract structured fields via regex and (optional) LLM fallback.
"""
import re
from typing import Dict, List

class Extractor:
    def __init__(self, lenders_config: List[Dict], llm_config: Dict):
        """
        Initialize the extractor with lender regex patterns and LLM settings.

        Args:
            lenders_config: List of lenders, each with 'name' and 'regex_patterns'.
            llm_config: Configuration for LLM fallback (model, API key, etc.).
        """
        self.lenders_config = lenders_config
        self.llm_config = llm_config

    def extract_with_regex(self, text: str) -> Dict[str, str]:
        """
        Apply regex patterns for each lender to extract known fields.

        Args:
            text: Raw text from the PDF.

        Returns:
            Dict mapping field names to extracted string values.
        """
        results: Dict[str, str] = {}
        for lender in self.lenders_config:
            patterns = lender.get('regex_patterns', {})
            for field, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    # Expect regex with named group 'value'
                    try:
                        results[field] = match.group('value')
                    except IndexError:
                        # fallback to first group
                        results[field] = match.group(1)
        return results

    def _needs_llm(self, regex_res: Dict[str, str]) -> bool:
        """
        Determine whether LLM fallback is needed (missing any mandatory field).

        Args:
            regex_res: Dict of fields extracted by regex.

        Returns:
            True if any field defined in regex_patterns is missing.
        """
        mandatory_fields = set()
        for lender in self.lenders_config:
            mandatory_fields.update(lender.get('regex_patterns', {}).keys())
        # If any mandatory field is missing or empty, fallback
        for field in mandatory_fields:
            if not regex_res.get(field):
                return True
        return False

    def extract_with_llm(self, text: str) -> Dict[str, str]:
        """
        Use an LLM to extract all fields according to schema (stub implementation).

        Args:
            text: Raw text from the PDF.

        Returns:
            Dict mapping field names to extracted string values.
        """
        # TODO: integrate OpenAI API to parse text into JSON schema
        return {}

    def merge_results(self, regex_res: Dict[str, str], llm_res: Dict[str, str]) -> Dict[str, str]:
        """
        Merge regex and LLM extraction results, preferring regex values.

        Args:
            regex_res: Results from regex extraction.
            llm_res: Results from LLM fallback.

        Returns:
            Combined dict with all fields present where possible.
        """
        merged = dict(llm_res)  # start with LLM fields
        merged.update(regex_res)  # overwrite/add with regex fields
        return merged

    def extract(self, text: str) -> Dict[str, str]:
        """
        Full extraction pipeline: regex first, then LLM if needed.

        Args:
            text: Raw text from the PDF.

        Returns:
            Final dict of extracted fields.
        """
        regex_res = self.extract_with_regex(text)
        if self._needs_llm(regex_res):
            llm_res = self.extract_with_llm(text)
        else:
            llm_res = {}
        return self.merge_results(regex_res, llm_res)
