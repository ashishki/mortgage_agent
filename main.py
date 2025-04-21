# main.py
import os
from dotenv import load_dotenv
import yaml
import logging

from modules.drive_watcher import DriveWatcher
from modules.pdf_parser import PDFParser
from modules.extractor import Extractor
from modules.writer import Writer
from modules.utils import setup_logging


def main():
    # 1) Load environment variables from .env
    load_dotenv()

    # 2) Load config.yaml without shell defaults
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # 3) Override config values from environment with sensible defaults
    # Logging level
    log_level = (
        os.environ.get("LOG_LEVEL")
        or config.get("logging", {}).get("level")
        or "INFO"
    )
    setup_logging(log_level)

    # Drive settings
    drive_cfg = config.get("drive", {})
    drive_cfg["folder_id"] = (
        os.environ.get("DRIVE_FOLDER_ID")
        or drive_cfg.get("folder_id")
    )
    drive_cfg["credentials_json"] = (
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or drive_cfg.get("credentials_json")
    )

    # OCR settings
    ocr_cfg = config.get("ocr", {})
    ocr_cfg["tesseract_cmd"] = (
        os.environ.get("TESSERACT_CMD")
        or ocr_cfg.get("tesseract_cmd")
    )

    # LLM settings
    llm_cfg = config.get("llm", {})
    llm_cfg["api_key"] = (
        os.environ.get("OPENAI_API_KEY")
        or llm_cfg.get("api_key")
    )
    llm_cfg["model"] = (
        os.environ.get("OPENAI_MODEL")
        or llm_cfg.get("model")
    )

    # Output settings
    out_cfg = config.get("output", {})
    out_cfg["type"] = (
    os.environ.get("OUTPUT_TYPE")
    or out_cfg.get("type")
    or "sheets"
)
    if out_cfg.get("type") == "sheets":
        sheets = out_cfg.get("sheets", {})
        sheets["spreadsheet_id"] = (
            os.environ.get("SPREADSHEET_ID")
            or sheets.get("spreadsheet_id")
        )
        sheets["credentials_json"] = (
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            or sheets.get("credentials_json")
        )
    elif out_cfg.get("type") == "airtable":
        at = out_cfg.get("airtable", {})
        at["base_id"] = (
            os.environ.get("AIRTABLE_BASE_ID")
            or at.get("base_id")
        )
        at["table_name"] = (
            os.environ.get("AIRTABLE_TABLE_NAME")
            or at.get("table_name")
        )
        at["token"] = (
            os.environ.get("AIRTABLE_TOKEN")
            or at.get("token")
        )
    
    # 4) Initialize components
    watcher   = DriveWatcher(drive_cfg)
    parser    = PDFParser(ocr_cfg)
    extractor = Extractor(config.get("lenders", []), llm_cfg)
    writer    = Writer(out_cfg)

    # 5) Process new PDFs
    files = watcher.list_new_pdfs()
    logging.info(f"Found {len(files)} new PDF(s) to process")
    for meta in files:
        logging.info(f"Downloading {meta['name']} ({meta['id']})")
        pdf_bytes = watcher.download_file(meta["id"])
        text      = parser.extract_text(pdf_bytes)
        record    = extractor.extract(text)
        if record.get("needs_review"):
            logging.warning(f"Record for {meta['name']} needs review, skipping write")
            continue
        writer.append_record(record)
        logging.info(f"Appended record for {meta['name']}")


if __name__ == "__main__":
    main()
