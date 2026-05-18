"""Email classification taxonomy for the enterprise email classifier."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str
    description: str


CATEGORIES: list[Category] = [
    Category(
        name="Invoice",
        description=(
            "Financial documents: vendor invoices, payment requests, "
            "billing statements, purchase orders, or payment reminders."
        ),
    ),
    Category(
        name="HR Query",
        description=(
            "Human resources topics: leave requests, payroll questions, "
            "benefits, onboarding, performance reviews, or HR policy."
        ),
    ),
    Category(
        name="IT Support",
        description=(
            "Technical help requests: hardware or software issues, "
            "password resets, VPN access problems, or system outages."
        ),
    ),
    Category(
        name="Client Request",
        description=(
            "Incoming requests, questions, complaints, or feedback from "
            "external clients about products, services, or deliverables."
        ),
    ),
    Category(
        name="Internal Announcement",
        description=(
            "Company-wide or team communications: policy updates, event "
            "invitations, org changes, or general internal notices."
        ),
    ),
    Category(
        name="Spam",
        description=(
            "Unsolicited promotional emails, phishing attempts, scam "
            "messages, or irrelevant mass mailings."
        ),
    ),
    Category(
        name="Other",
        description="Emails that do not clearly fit any of the categories above.",
    ),
]

# Lookup helpers used by the classifier and tests
CATEGORY_MAP: dict[str, Category] = {cat.name: cat for cat in CATEGORIES}
CATEGORY_NAMES: list[str] = [cat.name for cat in CATEGORIES]
