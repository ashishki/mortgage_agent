# modules/processing_chain.py
"""
Orchestrates the pipeline: DriveWatcher → PDFParser → Extractor → Writer → Indexer → Notifier
"""
from typing import Dict
from modules.drive_watcher import DriveWatcher
from modules.pdf_parser import PDFParser
from modules.extractor import Extractor
from modules.writer import Writer
from modules.indexer import Indexer
from modules.notifier import Notifier
from modules.processed_store import ProcessedStore

class ProcessingChain:
    """
    Simple orchestrator for processing PDFs end-to-end.
    """
    def __init__(self, config: Dict):
        self.config = config
        # Initialize components
        self.watcher   = DriveWatcher(config.get('drive', {}))
        self.parser    = PDFParser(config.get('ocr', {}))
        self.extractor = Extractor(config.get('lenders', []), config.get('llm', {}))
        self.writer    = Writer(config.get('output', {}))
        # Semantic indexer
        index_cfg = config.get('index', {}) or {}
        persist_path = index_cfg.get('persist_path')
        self.indexer  = Indexer(persist_path=persist_path)
        # Notifier for review queue
        notifier_cfg = config.get('notifier')

        store_cfg = config.get('store', {}) or {}
        self.store = ProcessedStore(store_path=store_cfg.get('persist_path'))

        try:
            if notifier_cfg:
                self.notifier = Notifier(notifier_cfg)
            else:
                self.notifier = None
        except ValueError:
            self.notifier = None

    def __call__(self, inputs: Dict) -> Dict:
        return self._call(inputs)

    def _call(self, inputs: Dict) -> Dict:
        new_files = self.watcher.list_new_pdfs()
        
        for meta in new_files:
            if self.store.has_processed(meta['id']):
                continue
            pdf_bytes = self.watcher.download_file(meta['id'])
            text      = self.parser.extract_text(pdf_bytes)
            record    = self.extractor.extract(text)
            # If missing mandatory fields, notify and skip
            if record.get('needs_review'):
                if getattr(self, 'notifier', None):
                    try:
                        self.notifier.notify(record)
                    except Exception:
                        pass
                continue
            # Otherwise write to destination and index
            self.writer.append_record(record)
            try:
                self.indexer.add_record(record)
            except Exception:
                pass

            self.store.mark_processed(meta['id'])

        return {'processed': len(new_files)}
