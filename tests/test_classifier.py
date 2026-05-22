"""
Integration tests for the personal email classifier.

Each test sends a realistic synthetic email to the Groq API and asserts:
  - The returned category matches the expected label
  - The confidence score is a valid float in [0.0, 1.0]
  - The reason is a non-empty string

Run with:
    pytest tests/ -v
"""

import pytest

from src.classifier import ClassificationResult, classify_email


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
# Spam (2 tests)
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


def test_spam_pharma_promotion():
    result = classify_email(
        subject="Lowest prices on Rx meds — no prescription needed!",
        body=(
            "Dear Valued Customer,\n\n"
            "Get brand-name medications at 90% off retail prices — no prescription required! "
            "Shipped discreetly to your door within 3 days.\n\n"
            "Click here to browse our catalog: http://cheap-pharma-direct.biz/shop\n\n"
            "Unsubscribe: http://cheap-pharma-direct.biz/unsub?id=8829"
        ),
    )
    _assert_result(result, "Spam")


# ---------------------------------------------------------------------------
# Learning (2 tests)
# ---------------------------------------------------------------------------

def test_learning_course_update():
    result = classify_email(
        subject="Your Coursera course — Week 3 materials are now available",
        body=(
            "Hi Fouzan,\n\n"
            "Week 3 of 'Machine Learning Specialization' is now unlocked. This week covers:\n"
            "  • Neural networks and deep learning fundamentals\n"
            "  • Backpropagation explained step by step\n"
            "  • Lab: Building your first neural net in Python\n\n"
            "Estimated time: 4 hours. Deadline: Sunday at 11:59 PM.\n\n"
            "Go to course → https://www.coursera.org/learn/machine-learning\n\n"
            "Happy learning!\n— The Coursera Team"
        ),
    )
    _assert_result(result, "Learning")


def test_learning_tech_newsletter():
    result = classify_email(
        subject="This week in AI: GPT-5 benchmarks, new open-source models & more",
        body=(
            "Hello,\n\n"
            "Here's your weekly digest of what's happening in AI and machine learning:\n\n"
            "1. GPT-5 benchmarks leaked — what they mean for developers\n"
            "2. Mistral releases a new 7B model outperforming GPT-3.5\n"
            "3. Tutorial: Fine-tuning LLMs on your own data with LoRA\n"
            "4. Paper of the week: 'Scaling Laws for Neural Language Models'\n\n"
            "Read more at: https://aiweekly.co/issues/301\n\n"
            "You're receiving this because you subscribed at aiweekly.co.\n"
            "Unsubscribe | Manage preferences"
        ),
    )
    _assert_result(result, "Learning")


# ---------------------------------------------------------------------------
# Jobs (2 tests)
# ---------------------------------------------------------------------------

def test_jobs_interview_invitation():
    result = classify_email(
        subject="Interview Invitation — Software Engineer at Stripe",
        body=(
            "Hi Fouzan,\n\n"
            "Thank you for applying to the Software Engineer — Payments Infrastructure role at Stripe. "
            "We've reviewed your application and would love to move forward with a technical screen.\n\n"
            "Please use the link below to schedule a 45-minute technical interview with one of our "
            "engineers at your convenience:\n\n"
            "Schedule: https://stripe.com/interview/schedule?token=abc123\n\n"
            "The interview will cover data structures, algorithms, and system design. "
            "Slots are available this week and next.\n\n"
            "Looking forward to speaking with you.\n\n"
            "Best,\nSarah Kim\nTechnical Recruiting, Stripe"
        ),
    )
    _assert_result(result, "Jobs")


def test_jobs_application_rejection():
    result = classify_email(
        subject="Update on your application — Backend Engineer at Notion",
        body=(
            "Hi Fouzan,\n\n"
            "Thank you for taking the time to apply for the Backend Engineer position at Notion "
            "and for the conversations we've had throughout the process.\n\n"
            "After careful consideration, we've decided to move forward with other candidates "
            "whose experience more closely matches our current needs. This was a difficult decision "
            "given the strength of your background.\n\n"
            "We'll keep your profile on file and encourage you to apply again in the future. "
            "We wish you the very best in your job search.\n\n"
            "Warm regards,\nNotion Recruiting Team"
        ),
    )
    _assert_result(result, "Jobs")


# ---------------------------------------------------------------------------
# Recruiters (2 tests)
# ---------------------------------------------------------------------------

def test_recruiters_linkedin_outreach():
    result = classify_email(
        subject="Exciting opportunity at a Series B startup — are you open to a chat?",
        body=(
            "Hi Fouzan,\n\n"
            "I came across your profile on LinkedIn and was really impressed by your background "
            "in backend engineering and distributed systems.\n\n"
            "I'm a technical recruiter at TalentBridge and I'm working with a Series B fintech "
            "startup (YC W22, $40M raised) that's looking for a Senior Backend Engineer. "
            "They're offering a very competitive comp package: $180k–$220k base + equity.\n\n"
            "Would you be open to a quick 15-minute call this week to see if there could be a fit?\n\n"
            "Best,\nJessica Park\nSenior Technical Recruiter, TalentBridge\njessp@talentbridge.io"
        ),
    )
    _assert_result(result, "Recruiters")


def test_recruiters_agency_blast():
    result = classify_email(
        subject="Are you looking for your next role? We have 200+ open positions!",
        body=(
            "Hello,\n\n"
            "My name is Mark and I'm a recruiter at DevHire Solutions. We specialize in placing "
            "software engineers at top tech companies across the country.\n\n"
            "Based on your skills, I think you'd be a great fit for several open roles we're "
            "currently filling — including positions at FAANG companies and hot startups.\n\n"
            "If you're open to exploring new opportunities, reply to this email with your resume "
            "and I'll reach out with the best matches for your profile.\n\n"
            "Regards,\nMark Torres | DevHire Solutions\nmark@devhire.io | +1 (555) 012-3456"
        ),
    )
    _assert_result(result, "Recruiters")


# ---------------------------------------------------------------------------
# Personal (1 test)
# ---------------------------------------------------------------------------

def test_personal_friend_message():
    result = classify_email(
        subject="Re: Weekend Hiking Plans — Trail Recommendation",
        body=(
            "Hey Fouzan,\n\n"
            "I checked out the trails you mentioned and I think Blue Ridge Loop is the way "
            "to go this Saturday. It's about 8 miles, moderate difficulty, and the views at "
            "the summit are supposed to be incredible this time of year.\n\n"
            "I'll pack extra water and snacks for everyone. Want to carpool from the coffee "
            "shop at 7am? Let me know!\n\n"
            "— Chris"
        ),
    )
    _assert_result(result, "Personal")


# ---------------------------------------------------------------------------
# Other (1 test)
# ---------------------------------------------------------------------------

def test_other_utility_bill():
    result = classify_email(
        subject="Your electricity bill for May is ready",
        body=(
            "Dear Customer,\n\n"
            "Your electricity bill for the period April 1 – April 30 is now available.\n\n"
            "Amount due: $87.42\n"
            "Due date: May 15, 2024\n\n"
            "You can view and pay your bill at https://myaccount.citypower.com.\n\n"
            "Thank you,\nCity Power & Light"
        ),
    )
    _assert_result(result, "Other")
