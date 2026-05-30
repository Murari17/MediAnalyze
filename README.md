# MediAnalyze (MedIntel AI)

> **Autonomous regulatory intelligence for medical document analysis.**

MediAnalyze is a full-stack application that processes clinical narratives and adverse event reports through a pipeline of NLP services — summarization, PHI anonymization, field validation, severity classification, semantic document comparison, and decision support. It exposes a FastAPI backend and a React + Tailwind frontend.

---

## Features

### Backend Pipeline

Each service runs independently and is also composed into a single `/analyze` endpoint:

**Summarization** — uses `facebook/bart-large-cnn` to condense long clinical texts. Handles long documents by splitting into paragraph-level chunks and re-summarizing the combined result. Returns a confidence score based on input/output length ratio.

**PHI Anonymization** — uses spaCy `en_core_web_sm` to detect and replace PERSON, ORG, and GPE entities. Preserves medical abbreviations, measurement units, dosage patterns, and section headers (e.g. `BP`, `troponin`, `mg/ml`, `Medications:`). Returns the redacted text, a list of replacement mappings, and span metadata.

**Field Validation** — checks for four required fields: `patient_name`, `age`, `drug_name`, and `adverse_event`. Uses regex patterns, section header detection, a known-drug dictionary, and heuristic name patterns. Each detected field is returned with a confidence score and source location; low-confidence detections are separated from confirmed ones. Detects inconsistencies such as multiple conflicting ages.

**Severity Classification** — classifies documents into `death`, `disability`, `hospitalization`, or `other` using a zero-shot transformer (`facebook/bart-large-mnli`) by default, with an optional fine-tuned model via the `SEVERITY_MODEL` environment variable. Falls back to keyword matching if the model is unavailable. Maps categories to severity levels: `CRITICAL`, `HIGH`, or `LOW`.

**Semantic Comparison** — compares two documents using `sentence-transformers/all-MiniLM-L6-v2`. Computes a document-level cosine similarity score, then splits each document into paragraphs or sentences and identifies sections below a configurable similarity threshold. Also produces a unified diff summary.

**Decision Support** — derives a final decision from the validation and classification results:
- `INCOMPLETE SUBMISSION` — one or more required fields are missing
- `URGENT ATTENTION` — severity is CRITICAL
- `REQUIRES REVIEW` — severity is HIGH
- `SAFE` — all fields present, severity is LOW

Signals specific clinical indicators (chest pain, elevated troponin, NSTEMI, stroke, sepsis, etc.) in the decision reason.

