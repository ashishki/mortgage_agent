# modules/processing_chain.py
"""
LangChain-like Chain orchestration: DriveWatcher → PDFParser → Extractor → Writer.
If langchain.Chain is unavailable, falls back to a simple base class.
"""
from modules.drive_watcher import DriveWatcher
from modules.pdf_parser import PDFParser
from modules.extractor import Extractor
from modules.writer import Writer

# Fallback Chain class if langchain doesn't provide one
try:
    from langchain import Chain
except ImportError:
    class Chain:
        input_keys = []
        output_keys = ["processed"]
        def __init__(self, config: dict = None):
            self.config = config or {}
        def __call__(self, inputs: dict) -> dict:
            return self._call(inputs)

class ProcessingChain(Chain):
    """
    Orchestrates the pipeline: DriveWatcher → PDFParser → Extractor → Writer
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.watcher   = DriveWatcher(config.get('drive', {}))
        self.parser    = PDFParser(config.get('ocr', {}))
        self.extractor = Extractor(config.get('lenders', []), config.get('llm', {}))
        self.writer    = Writer(config.get('output', {}))

    def _call(self, inputs: dict) -> dict:
        new_files = self.watcher.list_new_pdfs()
        for meta in new_files:
            pdf_bytes = self.watcher.download_file(meta['id'])
            text      = self.parser.extract_text(pdf_bytes)
            record    = self.extractor.extract(text)
            if not record.get('needs_review'):
                self.writer.append_record(record)
        return {"processed": len(new_files)}
