# 🧬 PharmaGuard — AI-Assisted Pharmacogenomic Risk Assessment Platform

PharmaGuard is a full-stack clinical decision support prototype that analyzes genomic VCF files and predicts drug-specific pharmacogenomic risks using deterministic clinical rules enhanced with AI-generated explanations.

It transforms raw genetic variant data into structured, explainable medication risk assessments for six clinically relevant drugs.

---

## 🚀 Live Demo

**Application (On Vercel):**
https://pharmaguard-ui.vercel.app
(note : A demo VCF file is provided in the repository for testing the application)

---

## 🏗️ System Architecture

### Full Pipeline Flow

```text
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                     │
│         React 18 + Vite SPA  —  Vercel CDN              │
└─────────────────────────┬───────────────────────────────┘
                          │  POST /api/vcf/analyse
                          │  (multipart: VCF file + drug list)
                          ▼
┌─────────────────────────────────────────────────────────┐
│             BACKEND  —  Python (FastAPI)                │
│                      Render (Docker)                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  1.  VCF Upload                                 │    │
│  │      Accepts .vcf file via multipart/form-data  │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  2.  VCF Parser                                 │    │
│  │      Extracts variants, genes & star alleles    │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  3.  Variant Filtering                          │    │
│  │      Retains only actionable genotypes          │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  4.  Diplotype Resolution                       │    │
│  │      Enforces diploid constraints per gene      │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  5.  Phenotype Mapping                          │    │
│  │      CPIC-aligned rules:                        │    │
│  │      Diplotype → PM / IM / NM / RM / URM        │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  6.  Drug Risk Engine                           │    │
│  │      Deterministic logic per drug–phenotype     │    │
│  │      pair  →  SAFE / ADJUST DOSE / TOXIC        │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  7.  Clinical Recommendation Engine             │    │
│  │      Structured medical guidance per drug       │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  8.  Confidence & Severity Scoring              │    │
│  │      Risk level + confidence percentage         │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  9.  LLM Explanation  (Google Gemini)           │    │
│  │      Plain-language clinical summary only       │    │
│  │      ⚠️  No risk decisions made by LLM          │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  10. Structured JSON Response                   │    │
│  │      Schema-compliant output per drug           │    │
│  └──────────────────────┬──────────────────────────┘    │
└─────────────────────────┼───────────────────────────────┘
                          │  JSON Array
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                     │
│   Confidence ring · Gene accordion · Variant table      │
│   LLM panel · JSON viewer · Download                    │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Module | Responsibility |
|---|---|---|
| **Ingestion** | VCF Parser | Parse raw VCF → extract variants, genes, star alleles |
| **Filtering** | Variant Filter | Discard non-actionable genotypes |
| **Genetics** | Diplotype Resolver | Enforce diploid constraints per pharmacogene |
| **Phenotyping** | Phenotype Rules | Map diplotypes to metaboliser status (CPIC) |
| **Risk** | Drug Risk Service | Classify drug risk deterministically |
| **Guidance** | Clinical Recommendation Service | Generate structured medical recommendations |
| **Scoring** | Risk Assessment Factory | Compute confidence score & severity level |
| **Explanation** | LLM Explanation Service | Generate Gemini-powered plain-language summary |
| **Output** | Response Mapper | Serialize schema-compliant JSON array |

### Design Principles

-  **Deterministic clinical logic** — AI never makes risk decisions
-  **Explainable variant traceability** — every risk traces back to a specific variant
-  **Strict schema-compliant JSON output** — consistent, parseable response
-  **Separation of logic and explanation layers** — LLM is summary-only
-  **Environment-driven configuration** — no hardcoded secrets
-  **Production-ready Docker deployment** — Render-hosted containerized backend

---

## ⚙️ Backend — Clinical Decision Engine

This repository contains the **Python (FastAPI)** backend.

### Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core runtime |
| FastAPI | REST API framework |
| Uvicorn | ASGI web server |
| Pydantic | Data validation & serialization |
| Docker | Containerization |
| Google Gen AI SDK | Gemini LLM integration |
| Render | Cloud deployment |

### Core Modules

| Module | Description |
|---|---|
| `vcf_parser.py` | Extracts variants, genes, and star alleles from uploaded VCF files |
| `diplotype_resolver.py` | Enforces diploid constraints and resolves star allele pairs |
| `phenotype_rules.py` | Maps diplotypes → PM / IM / NM / RM / URM using CPIC-aligned rules |
| `drug_risk_service.py` | Deterministic drug risk classification per phenotype |
| `clinical_recommendation_service.py` | Structured medical guidance per drug–phenotype combination |
| `risk_assessment.py` | Computes confidence percentage and severity score |
| `llm_explanation_service.py` | Calls Google Gemini to produce plain-language clinical summaries |

---

## 🖥️ Frontend — PharmaGuard SPA

### Tech Stack

| Technology | Purpose |
|---|---|
| React 18 | UI framework |
| Vite | Build tooling & dev server |
| React Router v6 | Client-side routing |
| Axios | HTTP client |
| Lucide React | Icon library |
| OGL | Aurora WebGL hero effect |
| Vanilla CSS | Custom design system |
| Vercel | CDN deployment |

### Pages

| Page | Description |
|---|---|
| Landing | Aurora hero, feature highlights, supported drugs, CTA |
| Analysis | VCF upload + drug selection → risk assessment results |
| Documentation | API reference & usage guide |

### Key Features

-  Dark / Light theme toggle
-  Drag-and-drop VCF upload
-  6 drug selection chips
-  Animated confidence ring
-  Gene accordion & variant table
-  LLM explanation panel
-  JSON viewer + download

---

## 📥 Installation

### Backend Setup

**1. Clone repository**
```bash
git clone https://github.com/matrix-1407/pharmaguard-backend.git
cd pharmaguard-backend
```

**2. Configure environment variables**

Create `.env`:
```properties
PORT=8080
GEMINI_API=your-gemini-api-key
FRONTEND_URL=http://localhost:5173
```

**3. Run**
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --port 8080 --reload
```

