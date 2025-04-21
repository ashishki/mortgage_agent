# tests/test_processing_chain.py
import pytest
from modules.processing_chain import ProcessingChain

class DummyWatcher:
    def __init__(self, files):
        self._files = files
        self.downloaded = []

    def list_new_pdfs(self):
        return self._files

    def download_file(self, file_id):
        self.downloaded.append(file_id)
        return b"pdf-bytes"

class DummyParser:
    def __init__(self):
        self.texts = []

    def extract_text(self, pdf_bytes):
        self.texts.append(pdf_bytes)
        return "parsed-text"

class DummyExtractor:
    def __init__(self, results):
        self._results = results

    def extract(self, text):
        return self._results

class DummyWriter:
    def __init__(self):
        self.records = []

    def append_record(self, record):
        self.records.append(record)

@pytest.fixture
def stub_chain(monkeypatch):
    # Prepare dummy modules
    files = [{"id": "1"}, {"id": "2"}]
    watcher = DummyWatcher(files)
    parser = DummyParser()

    # First record needs review, second does not
    extractor1 = DummyExtractor({"needs_review": True})
    extractor2 = DummyExtractor({"needs_review": False, "foo": "bar"})
    writer = DummyWriter()

    # Monkeypatch the instantiation inside ProcessingChain
    import modules.processing_chain as pc_mod
    monkeypatch.setattr(pc_mod, 'DriveWatcher', lambda cfg: watcher)
    monkeypatch.setattr(pc_mod, 'PDFParser', lambda cfg: parser)

    # Sequence extractor calls: first returns extractor1 results, then extractor2
    def fake_extractor_factory(cfg1, cfg2):
        class E:
            def __init__(self):
                self._count = 0

            def extract(self, text):
                idx = self._count
                self._count += 1
                return extractor1._results if idx == 0 else extractor2._results

        return E()
    monkeypatch.setattr(pc_mod, 'Extractor', fake_extractor_factory)

    monkeypatch.setattr(pc_mod, 'Writer', lambda cfg: writer)
    return ProcessingChain({'drive':{}, 'ocr':{}, 'lenders':[], 'llm':{}, 'output':{}}), watcher, parser, writer


def test_processing_chain_calls_components(stub_chain):
    chain, watcher, parser, writer = stub_chain
    result = chain({})
    # Should process both files, but write only one (the second)
    assert result['processed'] == 2
    assert writer.records == [{"needs_review": False, "foo": "bar"}]



