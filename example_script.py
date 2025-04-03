import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/gmail.send']

def get_services():
    flow = InstalledAppFlow.from_client_secrets_file('MyCredentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    sheets_service = build('sheets', 'v4', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    return sheets_service, gmail_service

def read_responses(sheets_service, spreadsheet_id, range_name):
    result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

def send_email(gmail_service, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    gmail_service.users().messages().send(userId='me', body=body).execute()

def main():
    SPREADSHEET_ID = '1721Vqb7iNruCoVdJA8MJW3FTd1tFh_nf6s9qUrKLgzs'
    RANGE_NAME = 'Sheet1!A1:D'

    sheets_service, gmail_service = get_services()
    responses = read_responses(sheets_service, SPREADSHEET_ID, RANGE_NAME)
    headers = responses[0]
    for row in responses[1:]:
        try:
            email_submitter = row[1]
            email_destination = row[2]
            feedback_message = row[3]

            email_body = (
                f"Thank you for your submission!\n\n"
                f"Submitter: {email_submitter}\n"
                f"Message: {feedback_message}\n"
            )

            send_email(gmail_service, email_destination, "Your Form Response", email_body)
            print(f"Email sent to {email_destination}")
        except IndexError:
            print("Skipping incomplete row:", row)

if __name__ == '__main__':
    main()
