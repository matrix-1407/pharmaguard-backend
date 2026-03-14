"""Drug risk service — evaluates drug risk against interpreted gene profiles.

Each drug maps to exactly one gene. Risk is derived purely from
the phenotype string of that gene's GeneProfile.

Risk label vocabulary (exhaustive):
  Safe, Adjust Dosage, Toxic, Ineffective, Unknown
"""

from __future__ import annotations

from app.models.drug_risk_result import DrugRiskResult
from app.models.gene_profile import GeneProfile
from app.models.risk_assessment import build_risk_assessment

# Supported drugs (source of truth)
SUPPORTED_DRUGS = frozenset({
    "CODEINE", "WARFARIN", "CLOPIDOGREL",
    "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL",
})

# Drug -> gene wiring
DRUG_GENE_MAP: dict[str, str] = {
    "CODEINE": "CYP2D6",
    "WARFARIN": "CYP2C9",
    "CLOPIDOGREL": "CYP2C19",
    "SIMVASTATIN": "SLCO1B1",
    "AZATHIOPRINE": "TPMT",
    "FLUOROURACIL": "DPYD",
}

# Per-drug phenotype prefix -> risk label
DRUG_RULES: dict[str, dict[str, str]] = {
    "CODEINE": {
        "PM": "Ineffective",
        "IM": "Adjust Dosage",
        "NM": "Safe",
        "RM": "Toxic",
        "UM": "Toxic",
    },
    "WARFARIN": {
        "PM": "Toxic",
        "IM": "Adjust Dosage",
        "NM": "Safe",
    },
    "CLOPIDOGREL": {
        "PM": "Ineffective",
        "IM": "Adjust Dosage",
        "NM": "Safe",
        "RM": "Safe",
    },
    "SIMVASTATIN": {
        "Poor Function": "Toxic",
        "Decreased Function": "Adjust Dosage",
        "Normal Function": "Safe",
    },
    "AZATHIOPRINE": {
        "PM": "Toxic",
        "IM": "Adjust Dosage",
        "NM": "Safe",
    },
    "FLUOROURACIL": {
        "PM": "Toxic",
        "IM": "Adjust Dosage",
        "NM": "Safe",
    },
}


def evaluate(gene_profiles: list[GeneProfile], drugs_param: str) -> list[DrugRiskResult]:
    """Evaluate only the drugs present in the comma-separated drugs_param.

    Rules:
      - null/blank input -> empty list
      - unsupported drug -> Unknown
      - supported, gene missing -> Safe (*1/*1 assumed)
      - supported, phenotype UNKNOWN -> Unknown
      - otherwise -> deterministic rule lookup
    """
    requested_drugs = _parse_drugs(drugs_param)
    if not requested_drugs:
        return []

    return [_evaluate_drug(drug, gene_profiles) for drug in requested_drugs]


def _parse_drugs(drugs_param: str | None) -> list[str]:
    """Split on commas, trim, uppercase — return only non-blank tokens."""
    if not drugs_param or not drugs_param.strip():
        return []
    return [
        d.strip().upper()
        for d in drugs_param.split(",")
        if d.strip()
    ]


def _evaluate_drug(drug: str, profiles: list[GeneProfile]) -> DrugRiskResult:
    """Evaluate a single drug against gene profiles."""

    # Unsupported drug
    if drug not in SUPPORTED_DRUGS:
        assessment = build_risk_assessment(
            drug=drug, gene=None, risk_label="Unknown",
            phenotype=None, is_fallback=False, is_unsupported=True,
        )
        return DrugRiskResult(drug=drug, based_on_gene=None, phenotype=None, risk_assessment=assessment)

    gene = DRUG_GENE_MAP[drug]

    # Find matching gene profile
    match = next((p for p in profiles if p.gene == gene), None)

    # Gene absent — *1/*1 fallback
    if match is None:
        assessment = build_risk_assessment(
            drug=drug, gene=gene, risk_label="Safe",
            phenotype="*1/*1 assumed", is_fallback=True, is_unsupported=False,
        )
        return DrugRiskResult(drug=drug, based_on_gene=gene, phenotype="*1/*1 assumed", risk_assessment=assessment)

    phenotype = match.phenotype

    # Phenotype unresolved
    if phenotype is None or phenotype.startswith("UNKNOWN"):
        assessment = build_risk_assessment(
            drug=drug, gene=gene, risk_label="Unknown",
            phenotype=phenotype, is_fallback=False, is_unsupported=False,
        )
        return DrugRiskResult(drug=drug, based_on_gene=gene, phenotype=phenotype, risk_assessment=assessment)

    # Explicit rule match
    risk_label = _resolve_risk(drug, phenotype)
    assessment = build_risk_assessment(
        drug=drug, gene=gene, risk_label=risk_label,
        phenotype=phenotype, is_fallback=False, is_unsupported=False,
    )
    return DrugRiskResult(drug=drug, based_on_gene=gene, phenotype=phenotype, risk_assessment=assessment)


def _resolve_risk(drug: str, phenotype: str) -> str:
    """Resolve risk label using startswith matching on phenotype."""
    rules = DRUG_RULES.get(drug)
    if rules is None:
        return "Unknown"
    for prefix, label in rules.items():
        if phenotype.startswith(prefix):
            return label
    return "Unknown"
