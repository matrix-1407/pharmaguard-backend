"""Risk assessment model and deterministic builder."""

from __future__ import annotations

from dataclasses import dataclass

# Confidence constants
CONFIDENCE_EXPLICIT_RULE = 0.95
CONFIDENCE_FALLBACK_SAFE = 0.85
CONFIDENCE_UNKNOWN_PHENO = 0.50
CONFIDENCE_UNSUPPORTED = 0.40

# Critical override pairs: drug + gene combos that cause life-threatening toxicity
CRITICAL_KEYS = frozenset({"FLUOROURACIL:DPYD", "AZATHIOPRINE:TPMT"})


@dataclass
class RiskAssessment:
    """Deterministic risk assessment for one drug evaluation.

    severity: none | low | moderate | high | critical
    confidence_score: 0.0 - 1.0
    """

    risk_label: str
    confidence_score: float
    severity: str


def build_risk_assessment(
    drug: str,
    gene: str | None,
    risk_label: str,
    phenotype: str | None,
    is_fallback: bool,
    is_unsupported: bool,
) -> RiskAssessment:
    """Build a RiskAssessment deterministically. All logic is pure."""
    confidence = _resolve_confidence(phenotype, is_fallback, is_unsupported)
    severity = _resolve_severity(drug, gene, risk_label, phenotype)
    return RiskAssessment(risk_label=risk_label, confidence_score=confidence, severity=severity)


def _resolve_confidence(
    phenotype: str | None, is_fallback: bool, is_unsupported: bool
) -> float:
    if is_unsupported:
        return CONFIDENCE_UNSUPPORTED
    if phenotype is None or phenotype.startswith("UNKNOWN"):
        return CONFIDENCE_UNKNOWN_PHENO
    if is_fallback:
        return CONFIDENCE_FALLBACK_SAFE
    return CONFIDENCE_EXPLICIT_RULE


def _resolve_severity(
    drug: str, gene: str | None, risk_label: str, phenotype: str | None
) -> str:
    # Critical override: specific drug+gene PM combos are life-threatening
    if (
        risk_label == "Toxic"
        and gene is not None
        and phenotype is not None
        and phenotype.startswith("PM")
        and f"{drug}:{gene}" in CRITICAL_KEYS
    ):
        return "critical"

    severity_map = {
        "Safe": "none",
        "Adjust Dosage": "moderate",
        "Ineffective": "moderate",
        "Toxic": "high",
    }
    return severity_map.get(risk_label, "low")
