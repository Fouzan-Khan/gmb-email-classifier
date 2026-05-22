# Personal Email Classifier <!-- v2.0.0 -->

A personal inbox classifier that connects to your Gmail account, reads unread emails, categorises each one using Groq's Llama 3.3-70B model, auto-creates folders, and files every email into the right place — no manual sorting required.

---

## Why This Exists

Personal inboxes are noisy. Spam, recruiter cold-outreach, job alerts, learning newsletters, and messages from friends all arrive in the same pile. This tool reads each unread email, decides what it is, and moves it to a dedicated Gmail folder — so your inbox stays clean without any manual effort.

---

## How It Works

```
Gmail INBOX (unread emails)
        │
        ▼
┌───────────────────────┐
│   IMAP Client         │  Fetches unread emails via
│   imap_client.py      │  imap.gmail.com:993 (SSL)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   Prompt Builder      │  Assembles a system prompt from the
│   classifier.py       │  category taxonomy (name + description
│                       │  for each of 6 personal categories)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   Groq Inference API  │  llama-3.3-70b-versatile
│   temperature = 0.1   │  response_format: json_object
│   (deterministic)     │  ~300–500 ms per call
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   Response Parser     │  Validates JSON, normalises category,
│   & Validator         │  clamps confidence to [0.0, 1.0]
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   Folder Manager      │  Creates Gmail label if it doesn't
│   imap_client.py      │  exist, then moves email out of INBOX
└───────────────────────┘
```

The classifier is stateless. There is no database, no training loop, and no vector store. It relies entirely on Llama 3.3-70B's instruction-following capability with a structured taxonomy prompt and enforced JSON output.

---

## Categories

| Folder | What goes there |
|---|---|
| **Spam** | Unsolicited promotions, phishing attempts, scam messages, mass marketing |
| **Learning** | Course updates, tech newsletters, webinars, coding challenges, educational content |
| **Jobs** | Application confirmations, interview invites, offer letters, job board alerts for roles you applied to |
| **Recruiters** | Cold outreach from recruiters and headhunters — roles you did not apply for |
| **Personal** | Messages from friends, family, or personal acquaintances |
| **Other** | Anything that does not clearly fit the above (security alerts, utility bills, etc.) |

---

## Tech Stack

| Component | Choice | Reason |
|---|---|---|
| Language | Python 3.11 | Typed dataclasses, clean structure |
| LLM | Llama 3.3-70B (`llama-3.3-70b-versatile`) | Strong instruction following; top open-weight model for structured output |
| Inference | [Groq API](https://groq.com) | Sub-500ms latency at 70B scale; no GPU required |
| Email access | `imaplib` (stdlib) | Standard IMAP over SSL — no extra dependencies |
| Output enforcement | `response_format: json_object` | Eliminates markdown wrapping and hallucinated schema |
| Config | `python-dotenv` | Keeps secrets out of source |
| Tests | `pytest` (integration, live API) | Validates end-to-end classification behaviour |

---

## Project Structure

```
personal-email-classifier/
├── src/
│   ├── classifier.py      # Core classification logic and Groq client
│   ├── categories.py      # Category taxonomy (names, descriptions, folder map)
│   └── imap_client.py     # Gmail IMAP: fetch, classify, create folders, move emails
├── tests/
│   └── test_classifier.py # 10 integration tests across all 6 categories
├── main.py                # One-shot CLI entry point
├── .env                   # Credentials (not committed)
├── requirements.txt
└── pyproject.toml
```

---

## Installation

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com) (free tier is sufficient)
- A Gmail account with:
  - IMAP enabled: Gmail Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP
  - An [App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification)

### Setup

```bash
# Clone the repository
git clone https://github.com/fouzan-khan/gmb-email-classifier.git
cd gmb-email-classifier

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure credentials

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key_here

EMAIL_USER=you@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password, NOT your regular password
```

