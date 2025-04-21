# modules/processed_store.py
"""
Track which Drive file IDs have been processed to avoid reprocessing.
"""
import json
import os
from typing import Optional, Set

class ProcessedStore:
    def __init__(self, store_path: Optional[str] = None):
        """
        Initialize the processed-store, loading existing state or creating a new one.

        Args:
            store_path: Path to JSON file where processed IDs are saved.
        """
        self.store_path = store_path or "processed.json"
        # Load existing IDs or start empty
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._processed: Set[str] = set(data)
            except Exception:
                # Corrupted or unreadable file, start fresh
                self._processed = set()
        else:
            self._processed = set()

    def has_processed(self, file_id: str) -> bool:
        """
        Check if a given file_id has already been marked processed.
        """
        return file_id in self._processed

    def mark_processed(self, file_id: str) -> None:
        """
        Mark a file_id as processed and persist the store to disk.
        """
        self._processed.add(file_id)
        # Persist updated list
        try:
            with open(self.store_path, 'w', encoding='utf-8') as f:
                json.dump(list(self._processed), f)
        except Exception:
            # In case of write errors, ignore but keep in-memory
            pass