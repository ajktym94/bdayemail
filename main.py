import os
import io
import json
import shutil
import base64
import requests
import pandas as pd
from datetime import datetime, timedelta
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# Define the scope required by the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

google_drive_folder_id = os.environ.get("GDRIVE_FOLDER_ID")
credentials = os.environ.get('GDRIVE_CREDENTIALS')
token = os.environ.get('GDRIVE_TOKEN')
token_json = json.loads(token)
credentials_json = json.loads(credentials)

def gmail_authenticate():
    creds = None
    # Load existing credentials if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_info(token_json)
    # If there are no (valid) credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
            credentials_json, SCOPES
        )
            creds = flow.run_local_server(port=0)
    return creds

def create_message(sender, to, subject, message_text):
    # Compose the email as a MIMEText object
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(service, sender, to, subject, message_text):
    # Create and send the message
    message = create_message(sender, to, subject, message_text)
    try:
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Email sent successfully: {sent_message}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
def download_csv_from_drive(file_id):
    # Google Drive download URL with format
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    os.mkdir('tmp')
    file_path = os.path.join(os.getcwd(), 'tmp', "birthdays.csv")

    response = requests.get(download_url)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File downloaded successfully as birthdays.csv")
        return file_path
    else:
        print("Failed to download file.")

# Main program
if __name__ == "__main__":

    file_path = download_csv_from_drive(FILE_ID)
    birthdays = pd.read_csv(file_path)
    
    # Get today's date in YYYY-MM-DD format
    today = datetime.now()
    print(today)
    tomorrow = today + timedelta(days=1)

    # Check each entry in the CSV
    for _, row in birthdays.iterrows():
        if row['Birthday'] == tomorrow.strftime("%d-%m-%Y"):
            creds = gmail_authenticate()  # Authenticate with Gmail API
            service = build('gmail', 'v1', credentials=creds)  # Build Gmail API service

            # Set email details
            sender_email = "gkcylberlin@gmail.com"
            receiver_email = "gkcylkoln@gmail.com"
            subject = "GKCYL Koln Unit Birthday Reminder"
            body = f"Tomorrow is the birthday of {row['Name']}"

            # Send the email
            send_email(service, sender_email, receiver_email, subject, body)

    shutil.rmtree('tmp')
