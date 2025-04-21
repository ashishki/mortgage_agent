# modules/indexer.py
"""
Index processed mortgage records for semantic search using LlamaIndex.
"""
from typing import Dict, List, Optional

try:
    from llama_index import GPTSimpleVectorIndex
except ImportError:
    GPTSimpleVectorIndex = None

try:
    # Document may be located in different submodules depending on version
    from llama_index import Document
except ImportError:
    try:
        from llama_index.core.schema import Document
    except ImportError:
        Document = None

class Indexer:
    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize the vector index, optionally loading or saving to disk.

        Args:
            persist_path: Path to save/load the index (optional).
        """
        self.persist_path = persist_path
        # Load existing index or create new
        if persist_path and GPTSimpleVectorIndex:
            try:
                self.index = GPTSimpleVectorIndex.load_from_disk(persist_path)
            except Exception:
                self.index = GPTSimpleVectorIndex([])
        else:
            # No persisting or library missing
            self.index = GPTSimpleVectorIndex([]) if GPTSimpleVectorIndex else None

    def add_record(self, record: Dict[str, str]) -> None:
        """
        Add a single record to the index.

        Args:
            record: Dictionary of field names to values.
        """
        if not self.index or not Document:
            return  # Indexing not available
        # Combine record into a single text blob
        text = "\n".join(f"{k}: {v}" for k, v in record.items())
        doc = Document(text=text, extra_info=record)
        self.index.insert(doc)
        # Persist index if configured
        if self.persist_path:
            self.index.save_to_disk(self.persist_path)

    def query(self, q: str) -> List[Dict[str, str]]:
        """
        Query the vector index and return matching records.

        Args:
            q: Search query string.

        Returns:
            List of record dicts matching the query.
        """
        if not self.index:
            return []
        response = self.index.query(q, response_mode="default")
        # Handle different response types
        if isinstance(response, dict):
            docs = response.get('docs', [])
        else:
            docs = getattr(response, 'docs', None) or getattr(response, 'documents', [])
        results: List[Dict[str, str]] = []
        for d in docs:
            info = getattr(d, 'extra_info', None)
            if info:
                results.append(info)
        return results
