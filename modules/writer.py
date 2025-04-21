# modules/writer.py
"""
Append extracted records to Google Sheets or Airtable based on configuration.
"""
from typing import Dict
import gspread
from airtable import Airtable

class Writer:
    def __init__(self, config: Dict):
        """
        Initialize Writer according to the output config.

        Config structure for Sheets:
        {
            'type': 'sheets',
            'sheets': {
                'spreadsheet_id': '<ID>',
                # Optional credentials_json path for service-account auth
                'credentials_json': '<path/to/creds.json>',
                # Optional list of header names
                'headers': ['col1', 'col2', ...]
            }
        }

        Config structure for Airtable:
        {
            'type': 'airtable',
            'airtable': {
                'base_id': '<BASE_ID>',
                'table_name': '<TABLE_NAME>',
                # Either 'api_key' or 'token'
                'api_key': '<API_KEY>'
            }
        }
        """
        self.config = config
        writer_type = config.get("type", "")
        writer_type = writer_type.split("#", 1)[0].strip()

        if writer_type == 'sheets':
            ss_cfg = config['sheets']
            # Use service_account if credentials_json provided, else authorize()
            if ss_cfg.get('credentials_json'):
                from gspread import service_account
                client = service_account(filename=ss_cfg['credentials_json'])
            else:
                client = gspread.authorize(None)

            ss = client.open_by_key(ss_cfg['spreadsheet_id'])
            self._worksheet = ss.worksheet('Sheet1')
            self._mode = 'sheets'

            # Optionally insert headers
            self._headers = ss_cfg.get('headers', []) or []
            if self._headers:
                try:
                    first_row = self._worksheet.row_values(1)
                except Exception:
                    first_row = []
                if first_row != self._headers:
                    self._worksheet.insert_row(self._headers, index=1)

        elif writer_type == 'airtable':
            at_cfg = config['airtable']
            base_id = at_cfg['base_id']
            table_name = at_cfg['table_name']
            api_token = at_cfg.get('api_key') or at_cfg.get('token')
            if not api_token:
                raise ValueError("Airtable config must include 'api_key' or 'token'.")
            self._airtable = Airtable(base_id, table_name, api_token)
            self._mode = 'airtable'

        else:
            raise ValueError(f"Unknown writer type: {writer_type}")

    def append_record(self, record: Dict):
        """
        Append a single record to the configured destination.

        Args:
            record: Dict mapping field names to values.
        """
        if self._mode == 'sheets':
            if self._headers:
                # Order values according to headers list
                row = [record.get(col, '') for col in self._headers]
            else:
                row = list(record.values())
            self._worksheet.append_row(row)

        elif self._mode == 'airtable':
            self._airtable.insert(record)

        else:
            raise RuntimeError(f"Unsupported write mode: {self._mode}")
