"""
Integration tests for the email classifier.

Each test sends a realistic synthetic email to the Groq API and asserts:
  - The returned category matches the expected label
  - The confidence score is a valid float in [0.0, 1.0]
  - The reason is a non-empty string

Run with:
    pytest tests/ -v
"""

import pytest

from src.classifier import ClassificationResult, classify_email


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _assert_result(result: ClassificationResult, expected_category: str) -> None:
    assert result.category == expected_category, (
        f"Expected '{expected_category}', got '{result.category}'. "
        f"Reason: {result.reason}"
    )
    assert 0.0 <= result.confidence <= 1.0, (
        f"Confidence {result.confidence} is outside [0, 1]"
    )
    assert isinstance(result.reason, str) and result.reason.strip(), (
        "Reason must be a non-empty string"
    )


# ---------------------------------------------------------------------------
# Invoice (2 tests)
# ---------------------------------------------------------------------------

def test_invoice_vendor_billing():
    result = classify_email(
        subject="Invoice #INV-2024-0892 for Office Supplies — Due June 15",
        body=(
            "Dear Accounts Payable Team,\n\n"
            "Please find attached invoice #INV-2024-0892 from Acme Office Supplies "
            "for the delivery of printer cartridges, paper, and desk accessories. "
            "Total amount due: $1,247.50. Payment terms: Net 30 from invoice date (May 16, 2024).\n\n"
            "Please remit payment to the bank account details listed on the attached invoice. "
            "For questions, contact billing@acmesupplies.com.\n\n"
            "Thank you for your business.\n"
            "— Acme Office Supplies Billing Department"
        ),
    )
    _assert_result(result, "Invoice")


def test_invoice_overdue_payment_reminder():
    result = classify_email(
        subject="SECOND NOTICE: Overdue Payment — Invoice #5571",
        body=(
            "This is a reminder that invoice #5571 issued on April 1, 2024 "
            "for $3,800.00 remains unpaid and is now 45 days overdue. "
            "Your contracted payment terms require settlement within 30 days of invoice date.\n\n"
            "Please process payment immediately to avoid service interruption and late fees "
            "of 1.5% per month. If payment has already been sent, please share the transaction "
            "reference.\n\n"
            "Contact our accounts receivable team at ar@techservices.io."
        ),
    )
    _assert_result(result, "Invoice")


# ---------------------------------------------------------------------------
# HR Query (1 test)
# ---------------------------------------------------------------------------

def test_hr_query_maternity_leave():
    result = classify_email(
        subject="Maternity Leave Request — Starting September 2, 2024",
        body=(
            "Hi Sarah,\n\n"
            "I wanted to formally notify HR of my intent to take maternity leave beginning "
            "September 2, 2024. My due date is August 25, and I plan to take the full 16 weeks "
            "of paid leave as outlined in our company policy.\n\n"
            "I've already briefed my manager, David Chen, and we're working on a handover plan. "
            "Could you please send me the relevant forms and confirm the leave dates in our HR "
            "system? I'd also like to understand the process for maintaining my benefits during "
            "the leave period.\n\n"
            "Thank you,\nEmily Watson"
        ),
    )
    _assert_result(result, "HR Query")


# ---------------------------------------------------------------------------
# IT Support (2 tests)
# ---------------------------------------------------------------------------

def test_it_support_password_reset():
    result = classify_email(
        subject="URGENT: Locked Out of Corporate Account — Password Reset Needed",
        body=(
            "Hello IT Support,\n\n"
            "I have been locked out of my corporate account since this morning. "
            "I believe my password expired and the self-service reset portal is returning "
            "the error: 'Reset token invalid.'\n\n"
            "I need access urgently as I have client calls scheduled for today. "
            "My employee ID is EMP-4821, username: m.johnson@company.com.\n\n"
            "Please reset my password or walk me through the fix as soon as possible.\n\n"
            "— Michael Johnson, Sales Team"
        ),
    )
    _assert_result(result, "IT Support")


def test_it_support_laptop_boot_failure():
    result = classify_email(
        subject="Laptop Won't Boot After Last Night's Windows Update",
        body=(
            "Hi IT,\n\n"
            "My Dell Latitude 5420 failed to start this morning after automatically installing "
            "a Windows 11 update overnight. It is stuck at the loading screen with a spinning "
            "circle and never reaches the desktop. I've tried a hard reboot twice with no success.\n\n"
            "Asset tag: LT-00342. I have a presentation in two hours and urgently need a working "
            "machine or remote assistance. Please advise.\n\n"
            "Thanks,\nSandra Lee, Product Team"
        ),
    )
    _assert_result(result, "IT Support")


