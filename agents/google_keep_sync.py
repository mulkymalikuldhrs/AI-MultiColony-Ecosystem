"""🗒️ KeepSyncAgent – Syncs Google Keep notes for further analysis.
Requires OAuth 2.0 credentials JSON (client_secret) and token storage.
Usage:
    keep = keep_sync_agent()
    notes = keep.fetch_notes()
"""
from __future__ import annotations
import os
from typing import List, Dict

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    InstalledAppFlow = None

SCOPES = ["https://www.googleapis.com/auth/keep.readonly"]
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_JSON", "token.json")
CRED_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "config/google-credentials.json")

class KeepSyncAgent:
    status = "ready"
    capabilities = ["keep_sync", "note_fetch"]

    def _auth(self):
        if not InstalledAppFlow:
            raise RuntimeError("google-auth libraries not installed: pip install google-auth-oauthlib google-api-python-client")
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        return creds

    def fetch_notes(self) -> List[Dict]:
        creds = self._auth()
        service = build("keep", "v1", credentials=creds, cache_discovery=False)
        result = service.notes().list(pageSize=50).execute()
        return result.get("notes", [])


def keep_sync_agent():
    return KeepSyncAgent()