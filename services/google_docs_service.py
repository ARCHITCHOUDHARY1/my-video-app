import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents"]

logger = logging.getLogger(__name__)

class GoogleDocsService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        try:
            if not os.path.exists("credentials.json"):
                logger.warning("credentials.json not found. Falling back to local text file.")
                return

            if os.path.exists("token.json"):
                self.creds = Credentials.from_authorized_user_file(
                    "token.json", SCOPES
                )

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                with open("token.json", "w") as token:
                    token.write(self.creds.to_json())

            self.service = build("docs", "v1", credentials=self.creds)
            logger.info("Authenticated with Google Docs API")
            
        except Exception as e:
            logger.error(f"Google Docs authentication failed: {str(e)}")
            self.service = None

    def create_doc(self, title: str, content: str):
        if not self.service:
            logger.warning("Google Docs service not available, skipping doc creation")
            return None
        
        try:
            doc = self.service.documents().create(
                body={"title": title}
            ).execute()

            doc_id = doc.get("documentId")

            requests = [{
                "insertText": {
                    "location": {"index": 1},
                    "text": content
                }
            }]

            self.service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": requests}
            ).execute()
            
            url = f"https://docs.google.com/document/d/{doc_id}"
            logger.info(f"Created Google Doc: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to create Google Doc: {str(e)}")
            return None