**Text Extraction** — extracts text from uploaded PDF or TXT files using PyMuPDF (`fitz`). Falls back to Tesseract OCR at 300 DPI for scanned/image-based PDFs.

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/upload` | Upload a PDF or TXT file; returns extracted text and a preview |
| `POST` | `/summarize` | Summarize text with configurable max length |
| `POST` | `/anonymize` | Redact PHI/PII, returning anonymized text and entity mappings |
| `POST` | `/validate` | Check for required fields and return confidence-aware detections |
| `POST` | `/classify` | Classify severity category and return top matched keywords |
| `POST` | `/compare` | Semantic similarity and diff between two documents |
| `POST` | `/decision` | Generate a final decision from pre-computed summary, classification, and validation |
| `POST` | `/analyze` | Full pipeline: runs all of the above in one request |
| `GET` | `/health` | Health check |

### Frontend

A React SPA with React Router, organized into:

- **Landing** (`/`) — product overview with feature list and a three-step how-it-works section
- **Dashboard** (`/dashboard`) — summary view of analysis history and stats
- **Analyze** (`/analyze`) — main document input and results view; accepts one or two documents (Document A and optional Document B for comparison); displays summary, anonymized text with highlighted redaction tokens, detected/missing fields, classification badge, comparison diff, and decision card with severity badge
- **History** (`/history`) — log of previous analysis runs
- **Settings** (`/settings`) — application settings

Dark mode is supported via a `useDarkMode` hook.

---

## Tech Stack

### Backend

| | |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| Summarization | `facebook/bart-large-cnn` (HuggingFace Transformers) |
| Classification | `facebook/bart-large-mnli` (zero-shot) or custom model via env var |
| Semantic comparison | `sentence-transformers/all-MiniLM-L6-v2` |
| NER / Anonymization | spaCy `en_core_web_sm` |
| PDF extraction | PyMuPDF (`fitz`) + Pytesseract (OCR fallback) |
| Validation | Pydantic v2 |
| Logging | Structured JSON logging with per-request context |

### Frontend

| | |
|---|---|
| Framework | React 18 + Vite |
| Routing | React Router v6 |
| Styling | Tailwind CSS v3 |
| HTTP client | Axios |
| Icons | Lucide React |

---

## Project Structure

```
MediAnalyze/
├── requirements.txt
├── backend/
│   ├── main.py                   # FastAPI app factory, middleware, router registration
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models for all endpoints
│   ├── routes/
│   │   ├── analyze.py            # Full pipeline endpoint
│   │   ├── anonymize.py
│   │   ├── classify.py
│   │   ├── compare.py
│   │   ├── decision.py
│   │   ├── summarize.py
│   │   ├── upload.py
│   │   └── validate.py
│   ├── services/
│   │   ├── anonymization.py      # spaCy-based PHI redaction
│   │   ├── classifier.py         # Zero-shot / fine-tuned severity classifier
│   │   ├── decision.py           # Decision logic + clinical signal extraction
│   │   ├── decision_support.py   # Backward-compatible wrapper
│   │   ├── semantic_compare.py   # Sentence embedding comparison + diff
│   │   ├── summarization.py      # BART summarizer with chunking
│   │   ├── text_extraction.py    # PDF / TXT extraction with OCR fallback
│   │   └── validation.py         # Required field detection with confidence scoring
│   └── utils/
│       └── logger.py             # JSON structured logger with request context vars
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        ├── services/
        │   └── api.js            # Axios client pointing to localhost:8000
        ├── pages/
        │   ├── Landing.jsx
        │   ├── Dashboard.jsx
        │   ├── Analyze.jsx
        │   ├── History.jsx
        │   └── Settings.jsx
        ├── components/
        │   ├── Badge.jsx
        │   ├── Button.jsx
        │   ├── Card.jsx
        │   ├── Loader.jsx
        │   ├── SectionHeader.jsx
        │   ├── StatCard.jsx
        │   └── TextAreaField.jsx
        ├── layout/
        │   ├── AppShell.jsx
        │   ├── Sidebar.jsx
        │   └── Topbar.jsx
        └── hooks/
            └── useDarkMode.js
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Tesseract OCR installed on your system (for scanned PDF support)

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Download the spaCy model
python -m spacy download en_core_web_sm

# Run the API server
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Configuration

### Custom Severity Model

By default the classifier uses `facebook/bart-large-mnli` for zero-shot classification. To use a fine-tuned text classification model, set the environment variable:

```bash
export SEVERITY_MODEL=your-org/your-model-name
```

The model is loaded lazily on the first request.

### File Upload

Uploaded files are stored under `data/uploads/` (created automatically on startup) with a UUID-prefixed filename to prevent collisions. Only `.pdf` and `.txt` files are accepted.

---

## API Usage Examples

**Full pipeline (text input):**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text_a": "Patient: John Smith, Age: 58. Current Medications: Metformin 500mg, Aspirin 81mg. Chief Complaint: Chest pain with elevated troponin. Diagnosis: NSTEMI.",
    "text_b": "Optional second document for comparison"
  }'
```

**Upload a PDF:**

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@report.pdf"
```

**Anonymize only:**

```bash
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient Jane Doe was admitted to St. Mary Hospital."}'
```

---

## Logging

All services emit structured JSON logs with the following fields:

```json
{
  "timestamp": "2026-05-30T10:00:00Z",
  "level": "INFO",
  "request_id": "abc123",
  "endpoint": "/analyze",
  "message": "Analyze processing time.",
  "duration_ms": 1420.5
}
```

Request IDs are generated per-request by middleware and threaded through all service calls via Python `contextvars`.

---

## Notes

- Transformer models (`facebook/bart-large-cnn`, `facebook/bart-large-mnli`, `sentence-transformers/all-MiniLM-L6-v2`) are downloaded from HuggingFace on first use and cached locally. Initial startup may be slow.
- GPU is used automatically if available (`torch.cuda.is_available()`); the summarizer falls back to CPU otherwise.
- The frontend API client has a 180-second timeout to accommodate slow model inference on CPU.