# ---------------------------------------------------------------------------
# Client Request (2 tests)
# ---------------------------------------------------------------------------

def test_client_request_feature_request():
    result = classify_email(
        subject="Feature Request: Bulk CSV Export for Monthly Reports",
        body=(
            "Hi Product Team,\n\n"
            "As one of your enterprise clients, we have been using your platform for six months "
            "and are overall very happy. However, our finance team struggles each month because "
            "there is no way to export transaction data in bulk to CSV. We currently export each "
            "account individually, which takes hours for our 200+ accounts.\n\n"
            "Could you prioritise adding a bulk export feature? It would save us significant time "
            "and could be a strong differentiator for other enterprise customers as well. "
            "Happy to jump on a call to discuss requirements.\n\n"
            "Best regards,\nJames Harrington, CFO — Harrington & Associates"
        ),
    )
    _assert_result(result, "Client Request")


def test_client_request_billing_complaint():
    result = classify_email(
        subject="Complaint: Double Charged on April Invoice",
        body=(
            "To whom it may concern,\n\n"
            "I've noticed that our company was charged twice for the Professional Plan "
            "subscription in April — on both April 1 and April 14. Our account number is "
            "ACC-77821. I've attached screenshots from our bank statement showing both charges "
            "totalling $598.\n\n"
            "This has never happened before and I expect a full refund of the duplicate charge "
            "within 5 business days. Please acknowledge this email and provide a resolution "
            "timeline.\n\n"
            "Regards,\nPriya Mehta, Finance Manager — GlobalLogix Inc."
        ),
    )
    _assert_result(result, "Client Request")


# ---------------------------------------------------------------------------
# Internal Announcement (1 test)
# ---------------------------------------------------------------------------

def test_internal_announcement_all_hands():
    result = classify_email(
        subject="All-Hands Meeting: Thursday, May 22 at 2:00 PM — Q2 Review & Roadmap",
        body=(
            "Dear Team,\n\n"
            "You are invited to our Q2 All-Hands meeting this Thursday, May 22 at 2:00 PM "
            "in the Main Auditorium (and live on Zoom for remote employees).\n\n"
            "CEO Mark Williams will present our Q2 financial results, followed by a deep-dive "
            "into the H2 strategic roadmap from the leadership team. We will also be recognising "
            "top performers from across the company.\n\n"
            "Attendance is mandatory for all full-time employees. The Zoom link and agenda have "
            "been shared via calendar invite. Light refreshments will be served in person.\n\n"
            "— People & Culture Team"
        ),
    )
    _assert_result(result, "Internal Announcement")


# ---------------------------------------------------------------------------
# Spam (1 test)
# ---------------------------------------------------------------------------

def test_spam_gift_card_scam():
    result = classify_email(
        subject="WINNER! Claim Your $10,000 Amazon Gift Card — Limited Time!!!",
        body=(
            "CONGRATULATIONS!!!\n\n"
            "You have been selected as our GRAND PRIZE WINNER in our annual customer "
            "appreciation draw! You are entitled to a $10,000 Amazon Gift Card!!!\n\n"
            "To claim your prize, click the link below within 24 HOURS or your reward will "
            "be forfeited. Hurry — only 3 slots remaining!!!\n\n"
            "CLAIM NOW: http://amaz0n-rewards-claim.xyz/winner\n"
            "Your prize ID: GP-981234\n\n"
            "Note: A small processing fee of $29.99 is required to release your reward."
        ),
    )
    _assert_result(result, "Spam")


# ---------------------------------------------------------------------------
# Other (1 test)
# ---------------------------------------------------------------------------

def test_other_personal_message():
    result = classify_email(
        subject="Re: Weekend Hiking Plans — Trail Recommendation",
        body=(
            "Hey Alex,\n\n"
            "I checked out the trails you mentioned and I think Blue Ridge Loop is the way "
            "to go this Saturday. It's about 8 miles, moderate difficulty, and the views at "
            "the summit are supposed to be incredible this time of year.\n\n"
            "I'll pack extra water and snacks for everyone. Want to carpool from the office "
            "parking lot at 7am? Let me know!\n\n"
            "— Chris"
        ),
    )
    _assert_result(result, "Other")
