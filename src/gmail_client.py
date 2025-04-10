import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


from auth import Auth
from utils import Utils
from db_connector import DB

class GmailClient:

    def __init__(self, creds_path=""):
        self.auth = Auth(credentials_file_path=creds_path)
        self.creds = self.auth.creds
        self.storage = DB()

    def mark_as_read(self, message_id):
        service = build("gmail", "v1", credentials=self.creds)
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()

    def move_to(self, message_id, label):
        service = build("gmail", "v1", credentials=self.creds)
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label]}
        ).execute()

    def fetch_emails(self):
        service = build("gmail", "v1", credentials=self.creds)
        threads = (
            service.users().threads().list(userId="me").execute().get("threads", [])
        )
        for thread in threads:
            tdata = (
              service.users().threads().get(userId="me", id=thread["id"]).execute()
            )
            nmsgs = len(tdata["messages"])

            subject = ""
            body = ""
            received_at = ""
            frm = ""
            from_name = ""
            from_email = ""
            message_id = tdata['messages'][0]['id']
            for h in tdata['messages'][0]['payload']['headers']:
                if h['name']=="Subject":
                    subject = h['value']
                if h['name']=="Date":
                    received_at = h['value']
                if h['name']=='From':
                    frm = h['value']
                    try:
                        from_email = frm.split("<")[-1].strip('>')
                        from_name = frm.split("<")[0].strip()
                    except Exception as err:
                        from_email = frm
                        from_name = frm
            payload = tdata['messages'][0]['payload']

            if 'parts' in payload:
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    if mime_type == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode("utf-8")
            else:
                # fallback if there's no parts
                data = payload['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8")

            cbody = Utils.clean_email_body(body)
            received_at = Utils.to_utc(received_at)
            print(f"Message ID: {message_id}\n")
            print(f"Received From: {from_email}\n")
            print(f"Received From name: {from_name}\n")
            print(f"Subject : {subject} \n")
            print(f"Body : {cbody} \n")
            print(f"Received at : {received_at}\n")

            print("\n###############################################################################################################\n")
 
            yield {
                    "message_id": message_id,
                    "from_email": from_email,
                    "from_name": from_name,
                    "subject": subject,
                    "body": cbody,
                    "received_at": received_at
                }
            #self.storage.save_email(message_id, from_email, from_name, subject, cbody, received_at)
       
if __name__=="__main__":
    gc = GmailClient()
    gc.fetch_emails()
