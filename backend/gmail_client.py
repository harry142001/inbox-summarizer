from googleapiclient.discovery import build
from auth import get_credentials
import base64

def get_gmail_service():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_unread_emails(max_results=10):
    service = get_gmail_service()
    
    # Get list of unread emails
    results = service.users().messages().list(
        userId='me',
        labelIds=['UNREAD'],
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    emails = []
    
    for msg in messages:
        # Fetch full email details
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        
        # Extract subject and sender
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        
        # Extract email body
        body = extract_body(message)
        
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'body': body
        })
    
    return emails

def extract_body(message):
    try:
        parts = message['payload'].get('parts', [])
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            # If no plain text part found, try HTML part
            for part in parts:
                if part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = message['payload']['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        return "No email body found"
    except:
        return "Could not extract email body"