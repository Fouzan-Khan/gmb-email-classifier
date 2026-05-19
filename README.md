# GMB Email Classifier <!-- v1.0.1 -->

An enterprise-grade email classification system that categorises incoming business emails in real time using Groq's inference API and Meta's Llama 3.3-70B model. Designed to slot into any business inbox pipeline — helpdesks, CRMs, or internal ticketing systems — with zero fine-tuning required.

---

## Why This Exists

Enterprise inboxes are noisy. Support tickets, vendor invoices, HR queries, and client complaints all land in the same place, creating routing delays and manual triage overhead. This classifier reads an email's subject and body, identifies its business intent, and returns a structured result — category, confidence score, and a one-sentence rationale — fast enough to act on in real time.

---

## How It Works

```
Email (subject + body)
        │
        ▼
┌───────────────────────┐
│   Prompt Builder      │  Assembles a system prompt from the
│   _build_system_      │  category taxonomy (name + description
│   prompt()            │  for each of 7 business categories)
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
│   Response Parser     │  Validates JSON, normalises category
│   & Validator         │  against CATEGORY_MAP, clamps
│                       │  confidence to [0.0, 1.0]
└───────────┬───────────┘
            │
            ▼
    ClassificationResult
    ├── category:   str    # one of 7 defined categories
    ├── confidence: float  # 0.0 – 1.0
    └── reason:     str    # one-sentence explanation
```

The classifier is stateless and single-file. There is no database, no training loop, and no vector store. It relies entirely on Llama 3.3-70B's instruction-following capability combined with a structured taxonomy prompt and enforced JSON output.

---

## Categories

| Category | Covers |
|---|---|
| **Invoice** | Vendor invoices, payment requests, billing statements, purchase orders |
| **HR Query** | Leave requests, payroll questions, benefits, onboarding, HR policy |
| **IT Support** | Hardware/software issues, password resets, VPN problems, outages |
| **Client Request** | External client questions, complaints, feature requests, feedback |
| **Internal Announcement** | Policy updates, all-hands meetings, org changes, internal notices |
| **Spam** | Unsolicited promotions, phishing attempts, scam messages |
| **Other** | Anything that does not clearly fit the above |

---

## Tech Stack

| Component | Choice | Reason |
|---|---|---|
| Language | Python 3.11 | Typed dataclasses, clean async-ready structure |
| LLM | Llama 3.3-70B (`llama-3.3-70b-versatile`) | Strong instruction following; top open-weight model for structured output |
| Inference | [Groq API](https://groq.com) | Sub-500ms latency at 70B scale; no GPU required |
| Output enforcement | `response_format: json_object` | Eliminates markdown wrapping and hallucinated schema |
| Config | `python-dotenv` | Keeps secrets out of source |
| Tests | `pytest` (integration, live API) | Validates end-to-end behaviour, not just unit logic |

---

## Project Structure

```
gmb-email-classifier/
├── src/
│   ├── classifier.py      # Core classification logic and Groq client
│   └── categories.py      # Category taxonomy (names, descriptions, lookup maps)
├── tests/
│   └── test_classifier.py # 10 integration tests across all 7 categories
├── .env                   # GROQ_API_KEY (not committed)
├── requirements.txt
└── pyproject.toml
```

---

## Installation

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com) (free tier is sufficient)

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

# Configure your API key
echo "GROQ_API_KEY=your_key_here" > .env
```

---

## Usage

```python
from src.classifier import classify_email

result = classify_email(
    subject="Invoice #INV-2024-0892 for Office Supplies — Due June 15",
    body=(
        "Dear Accounts Payable Team,\n\n"
        "Please find attached invoice #INV-2024-0892 from Acme Office Supplies "
        "for printer cartridges, paper, and desk accessories. "
        "Total amount due: $1,247.50. Payment terms: Net 30.\n\n"
        "Please remit payment to the bank details on the attached invoice.\n"
        "— Acme Office Supplies Billing Department"
    ),
)

print(result)
# [Invoice] (97% confidence) — The email is a vendor invoice requesting payment for office supplies with a specific invoice number and payment terms.

print(result.category)    # 'Invoice'
print(result.confidence)  # 0.97
print(result.reason)      # 'The email is a vendor invoice...'
```

### Example Outputs Across Categories

| Email | Category | Confidence |
|---|---|---|
| Vendor invoice #INV-2024-0892, Net 30 payment | Invoice | 97% |
| Maternity leave request, 16 weeks from September | HR Query | 99% |
| Laptop stuck on boot after Windows 11 update | IT Support | 99% |
| Client requesting bulk CSV export feature | Client Request | 98% |
| All-hands Q2 review, mandatory attendance | Internal Announcement | 99% |
| "Claim your $10,000 Amazon gift card" | Spam | 99% |
| Weekend hiking trail recommendation | Other | 95% |

---

## Tests

The test suite consists of 10 live integration tests that call the Groq API with realistic synthetic emails and assert correct category, valid confidence range, and non-empty reason.

```bash
pytest tests/ -v
```

```
tests/test_classifier.py::test_invoice_vendor_billing             PASSED
tests/test_classifier.py::test_invoice_overdue_payment_reminder   PASSED
tests/test_classifier.py::test_hr_query_maternity_leave           PASSED
tests/test_classifier.py::test_it_support_password_reset          PASSED
tests/test_classifier.py::test_it_support_laptop_boot_failure     PASSED
tests/test_classifier.py::test_client_request_feature_request     PASSED
tests/test_classifier.py::test_client_request_billing_complaint   PASSED
tests/test_classifier.py::test_internal_announcement_all_hands    PASSED
tests/test_classifier.py::test_spam_gift_card_scam                PASSED
tests/test_classifier.py::test_other_personal_message             PASSED

========================= 10 passed in 12.43s =========================
```

Each test asserts:
- Returned category matches the expected label exactly
- Confidence is a valid float within `[0.0, 1.0]`
- Reason is a non-empty string

---

## Design Decisions

**Why Groq instead of OpenAI?** Groq's LPU hardware delivers Llama 3.3-70B inference at sub-500ms latency with a generous free tier — well-suited for real-time inbox routing where OpenAI's cost at scale becomes a factor.

**Why no fine-tuning?** The category taxonomy is encoded directly in the system prompt with descriptions precise enough that Llama 3.3-70B classifies correctly without any labelled training data. This keeps the system maintainable: adding or changing a category is a one-line edit in `categories.py`.

**Why `temperature=0.1`?** Classification is a deterministic task. Near-zero temperature yields consistent results across repeated calls on identical inputs, which matters for auditability in enterprise workflows.

**Why live integration tests instead of mocks?** Mocking the Groq client would test the JSON parsing logic but not the thing that matters — whether the model actually classifies emails correctly. All 10 tests run against the real API.

---

## Extending the Classifier

**Add a new category** — append a `Category` entry to `CATEGORIES` in `src/categories.py`. The prompt rebuilds automatically.

**Batch classification** — wrap `classify_email` calls in `asyncio.gather` with an async Groq client for parallel processing.

**Webhook integration** — expose `classify_email` behind a FastAPI endpoint and wire it to your email provider's webhook (Gmail Pub/Sub, Outlook Graph API, etc.).

---

## License

MIT
