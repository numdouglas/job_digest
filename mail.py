import os
import base64
from email.message import EmailMessage
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- Configuration ---
# The file 'token.json' stores the user's access and refresh tokens,
# and is created automatically when the authorization flow completes for the first time.
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

# If modifying these scopes, delete the file token.json.
# This scope allows the script to send emails.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def create_message(sender, to, subject, message_text):
    """Creates a MIME message for sending via the API."""
    message = EmailMessage()
    message.add_alternative(message_text, subtype="html")
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # The API requires the message to be base64url-encoded
    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw_message.decode()}


def send_message(service, user_id, message):
    """Sends the message to the Gmail API."""
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        return sent_message
    except Exception as error:
        return None


def get_creds():
    """Shows user how to send a message."""
    creds = None

    # Load credentials if they exist
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, initiate the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This step will open a browser window for user authentication
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the new credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())


def push_mail(message: str):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # Build the Gmail service client
    service = build('gmail', 'v1', credentials=creds)

    # --- Email Details ---
    SENDER_EMAIL = 'me'  # 'me' is a special value for the authenticated user
    RECEIVER_EMAIL = 'panchikombogz@gmail.com'
    SUBJECT = 'Open Roles'
    BODY = message

    # 1. Create the API message object
    message = create_message(SENDER_EMAIL, RECEIVER_EMAIL, SUBJECT, BODY)

    # 2. Send the message
    send_message(service, SENDER_EMAIL, message)


if __name__ == "__main__":
    get_creds()
