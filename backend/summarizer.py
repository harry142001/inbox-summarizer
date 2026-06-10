import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def summarize_email(subject: str, sender: str, body: str) -> dict:
    prompt = f"""You are an expert email assistant. Analyze this email and respond with ONLY a JSON object, no other text, no markdown, no backticks.

From: {sender}
Subject: {subject}
Body: {body[:2000]}

Respond with exactly this JSON structure:
{{
  "summary": "one sentence summary of the email in max 20 words",
  "action_items": ["action 1", "action 2"],
  "category": "one of: Work, Newsletter, Finance, Personal, Spam",
  "priority": 5,
  "priority_reason": "one sentence explaining the priority score"
}}"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text.strip()
    
    # Remove markdown backticks if Claude adds them
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    
    try:
        return json.loads(response_text)
    except:
        # Fallback if parsing fails
        return {
            "summary": subject,
            "action_items": [],
            "category": "Uncategorized",
            "priority": 5,
            "priority_reason": "Could not analyze"
        }
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text
    return json.loads(response_text)

def summarize_all_emails(emails: list) -> list:
    summarized = []
    for email in emails:
        result = summarize_email(
            subject=email['subject'],
            sender=email['sender'],
            body=email['body']
        )
        summarized.append({
            'id': email['id'],
            'subject': email['subject'],
            'sender': email['sender'],
            'summary': result.get('summary', ''),
            'action_items': result.get('action_items', []),
            'category': result.get('category', 'Uncategorized'),
            'priority': result.get('priority', 5),
            'priority_reason': result.get('priority_reason', '')
        })
    return summarized