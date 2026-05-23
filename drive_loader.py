import os
import re
import io
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import config

class GoogleDriveBusLoader:
    def __init__(self, credentials_file: Optional[str] = None):
        if credentials_file is None:
            self.credentials_file = str(config.DEFAULT_CREDENTIALS)
        else:
            self.credentials_file = credentials_file
        self.service = self._authenticate()
    
    def _authenticate(self):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=config.SCOPES
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"Auth error: {e}")
            return None

    def extract_folder_id(self, url: str) -> Optional[str]:
        patterns = [
            r'/folders/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
        
    def download_all_from_folder(self, folder_url: str, destination_dir: str) -> List[str]:
        downloaded_files = []
        folder_id = self.extract_folder_id(folder_url)
        if not folder_id or not self.service:
            return []
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            json_files = [f for f in files if f['name'].lower().endswith('.json')]

            for file in json_files:
                dest = os.path.join(destination_dir, file['name'])
                if os.path.exists(dest):
                    downloaded_files.append(dest)
                    continue

                request = self.service.files().get_media(fileId=file['id'])
                with io.FileIO(dest, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        _, done = downloader.next_chunk()
                downloaded_files.append(dest)
            return downloaded_files
        except Exception as e:
            print(f"Download error for folder {folder_id}: {e}")
            return []
