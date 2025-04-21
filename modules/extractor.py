# modules/extractor.py
"""
Extract structured fields via regex and (optional) LLM fallback.
"""
import re
import json
from typing import Dict, List
# Drop-in replacement for OpenAI SDK to auto-log all calls to Langfuse
from langfuse.openai import openai

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
        openai.api_key = llm_config.get("api_key")

    def extract_with_regex(self, text: str) -> Dict[str, str]:
        """
        Apply regex patterns for each lender to extract known fields.

        Returns a dict mapping field names to string values.
        """
        results: Dict[str, str] = {}
        for lender in self.lenders_config:
            patterns = lender.get('regex_patterns', {})
            for field, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    try:
                        results[field] = match.group('value')
                    except IndexError:
                        results[field] = match.group(1)
        return results

    def _needs_llm(self, regex_res: Dict[str, str]) -> bool:
        """
        Determine whether LLM fallback is needed (missing any mandatory field).
        """
        mandatory_fields = set()
        for lender in self.lenders_config:
            mandatory_fields.update(lender.get('regex_patterns', {}).keys())
        for field in mandatory_fields:
            if not regex_res.get(field):
                return True
        return False

    def extract_with_llm(self, text: str) -> Dict[str, str]:
        """
        Use an LLM to extract all fields according to the regex schema.

        Sends a prompt to OpenAI ChatCompletion and parses the JSON response.
        """
        # Build the JSON schema list of fields
        fields = []
        for lender in self.lenders_config:
            fields.extend(lender.get('regex_patterns', {}).keys())
        # Create the prompt
        prompt = (
            "Extract the following fields from this mortgage statement as a JSON object: "
            + ", ".join(fields)
            + "\n\nText:\n" + text + "\n\nJSON:"
        )
        # Call the OpenAI ChatCompletion API (drop-in auto-logged by Langfuse)
               # For openai>=1.0.0 the ChatCompletion endpoint is under .chat.completions
        resp = openai.chat.completions.create(
            model=self.llm_config['model'],
            messages=[{"role":"user", "content": prompt}],
            temperature=self.llm_config.get("temperature", 0.0),
            max_tokens=self.llm_config.get("max_tokens", 512),
        )
        content = resp.choices[0].message.content
        # Parse and return the JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If parsing fails, return empty dict or handle error
            return {}

    def merge_results(self, regex_res: Dict[str, str], llm_res: Dict[str, str]) -> Dict[str, str]:
        """
        Merge regex and LLM extraction results, preferring regex values.
        """
        merged = dict(llm_res)
        merged.update(regex_res)
        return merged

    def extract(self, text: str) -> Dict[str, str]:
        """
        Full extraction pipeline: regex first, then LLM if needed.
        """
        regex_res = self.extract_with_regex(text)
        if self._needs_llm(regex_res):
            llm_res = self.extract_with_llm(text)
        else:
            llm_res = {}
        return self.merge_results(regex_res, llm_res)