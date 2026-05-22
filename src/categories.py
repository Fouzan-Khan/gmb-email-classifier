"""Email classification taxonomy for personal email classifier."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str
    description: str
    folder: str  # IMAP folder/label name


CATEGORIES: list[Category] = [
    Category(
        name="Spam",
        folder="Spam",
        description=(
            "Unsolicited promotional emails, phishing attempts, scam messages, "
            "mass marketing with no opt-in, lottery/prize notifications, or "
            "obviously fake/fraudulent content."
        ),
    ),
    Category(
        name="Learning",
        folder="Learning",
        description=(
            "Emails related to education or skill-building: online course updates, "
            "tutorial newsletters, coding challenges, webinars, study resources, "
            "or content from platforms like Coursera, Udemy, YouTube, Khan Academy, "
            "or newsletters covering programming, tech, science, or other learning topics."
        ),
    ),
    Category(
        name="Jobs",
        folder="Jobs",
        description=(
            "Job-related emails where the user applied or engaged: application "
            "confirmations, interview invitations, offer letters, rejection notices, "
            "or status updates from job boards like LinkedIn, Indeed, or Glassdoor "
            "for roles the user actively applied to."
        ),
    ),
    Category(
        name="Recruiters",
        folder="Recruiters",
        description=(
            "Cold outreach from recruiters or headhunters: unsolicited messages "
            "about job opportunities, invitations to apply, or recruiter introductions "
            "from staffing agencies or HR professionals — distinct from jobs the user "
            "applied for themselves."
        ),
    ),
    Category(
        name="Personal",
        folder="Personal",
        description=(
            "Messages from friends, family, or personal acquaintances: casual "
            "conversation, social plans, personal updates, or any informal "
            "communication not related to work, business, or job searching."
        ),
    ),
    Category(
        name="Other",
        folder="Other",
        description="Emails that do not clearly fit any of the categories above.",
    ),
]

CATEGORY_MAP: dict[str, Category] = {cat.name: cat for cat in CATEGORIES}
CATEGORY_NAMES: list[str] = [cat.name for cat in CATEGORIES]
