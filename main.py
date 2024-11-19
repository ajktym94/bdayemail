import os
import io
import json
import shutil
import base64
import requests
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your email credentials
google_drive_file_id = os.environ.get("GDRIVE_FILE_ID")
MAIL_API = os.environ.get("MAIL_API")
API_ENDPOINT = os.environ['API_ENDPOINT']
SENDER = os.environ['SENDER']
RECEIVER = os.environ['RECEIVER']

def send_email(sender_email, receiver_email, subject, body):
    x = requests.post(
  		API_ENDPOINT,
  		auth=("api", MAIL_API),
  		data={"from": f"GKCYL Koln <{sender_email}>",
  			"to": [receiver_email],
  			"subject": subject,
  			"text": body})
    print(x.text)

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

    file_path = download_csv_from_drive(google_drive_file_id)
    birthdays = pd.read_csv(file_path)
    
    # Get today's date in YYYY-MM-DD format
    today = datetime.now()
    print(today)
    tomorrow = today + timedelta(days=1)

    # Check each entry in the CSV
    for _, row in birthdays.iterrows():
        if row['Birthday'] == tomorrow.strftime("%d-%m-%Y"):
            # Set email details
            sender_email = SENDER
            receiver_email = RECEIVER
            subject = "GKCYL Koln Unit Birthday Reminder"
            body = f"Tomorrow is the birthday of {row['Name']}"

            # Send the email
            send_email(sender_email, receiver_email, subject, body)

    shutil.rmtree('tmp')
