"""LLM explanation service — generates clinical summaries using Google Gemini.

The LLM is a NARRATOR only:
  - Risk, severity, diplotype, and clinical action are all pre-computed.
  - The model receives those facts and turns them into 3-4 readable sentences.
  - It cannot modify, override, or invent any clinical value.
  - On any failure, returns a static fallback.
"""

from __future__ import annotations

from app.config import settings

MODEL = "gemini-2.5-flash"

FALLBACK_SUMMARY = (
    "Explanation unavailable \u2014 pharmacogenomic profile and risk assessment "
    "are provided in the structured fields above."
)

SYSTEM_PROMPT = (
    "You are a clinical pharmacogenomics assistant. "
    "Write a single concise paragraph of 3-4 sentences that explains "
    "in plain English why this patient's genetic profile affects the named drug "
    "and what the clinical consequence of the stated risk label is. "
    "Use only the facts given to you \u2014 do NOT suggest a different risk level, "
    "severity, or treatment action. Do NOT use bullet points or disclaimers."
)


def generate_summary(
    drug: str,
    gene: str | None,
    diplotype: str | None,
    phenotype: str | None,
    risk_label: str | None,
    severity: str | None,
    action: str | None,
) -> str:
    """Generate a plain-language summary for one drug result. Never raises."""
    try:
        prompt = _build_prompt(drug, gene, diplotype, phenotype, risk_label, severity, action)
        summary = _call_gemini(prompt)
        return summary
    except Exception as e:
        print(f"[LlmExplanationService] Error: {e}")
        return FALLBACK_SUMMARY


def _build_prompt(
    drug: str,
    gene: str | None,
    diplotype: str | None,
    phenotype: str | None,
    risk_label: str | None,
    severity: str | None,
    action: str | None,
) -> str:
    """Structured fact block passed as the user message."""
    return (
        f"Drug: {drug}\n"
        f"Governing gene: {_safe(gene)}\n"
        f"Patient diplotype: {_safe(diplotype)}\n"
        f"Phenotype: {_safe(phenotype)}\n"
        f"Risk label: {_safe(risk_label)}\n"
        f"Severity: {_safe(severity)}\n"
        f"Advised clinical action: {_safe(action)}\n\n"
        "Summarise why this genetic profile affects this drug and what "
        "the clinical consequence of the risk label is."
    )


def _call_gemini(user_prompt: str) -> str:
    """Call Google Gemini via the official SDK."""
    from google import genai

    client = genai.Client(api_key=settings.gemini_api)
    response = client.models.generate_content(
        model=MODEL,
        contents=SYSTEM_PROMPT + "\n\n" + user_prompt,
    )
    text = response.text
    return text.strip() if text and text.strip() else FALLBACK_SUMMARY


def _safe(value: str | None) -> str:
    """Return value or 'Unknown' if empty."""
    return value if value and value.strip() else "Unknown"
