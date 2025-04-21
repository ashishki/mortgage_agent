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
                'credentials_json': '<path/to/creds.json>',
                'headers': ['col1', 'col2', ...]  # optional header row
            }
        }

        Config structure for Airtable:
        {
            'type': 'airtable',
            'airtable': {
                'base_id': '<BASE_ID>',
                'table_name': '<TABLE_NAME>',
                'api_key': '<API_KEY>' or 'token': '<TOKEN>'
            }
        }
        """
        self.config = config
        writer_type = config.get('type')

        if writer_type == 'sheets':
            ss_cfg = config['sheets']
            from gspread import service_account

            # Authenticate and open sheet
            client = service_account(filename=ss_cfg['credentials_json'])
            ss = client.open_by_key(ss_cfg['spreadsheet_id'])
            self._worksheet = ss.worksheet('Sheet1')
            self._mode = 'sheets'

            # Setup headers if provided
            self._headers = ss_cfg.get('headers', [])
            if self._headers:
                # Read first row
                try:
                    first_row = self._worksheet.row_values(1)
                except Exception:
                    first_row = []
                # Insert headers if they differ
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
            if hasattr(self, '_headers') and self._headers:
                # Order values according to headers
                row = [record.get(col, '') for col in self._headers]
            else:
                row = list(record.values())
            self._worksheet.append_row(row)

        elif self._mode == 'airtable':
            self._airtable.insert(record)

        else:
            raise RuntimeError(f"Unsupported write mode: {self._mode}")