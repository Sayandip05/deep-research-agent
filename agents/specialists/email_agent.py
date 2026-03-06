"""
agents/specialists/email_agent.py
Reads and sends email via Gmail API. Extracts meeting info from threads.
"""

from __future__ import annotations
import base64
import os
import structlog
from typing import Any

logger = structlog.get_logger()


def _get_gmail_service():
    """Build an authenticated Gmail service client."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "config"))
    from settings import settings

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    # Expects token.json to exist (created via OAuth flow)
    token_path = os.path.join(os.path.dirname(__file__), "..", "..", "credentials", "gmail_token.json")
    if not os.path.exists(token_path):
        raise FileNotFoundError(
            f"Gmail token not found at {token_path}. Run the OAuth flow first."
        )

    creds = Credentials.from_authorized_user_file(
        token_path,
        scopes=["https://www.googleapis.com/auth/gmail.modify"]
    )
    return build("gmail", "v1", credentials=creds)


async def read_recent_emails(params: dict) -> dict:
    """Fetch recent emails from Gmail."""
    max_results = params.get("max_results", 10)
    query = params.get("query", "")

    try:
        import asyncio
        service = await asyncio.get_event_loop().run_in_executor(None, _get_gmail_service)

        result = service.users().messages().list(
            userId="me",
            maxResults=max_results,
            q=query or "is:unread",
        ).execute()

        messages = result.get("messages", [])
        emails = []

        for msg in messages[:max_results]:
            full = service.users().messages().get(
                userId="me", id=msg["id"], format="full"
            ).execute()

            headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
            snippet = full.get("snippet", "")

            emails.append({
                "id": msg["id"],
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": snippet,
            })

        logger.info("email.read_recent", count=len(emails))
        return {"emails": emails}

    except FileNotFoundError as e:
        return {"error": str(e), "emails": []}
    except Exception as e:
        logger.error("email.read_error", error=str(e))
        return {"error": str(e), "emails": []}


async def send_email(params: dict) -> dict:
    """Send an email via Gmail."""
    to = params.get("to", "")
    subject = params.get("subject", "")
    body = params.get("body", "")

    if not all([to, subject, body]):
        return {"error": "Missing required fields: to, subject, body"}

    try:
        import asyncio
        from email.mime.text import MIMEText

        service = await asyncio.get_event_loop().run_in_executor(None, _get_gmail_service)

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        result = service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

        logger.info("email.sent", to=to, subject=subject)
        return {"message_id": result["id"], "success": True}

    except Exception as e:
        logger.error("email.send_error", error=str(e))
        return {"error": str(e), "success": False}


async def extract_meeting_info(params: dict) -> dict:
    """Use LLM to extract meeting info from an email."""
    email_id = params.get("email_id", "")
    # TODO: fetch full email body and run LLM extraction
    return {"proposed_time": None, "participants": [], "location": None,
            "note": "LLM extraction not yet implemented"}
