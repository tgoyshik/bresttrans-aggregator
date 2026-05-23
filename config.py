import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DEFAULT_CREDENTIALS = BASE_DIR / "credentials.json"
DEFAULT_OUTPUT = BASE_DIR / "merged_data.json"

REQUIRED_FIELDS = [
    'time', 'currentStop', 'nextStop', 'peopleAtStop', 'entered', 'exited', 'latitude', 'longitude', 'weather'
]

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
