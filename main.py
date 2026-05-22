"""Personal email classifier — one-shot CLI entry point.

Usage:
    python main.py           # process unread emails only (default)
    python main.py --all     # process all emails in INBOX

Set the following in your .env file:
    GROQ_API_KEY   — from https://console.groq.com
    EMAIL_USER     — your Gmail address (e.g. you@gmail.com)
    EMAIL_PASSWORD — a Gmail App Password (NOT your regular password)
                     Generate one at: https://myaccount.google.com/apppasswords
"""

import argparse

from src.imap_client import run_classifier


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and file Gmail inbox emails.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all emails in INBOX, not just unread ones.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of emails to process (default: 50).",
    )
    args = parser.parse_args()

    unread_only = not args.all
    scope = "all" if args.all else "unread"
    print(f"Connecting to Gmail and fetching {scope} emails...\n")

    try:
        results = run_classifier(limit=args.limit, unread_only=unread_only)
    except EnvironmentError as exc:
        print(f"Configuration error:\n{exc}")
        return

    if not results:
        print(f"No {scope} emails found in INBOX.")
        return

    errors = [r for r in results if "error" in r]
    ok = [r for r in results if "error" not in r]

    print(f"Processed {len(results)} email(s) — {len(ok)} classified, {len(errors)} failed.\n")

    for r in ok:
        pct = f"{r['confidence']:.0%}"
        print(f"  [{r['category']:<11}] ({pct:>4}) → {r['folder']}")
        print(f"    Subject : {r['subject']}")
        print(f"    Reason  : {r['reason']}\n")

    if errors:
        print("Errors:")
        for r in errors:
            print(f"  [ERROR] {r['subject']!r} — {r['error']}")


if __name__ == "__main__":
    main()
