# tests/test_indexer.py
import pytest
from modules.indexer import Indexer

class DummyIndex:
    def __init__(self):
        self.docs = []
        self.saved = False
    def insert(self, doc):
        self.docs.append(doc)
    def save_to_disk(self, path):
        self.saved = True
    def query(self, q, response_mode):
        return {'query': q, 'mode': response_mode, 'docs': self.docs}

class DummyDocument:
    def __init__(self, text, extra_info):
        self.text = text
        self.extra_info = extra_info

@pytest.fixture(autouse=True)
def patch_llama(monkeypatch):
    import modules.indexer as idx_mod
    # Patch GPTSimpleVectorIndex and Document
    monkeypatch.setattr(idx_mod, 'GPTSimpleVectorIndex', lambda docs: DummyIndex())
    monkeypatch.setattr(idx_mod, 'Document', lambda text, extra_info: DummyDocument(text, extra_info))
    yield


def test_add_record_creates_document_and_persists(tmp_path):
    idx_path = tmp_path / "index.json"
    idx = Indexer(persist_path=str(idx_path))
    record = {'A': '1', 'B': '2'}
    idx.add_record(record)
    # Document inserted
    assert len(idx.index.docs) == 1
    doc = idx.index.docs[0]
    assert isinstance(doc, DummyDocument)
    assert doc.extra_info == record
    # Index persisted
    assert idx.index.saved


def test_query_returns_matching_records():
    idx = Indexer()
    # Replace index with dummy
    idx.index = DummyIndex()
    # Pre-populate
    rec = {'foo': 'bar'}
    idx.index.insert(DummyDocument(text='foo: bar', extra_info=rec))
    result = idx.query('bar')
    assert isinstance(result, list)
    assert result == [rec]
