"""Personal email classifier powered by Groq's Llama 3.3-70B model."""

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from groq import Groq

from .categories import CATEGORIES, CATEGORY_MAP

load_dotenv()

# Shared client — initialized once on first call to avoid repeated instantiation
_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. Add it to your .env file or environment."
            )
        _client = Groq(api_key=api_key)
    return _client


def _build_system_prompt() -> str:
    category_block = "\n".join(
        f"  - {cat.name}: {cat.description}" for cat in CATEGORIES
    )
    #print(f"------------------------------------------{category_block}")
    return (
        "You are a personal email classification system.\n"
        "Classify the email into exactly one of the following categories:\n"
        f"{category_block}\n\n"
        "Respond with a JSON object and nothing else — no markdown, no extra text:\n"
        "{\n"
        '  "category": "<one of the category names above>",\n'
        '  "confidence": <float between 0.0 and 1.0>,\n'
        '  "reason": "<one-sentence explanation>"\n'
        "}"
    )


@dataclass
class ClassificationResult:
    category: str
    confidence: float  # 0.0 – 1.0
    reason: str

    def __str__(self) -> str:
        return f"[{self.category}] ({self.confidence:.0%} confidence) — {self.reason}"


def classify_email(subject: str, body: str) -> ClassificationResult:
    """Classify an email into a predefined enterprise category.

    Args:
        subject: The email subject line.
        body: The full email body text.

    Returns:
        ClassificationResult with category, confidence score (0–1), and reason.

    Raises:
        EnvironmentError: If GROQ_API_KEY is not configured.
        ValueError: If the model returns a response that cannot be parsed.
    """
    client = _get_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _build_system_prompt()},
            {"role": "user", "content": f"Subject: {subject}\n\nBody:\n{body}"},
        ],
        temperature=0.1,  # low temperature for deterministic, consistent outputs
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model returned non-JSON response: {raw!r}") from exc

    # Validate and normalise category
    category = data.get("category", "Other")
    if category not in CATEGORY_MAP:
        category = "Other"

    # Clamp confidence to [0.0, 1.0] regardless of what the model says
    confidence = float(data.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))

    reason = data.get("reason", "No reason provided.")

    return ClassificationResult(category=category, confidence=confidence, reason=reason)