> **Generating a Gmail App Password**
> 1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 2. Select app: **Mail**, device: **Other** → name it anything
> 3. Copy the 16-character password into `EMAIL_PASSWORD`

---

## Usage

```bash
python main.py
```

The script will:
1. Connect to your Gmail inbox over IMAP
2. Fetch up to 50 unread emails
3. Classify each one using Llama 3.3-70B
4. Create the destination Gmail folder/label if it doesn't exist
5. Move the email out of INBOX into the correct folder
6. Print a formatted summary

### Example output

```
Connecting to Gmail and fetching unread emails...

Processed 50 email(s) — 50 classified, 0 failed.

  [Spam       ] ( 99%) → Spam
    Subject : ⏳ Fouzan, ₹2750 Vouchers + Lifetime FREE Credit Card!
    Reason  : Promotional message with a voucher offer and call to action.

  [Jobs       ] ( 90%) → Jobs
    Subject : New jobs posted from careers.hydroone.com
    Reason  : Job alert from a company career portal matching saved search criteria.

  [Recruiters ] ( 95%) → Recruiters
    Subject : AI Engineer (Fresher) @ AAPNA Infotech
    Reason  : Unsolicited message about a job opportunity from a recruiter.

  [Learning   ] ( 90%) → Learning
    Subject : Beyond the Notebook: Shipping AI Agents to Production (Part 2)
    Reason  : Notification about an upcoming educational webinar on AI engineering.

  [Personal   ] ( 90%) → Personal
    Subject : Graduation Pool Party & Farewell — Friday 5PM
    Reason  : Personal invitation to a social event from an acquaintance.
```

---

## Tests

10 live integration tests call the Groq API with realistic synthetic emails and assert correct category, valid confidence range, and a non-empty reason.

```bash
pytest tests/ -v
```

```
tests/test_classifier.py::test_spam_gift_card_scam           PASSED
tests/test_classifier.py::test_spam_pharma_promotion         PASSED
tests/test_classifier.py::test_learning_course_update        PASSED
tests/test_classifier.py::test_learning_tech_newsletter      PASSED
tests/test_classifier.py::test_jobs_interview_invitation     PASSED
tests/test_classifier.py::test_jobs_application_rejection    PASSED
tests/test_classifier.py::test_recruiters_linkedin_outreach  PASSED
tests/test_classifier.py::test_recruiters_agency_blast       PASSED
tests/test_classifier.py::test_personal_friend_message       PASSED
tests/test_classifier.py::test_other_utility_bill            PASSED

========================= 10 passed in 4.55s =========================
```

---

## Design Decisions

**Why Groq instead of OpenAI?** Groq's LPU hardware delivers Llama 3.3-70B inference at sub-500ms latency with a generous free tier — fast enough for real-time inbox sorting without any cost at personal scale.

**Why no fine-tuning?** The category taxonomy is encoded directly in the system prompt with descriptions precise enough that the model classifies correctly out of the box. Adding or changing a category is a one-line edit in `src/categories.py`.

**Why `temperature=0.1`?** Classification is a deterministic task. Near-zero temperature yields consistent results across repeated calls on identical inputs.

**Why live integration tests instead of mocks?** Mocking the Groq client would test JSON parsing, not whether the model actually classifies emails correctly. All 10 tests run against the real API.

**Why `imaplib` (stdlib) instead of a third-party library?** No extra dependency needed. Standard IMAP over SSL handles everything: folder listing, creation, copy, and delete.

---

## Extending the Classifier

**Add a new category** — append a `Category` entry to `CATEGORIES` in `src/categories.py`. The prompt and folder logic pick it up automatically.

**Process more emails** — change the `limit` argument in `main.py`: `run_classifier(limit=200)`.

**Schedule it** — add a cron job or use Task Scheduler (Windows) to run `python main.py` on a recurring interval.

**Webhook / always-on** — expose `run_classifier` behind a FastAPI endpoint and wire it to Gmail Pub/Sub for instant classification on every new email.

---

## License

MIT
