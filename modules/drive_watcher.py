# modules/drive_watcher.py
"""
Watch a Google Drive folder for new PDF statements, authenticating via service account.
"""
from typing import List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class DriveWatcher:
    def __init__(self, config: Dict):
        """
        Initialize DriveWatcher with service account credentials.

        Args:
            config: Dict containing:
                - folder_id: Google Drive folder ID to watch.
                - credentials_json: Path to service-account JSON key file.
        """
        self.folder_id = config['folder_id']

        # Get the JSON key path from config
        creds_path = config.get('credentials_json')
        if not creds_path:
            raise ValueError("DriveWatcher config must include 'credentials_json'")

        # Scopes for Drive access
        scopes = [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)

        # Build the Drive API client
        self.service = build('drive', 'v3', credentials=creds)

    def list_new_pdfs(self) -> List[Dict]:
        """
        List PDF files in the monitored Drive folder.

        Returns:
            A list of dicts with keys 'id', 'name', 'modifiedTime'.
        """
        query = f"mimeType='application/pdf' and '{self.folder_id}' in parents"
        response = (
            self.service.files()
                .list(q=query, fields='files(id,name,modifiedTime)')
                .execute()
        )
        return response.get('files', [])

    def download_file(self, file_id: str) -> bytes:
        """
        Download the PDF file as raw bytes.

        Args:
            file_id: ID of the file to download.

        Returns:
            Raw bytes of the PDF.
        """
        media = self.service.files().get_media(fileId=file_id)
        return media.execute()
