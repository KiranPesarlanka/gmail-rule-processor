from gmail_client import GmailClient
from db_connector import DB


def extract_emails(creds_path):
    
    gc = GmailClient(creds_path)
    db = DB()

    for email_dict in gc.fetch_emails():

        db.save_email(
                        message_id=email_dict['message_id'],
                        from_email=email_dict['from_email'], 
                        from_name=email_dict['from_name'], 
                        subject=email_dict['subject'], 
                        body=email_dict['body'], 
                        received_at=email_dict['received_at']
                    )
        print(f"Inserted Message ID: {email_dict['message_id']}")

creds_path = "credentials.json"
extract_emails(creds_path)