---

### 🐳 Docker Deployment (Render)

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Deploy via **Render → Web Service → Docker** environment.

---

### Frontend Setup

```bash
cd pharmaguard-frontend
npm install
```

Create `.env`:
```env
VITE_API_BASE_URL=http://localhost:8080
VITE_USE_MOCK=false
```

Run:
```bash
npm run dev
```

Deploy via **Vercel**.

---

## 📡 API Documentation

### Endpoint

```
POST /api/vcf/analyse
```

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | File | VCF file (v4.x) |
| `drugs` | String | Comma-separated drug list |

**Example:**
```
drugs=WARFARIN,CLOPIDOGREL
```

**Response** — JSON array of per-drug pharmacogenomic records:

```json
[
  {
    "risk_assessment": { ... },
    "pharmacogenomic_profile": { ... },
    "clinical_recommendation": { ... },
    "llm_generated_explanation": { "summary": "..." },
    "quality_metrics": { ... }
  }
]
```

---

## 💊 Supported Drugs

| Drug | Gene(s) | Risk Category |
|---|---|---|
| Codeine | CYP2D6 | Opioid toxicity / inefficacy |
| Warfarin | CYP2C9, VKORC1, CYP4F2 | Bleeding / thrombosis |
| Clopidogrel | CYP2C19 | Antiplatelet resistance |
| Simvastatin | SLCO1B1 | Myopathy / rhabdomyolysis |
| Azathioprine | TPMT, NUDT15 | Myelosuppression |
| Fluorouracil | DPYD | Severe toxicity |

---

### Front-end repo: https://github.com/matrix-1407/pharmaguard-ui
---

## 🏆 Hackathon Highlights

- ✅ Deterministic pharmacogenomic engine
- ✅ Explainable AI (LLM for clinical summary only)
- ✅ Full-stack deployment (Vercel + Render)
- ✅ Dockerized backend
- ✅ Strict JSON schema compliance
- ✅ Production-style architecture
- ✅ CPIC-aligned phenotype rules
- ✅ 6-drug coverage across major pharmacogenes
