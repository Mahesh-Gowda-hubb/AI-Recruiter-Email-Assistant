import base64
import re

from bs4 import BeautifulSoup

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

class GmailService:
    """
    Handles Gmail authentication and creates
    a Gmail API service instance.
    """

    def __init__(self):
        """
        Initialize the Gmail service.

        The service object will be created after
        successful authentication.
        """
        self.service = None
        
    def authenticate(self):
        """
        Authenticate the user and create
        the Gmail API service.
        """
        credentials = None
                # Check if a saved token already exists
        if os.path.exists("token.json"):
            credentials = Credentials.from_authorized_user_file(
                "token.json",
                SCOPES
            )
        # If there are no valid credentials, authenticate the user
        if not credentials or not credentials.valid:
                        # Refresh the token if it has expired
            if (
                credentials
                and credentials.expired
                and credentials.refresh_token
            ):
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "config/credentials.json",
                    SCOPES
                )
                credentials = flow.run_local_server(port=0)
            # Save the credentials for future runs
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    # Build the Gmail API service
        self.service = build(
        "gmail",
        "v1",
        credentials=credentials
        )

        return self.service
    
    def read_messages(self, max_results=10):
        """
        Retrieve the latest Gmail messages.

        Args:
            max_results (int): Maximum number of messages to retrieve.

        Returns:
            list: List of Gmail message metadata.
        """

        results = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                maxResults=max_results
            )
            .execute()
        )

        messages = results.get("messages", [])

        return messages
    def get_message(self, message_id):
        """
        Retrieve the full details of a Gmail message.

        Args:
            message_id (str): Gmail message ID.

        Returns:
            dict: Full Gmail message data.
        """

        message = (
            self.service.users()
            .messages()
            .get(
                userId="me",
                id=message_id
            )
            .execute()
        )
        return message
    def get_header(self, headers, header_name):
        """
        Extract a specific header value from Gmail headers.

         Args:
        headers (list): Gmail message headers.
        header_name (str): Header name to search for.

         Returns:
        str or None: Header value if found, otherwise None.
         """
        for header in headers:
            if header["name"] == header_name:
                return header["value"]
        return None

    def _find_body_part(self, payload, mime_type):
        """
        Recursively search for a specific MIME type in the email payload.

        """
        # Check the current payload
        if payload.get("mimeType") == mime_type:
            body_data = payload.get("body", {}).get("data")
            if body_data:
                return body_data
             # Check nested parts
        for part in payload.get("parts", []):
            result = self._find_body_part(part, mime_type)
            if result:
                return result
        return None
        

    def get_body(self, payload):
        """
        Extract, decode and clean the email body.
        """

        # --------------------------------------------------
        # 1. Prefer plain text
        # --------------------------------------------------

        body_data = self._find_body_part(
            payload,
            "text/plain"
        )

        if body_data:

            decoded_bytes = base64.urlsafe_b64decode(
                body_data
            )

            body_text = decoded_bytes.decode(
                "utf-8",
                errors="replace"
            )

            return body_text

        # --------------------------------------------------
        # 2. Fall back to HTML
        # --------------------------------------------------

        body_data = self._find_body_part(
            payload,
            "text/html"
        )

        if body_data:

            decoded_bytes = base64.urlsafe_b64decode(
                body_data
            )

            html_text = decoded_bytes.decode(
                "utf-8",
                errors="replace"
            )

            soup = BeautifulSoup(
                html_text,
                "html.parser"
            )

            clean_text = soup.get_text(
                separator="\n",
                strip=True
            )

            normalized_text = re.sub(
                r"\n\s*\n+",
                "\n\n",
                clean_text
            )

            return normalized_text

        return None