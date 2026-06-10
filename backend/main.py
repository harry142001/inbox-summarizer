from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from auth import authenticate, get_credentials
from gmail_client import fetch_unread_emails
from summarizer import summarize_all_emails
from database import init_db, get_db, EmailSummary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Inbox Summarizer API is running"}

@app.get("/auth/login")
def login():
    authenticate()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="http://localhost:5173")

@app.get("/auth/status")
def auth_status():
    creds = get_credentials()
    if creds and creds.valid:
        return {"authenticated": True}
    return {"authenticated": False}

@app.get("/emails/summarize")
def get_summarized_emails(db: Session = Depends(get_db)):
    creds = get_credentials()
    if not creds or not creds.valid:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        emails = fetch_unread_emails(max_results=10)
        new_emails = []
        cached_emails = []

        for email in emails:
            existing = db.query(EmailSummary).filter(
                EmailSummary.id == email['id']
            ).first()

            if existing:
                # Already summarized — load from database
                cached_emails.append({
                    'id': existing.id,
                    'subject': existing.subject,
                    'sender': existing.sender,
                    'summary': existing.summary,
                    'category': existing.category,
                    'priority': existing.priority,
                    'priority_reason': '',
                    'action_items': [],
                    'from_cache': True
                })
            else:
                new_emails.append(email)

        # Only call Claude for new emails
        freshly_summarized = []
        if new_emails:
            freshly_summarized = summarize_all_emails(new_emails)

            # Save new summaries to database
            for email in freshly_summarized:
                db_email = EmailSummary(
                    id=email['id'],
                    subject=email['subject'],
                    sender=email['sender'],
                    summary=email['summary'],
                    category=email['category'],
                    priority=email['priority']
                )
                db.add(db_email)
            db.commit()

        all_emails = freshly_summarized + cached_emails
        return {
            "emails": all_emails,
            "new": len(freshly_summarized),
            "cached": len(cached_emails)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/history")
def get_history(db: Session = Depends(get_db)):
    emails = db.query(EmailSummary).order_by(
        EmailSummary.created_at.desc()
    ).all()
    return {"emails": [
        {
            "id": e.id,
            "subject": e.subject,
            "sender": e.sender,
            "summary": e.summary,
            "category": e.category,
            "priority": e.priority,
            "created_at": e.created_at
        } for e in emails
    ]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)