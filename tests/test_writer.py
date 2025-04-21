# tests/test_writer.py
import pytest
from modules.writer import Writer

class DummyWorksheet:
    def __init__(self):
        self.rows = []
    def append_row(self, row):
        self.rows.append(row)

class DummySpreadsheet:
    def __init__(self):
        self.sheet1 = DummyWorksheet()
    def worksheet(self, name):
        return self.sheet1

class DummyGSpreadClient:
    def __init__(self, creds):
        pass
    def open_by_key(self, key):
        return DummySpreadsheet()

class DummyAirtable:
    def __init__(self, base_id, table_name, api_key):
        self.base_id = base_id
        self.table_name = table_name
        self.api_key = api_key
        self.records = []
    def insert(self, data):
        self.records.append(data)
        return data

@pytest.fixture(autouse=True)
def patch_clients(monkeypatch):
    # Patch gspread and airtable clients
    import modules.writer as wmod
    monkeypatch.setattr(wmod, 'gspread', type('m', (), {'authorize': lambda creds: DummyGSpreadClient(creds)}))
    monkeypatch.setattr(wmod, 'Airtable', DummyAirtable)
    yield


def test_append_record_to_sheets():
    config = {
        'type': 'sheets',
        'sheets': {'spreadsheet_id': 'sheet123'}
    }
    writer = Writer(config)
    record = {'A': 1, 'B': 2, 'C': 3}
    writer.append_record(record)
    # After insertion, the dummy worksheet should contain one row
    ws = writer._worksheet  # internal reference to DummyWorksheet
    assert ws.rows == [[1, 2, 3]]


def test_append_record_to_airtable():
    config = {
        'type': 'airtable',
        'airtable': {'base_id': 'base123', 'table_name': 'Table', 'api_key': 'keyabc'}
    }
    writer = Writer(config)
    record = {'Field1': 'val1', 'Field2': 'val2'}
    writer.append_record(record)
    # DummyAirtable should have recorded insertion
    at = writer._airtable  # internal reference
    assert at.records == [record]
