# tests/test_drive_watcher.py
import pytest
from modules.drive_watcher import DriveWatcher

# Dummy classes to simulate Google Drive API
class DummyFilesList:
    def __init__(self):
        self._query = None
    def list(self, **kwargs):
        # Capture kwargs for introspection
        self._query = kwargs
        return self
    def execute(self):
        # Return a fake file list response
        return {"files": [{"id": "1", "name": "a.pdf", "modifiedTime": "2025-01-01T00:00:00Z"}]}

class DummyMediaDownload:
    def __init__(self, data: bytes):
        self._data = data
    def execute(self):
        return self._data

class DummyFilesService:
    def __init__(self):
        self._list = DummyFilesList()
        self._download = DummyMediaDownload(b"%PDF-1.4 Dummy PDF bytes")
    def files(self):
        return self
    def list(self, **kwargs):
        return self._list.list(**kwargs)
    def get_media(self, fileId):
        return self._download

# Monkeypatch the build function to return our dummy service
@pytest.fixture(autouse=True)
def patch_drive_service(monkeypatch):
    import modules.drive_watcher as dw_mod
    monkeypatch.setattr(dw_mod, 'build', lambda *args, **kwargs: DummyFilesService())
    yield


def test_list_new_pdfs_returns_expected_dict():
    config = {"credentials_json": "fake.json", "folder_id": "folder123"}
    watcher = DriveWatcher(config)

    result = watcher.list_new_pdfs()

    assert isinstance(result, list)
    assert result == [{"id": "1", "name": "a.pdf", "modifiedTime": "2025-01-01T00:00:00Z"}]


def test_download_file_returns_bytes():
    config = {"credentials_json": "fake.json", "folder_id": "folder123"}
    watcher = DriveWatcher(config)

    data = watcher.download_file("1")
    assert isinstance(data, (bytes, bytearray))
    assert data.startswith(b"%PDF-1.4")
