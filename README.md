# Mortgage Statement Processing Agent

[![CI](https://github.com/ashishki/mortgage_agent/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ashishki/mortgage_agent/actions)
[![Coverage](https://codecov.io/gh/ashishki/mortgage_agent/branch/main/graph/badge.svg)](https://codecov.io/gh/ashishki/mortgage_agent)
[![Python Versions](https://img.shields.io/badge/python-3.8%2C3.9%2C3.10%2C3.11-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A robust, fully‑automated pipeline that watches a Google Drive folder for PDF mortgage statements, extracts structured data using a hybrid regex + LLM approach, and stores results to Google Sheets or Airtable. Key features:

- **DriveWatcher**: Authenticates with a service account to list and download new PDFs.
- **PDFParser**: Uses `pdfplumber` and Tesseract OCR fallback for text extraction.
- **Extractor**: First attempts regex per configured lender; missing fields trigger GPT‑4 fallback.
- **Writer**: Appends rows to Google Sheets (with optional headers) or Airtable tables.
- **Indexer**: Builds a semantic vector index via LlamaIndex for later search and analytics.
- **Notifier**: Sends Slack alerts for any statement missing mandatory fields.
- **ProcessedStore**: Tracks processed file IDs in JSON to avoid duplicate processing.
- **ProcessingChain**: Orchestrates all modules end‑to‑end in a single callable class.
- **Langfuse Integration**: Drop‑in replacement for the OpenAI SDK to trace all LLM calls.
- **Dockerized**: Multi‑stage `Dockerfile` for lean production images with Tesseract.
- **CI/CD**: GitHub Actions runs tests, coverage, and builds/publishes Docker images to GHCR.

---

## 🚀 Quickstart

1. **Clone the repo**
   ```bash
   git clone https://github.com/ashishki/mortgage_agent.git
   cd mortgage_agent
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env`** in the project root:
   ```ini
   DRIVE_FOLDER_ID=<drive_folder_id>
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json
   TESSERACT_CMD=/usr/bin/tesseract
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4
   OUTPUT_TYPE=sheets
   SPREADSHEET_ID=<sheet_id>
   AIRTABLE_BASE_ID=<base_id>
   AIRTABLE_TABLE_NAME=<table_name>
   AIRTABLE_TOKEN=<airtable_token>
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_PROJECT_ID=<project_id>
   LOG_LEVEL=INFO
   ```

5. **Configure `config.yaml`** (slots auto‑filled from `.env`):
   ```yaml
   drive:
     folder_id: ${DRIVE_FOLDER_ID}
     credentials_json: null

   ocr:
     lang: eng
     tesseract_cmd: ${TESSERACT_CMD}

   lenders:
     - name: shellpoint
       regex_patterns:
         StatementDate: "Statement Date[:\\s]+(?P<value>\\d{1,2}/\\d{1,2}/\\d{4})"
         AmountPrincipal: "Principal Balance[:\\s]*\\$?(?P<value>[\\d,]+\\.\\d{2})"
         # ... other patterns ...

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

6. **Run locally**
   ```bash
   python main.py
   ```
   - New statements are processed, stored, indexed, and any incomplete records notify via Slack.

---

## 🧪 Testing & CI

- **Run tests** locally:
  ```bash
  pytest -q
  ```
- **GitHub Actions** automates:
  - pytest on PRs and pushes
  - Coverage reporting to Codecov
  - Docker build & push to GitHub Container Registry

---

## 📦 Deployment & Scheduling

- **Docker**: built from multi‑stage `Dockerfile`, published as `ghcr.io/ashishki/mortgage_agent:latest`.
- **Cloud Run Job** or **Kubernetes CronJob** to schedule periodic runs (e.g., daily at 06:00 UTC).

Example K8s CronJob snippet:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mortgage-agent
spec:
  schedule: "0 6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: agent
            image: ghcr.io/ashishki/mortgage_agent:latest
            env:
              - name: GOOGLE_APPLICATION_CREDENTIALS
                value: /secrets/sa.json
              - name: DRIVE_FOLDER_ID
                valueFrom:
                  secretKeyRef:
                    name: drive-creds
                    key: folder_id
          restartPolicy: OnFailure
``` 

---

## 🔧 Next Steps

1. **Regex Coverage Expansion**: Add new lender patterns and automated regex tests.
2. **Monitoring & Alerts**: Add log‑based metrics for error rates and integrate with Cloud Monitoring or PagerDuty.
3. **Versioning & Rollback**: Tag Docker images by Git SHA or semantic version in CI.
4. **Light UI**: Build a React dashboard for searching indexed records and reviewing notifications.

Contributions welcome! Fork, add tests, and PR. Happy automating! 🚀

