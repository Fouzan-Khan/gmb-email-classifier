"""Gmail IMAP client: fetch unread emails, classify them, and file into folders."""

import email
import imaplib
import os
from email import policy

from dotenv import load_dotenv

from .categories import CATEGORY_MAP
from .classifier import ClassificationResult, classify_email

load_dotenv()

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993


def _get_credentials() -> tuple[str, str]:
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    if not user or not password:
        raise EnvironmentError(
            "EMAIL_USER and EMAIL_PASSWORD must be set in your .env file.\n"
            "For Gmail, generate an App Password at:\n"
            "  https://myaccount.google.com/apppasswords\n"
            "(Requires 2-Step Verification to be enabled on your Google account.)"
        )
    return user, password


def _folder_exists(conn: imaplib.IMAP4_SSL, folder: str) -> bool:
    status, data = conn.list('""', folder)
    return status == "OK" and bool(data and data[0])


def _ensure_folder(conn: imaplib.IMAP4_SSL, folder: str) -> None:
    """Create an IMAP folder (Gmail label) if it doesn't already exist."""
    if not _folder_exists(conn, folder):
        conn.create(folder)
        conn.subscribe(folder)


def _extract_text(msg) -> str:
    """Return the plain-text body from a (possibly multipart) email."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="replace")
    payload = msg.get_payload(decode=True)
    if payload:
        return payload.decode(errors="replace")
    return ""


def run_classifier(limit: int = 50, unread_only: bool = True) -> list[dict]:
    """
    Connect to Gmail, classify INBOX emails, and move each to its folder.

    Args:
        limit: Maximum number of emails to process (most recent first).
        unread_only: If True (default), only process unread emails. If False, process all.

    Returns:
        List of result dicts with keys: subject, category, confidence, reason, folder.
        On per-email errors the dict has keys: subject, error.
    """
    user, password = _get_credentials()
    results: list[dict] = []

    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as conn:
        conn.login(user, password)
        conn.select("INBOX")

        search_criterion = "UNSEEN" if unread_only else "ALL"
        status, data = conn.uid("SEARCH", None, search_criterion)
        if status != "OK" or not data[0]:
            return results

        uids = data[0].split()
        # Process most recent first, up to limit
        uids = uids[-limit:][::-1]

        # Phase 1: fetch and classify all emails
        classified: list[tuple[bytes, str, ClassificationResult]] = []
        for uid in uids:
            status, raw = conn.uid("FETCH", uid, "(RFC822)")
            if status != "OK" or not raw or not raw[0]:
                continue

            msg = email.message_from_bytes(raw[0][1], policy=policy.default)
            subject = str(msg.get("Subject", "(no subject)"))
            body = _extract_text(msg)

            try:
                result = classify_email(subject, body[:3000])
                classified.append((uid, subject, result))
            except Exception as exc:
                results.append({"subject": subject, "error": str(exc)})

        # Phase 2: ensure all needed folders exist (uses LIST, no mailbox change)
        needed_folders = {CATEGORY_MAP[r.category].folder for _, _, r in classified}
        for folder in needed_folders:
            _ensure_folder(conn, folder)

        # Phase 3: re-select INBOX and move each email
        conn.select("INBOX")
        for uid, subject, result in classified:
            folder = CATEGORY_MAP[result.category].folder
            conn.uid("COPY", uid, folder)
            conn.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
            results.append({
                "subject": subject,
                "category": result.category,
                "confidence": result.confidence,
                "reason": result.reason,
                "folder": folder,
            })

        conn.expunge()

    return results
