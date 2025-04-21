# Mortgage Statement Processing Agent

[![CI](https://github.com/ashishki/mortgage_agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ashishki/mortgage_agent/actions)
[![Coverage](https://codecov.io/gh/ashishki/mortgage_agent/branch/main/graph/badge.svg)](https://codecov.io/gh/ashishki/mortgage_agent)
[![Python Versions](https://img.shields.io/badge/python-3.8%2C3.9%2C3.10%2C3.11-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A fully automated pipeline to monitor a Google Drive folder of PDF mortgage statements, extract structured data using a hybrid regex + LLM approach, and store results in Google Sheets or Airtable. Features:

- **DriveWatcher**: Polls a Drive folder for new PDFs using a service account
- **PDFParser**: Extracts text via `pdfplumber` with Tesseract OCR fallback
- **Extractor**: Uses regex for known lenders, with GPT-4 fallback via OpenAI SDK
- **Writer**: Appends records to Google Sheets (with headers) or Airtable
- **Indexer**: Builds a semantic vector index using LlamaIndex for search
- **Notifier**: Sends Slack alerts for any records requiring manual review
- **ProcessedStore**: Tracks processed files to avoid duplicates
- **Langfuse Integration**: Automatic tracing of all OpenAI calls
- **100% Test Coverage**: Comprehensive pytest suite for each module

---

## 🚀 Quickstart

1. **Clone the repo**
   ```bash
   git clone https://github.com/ashishki/mortgage_agent.git
   cd mortgage_agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in project root:
   ```ini
   DRIVE_FOLDER_ID=<your_drive_folder_id>
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   TESSERACT_CMD=/usr/bin/tesseract
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4
   OUTPUT_TYPE=sheets
   SPREADSHEET_ID=<your_spreadsheet_id>
   AIRTABLE_BASE_ID=<your_base_id>
   AIRTABLE_TABLE_NAME=<your_table_name>
   AIRTABLE_TOKEN=<your_airtable_token>
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_PROJECT_ID=<project_id>
   LOG_LEVEL=INFO
   ```

5. **Configure `config.yaml`** (placeholders are auto‑expanded from `.env`):
   ```yaml
   drive:
     folder_id: ${DRIVE_FOLDER_ID}
     credentials_json: null

   ocr:
     lang: eng
     tesseract_cmd: ${TESSERACT_CMD}

   lenders:
     - name: example_bank
       regex_patterns:
         StatementDate: "Statement Date[:\s]+(?P<value>\d{1,2}/\d{1,2}/\d{4})"
         # ... more patterns ...

   llm:
     model: ${OPENAI_MODEL}
     api_key: ${OPENAI_API_KEY}
     temperature: 0.0
     max_tokens: 512

   output:
     type: ${OUTPUT_TYPE}
     sheets:
       spreadsheet_id: ${SPREADSHEET_ID}
       credentials_json: ${GOOGLE_APPLICATION_CREDENTIALS}
       headers:
         - StatementFileName
         - StatementDate
         - MostRecentPaymentDate
         - MostRecentPaymentAmount
         - AmountPrincipal
         - AmountInterest
         - AmountTaxInsurance
         - AmountUnpaidBalance
         - AmountInterestRate
         - PastDueAmount
         - PropertyAddress
     airtable:
       base_id: ${AIRTABLE_BASE_ID}
       table_name: ${AIRTABLE_TABLE_NAME}
       token: ${AIRTABLE_TOKEN}

   notifier:
     slack:
       webhook_url: ${SLACK_WEBHOOK_URL}

   index:
     persist_path: ./index.json

   store:
     persist_path: ./processed.json

   logging:
     level: ${LOG_LEVEL}
   ```

6. **Run the agent**
   ```bash
   python main.py
   ```

All new statements will be processed, stored, indexed, and any anomalies notified via Slack.

---

## 📚 Testing & CI

- **Run tests**:
  ```bash
  pytest -q
  ```
- **GitHub Actions** workflows ensure CI, linting, and coverage.

---

## 🛠️ Architecture Overview

```
mortgage_agent/
├── main.py
├── config.yaml
├── .env
├── modules/
│   ├── drive_watcher.py    # Google Drive polling
│   ├── pdf_parser.py       # PDF→text extraction
│   ├── extractor.py        # Regex + GPT-4 extraction
│   ├── writer.py           # Sheets/Airtable output
│   ├── indexer.py          # Semantic vector index
│   ├── notifier.py         # Slack alerts
│   ├── processed_store.py  # Deduplication store
│   └── utils.py            # Logging & normalization
├── tests/                  # pytest suite
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing

1. Fork the repo and create a feature branch.
2. Write tests for new functionality.
3. Submit a PR, ensure CI passes.

Happy automating! 🚀