"""Response mapping service — pure transformation layer.

Takes raw pipeline outputs and assembles one PharmaGuardResponse per
requested drug. Maps phenotype labels to short CPIC codes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.models.drug_risk_result import DrugRiskResult
from app.models.gene_profile import GeneProfile
from app.models.vcf_variant import VcfVariant
from app.services import clinical_recommendation_service
from app.services import llm_explanation_service
from app.schemas.response import (
    ClinicalRecommendationResponse,
    DetectedVariantResponse,
    LlmExplanationResponse,
    PharmaGuardResponse,
    PharmacogenomicProfileResponse,
    QualityMetricsResponse,
    RiskAssessmentResponse,
)

# Phenotype short code mappings (order matters for startswith matching)
PHENOTYPE_SHORT_CODES: list[tuple[str, str]] = [
    ("NM", "NM"),
    ("IM", "IM"),
    ("PM", "PM"),
    ("RM", "RM"),
    ("UM", "UM"),
    ("Normal Function", "NM"),
    ("Decreased Function", "IM"),
    ("Poor Function", "PM"),
]


def map_responses(
    drug_risks: list[DrugRiskResult],
    gene_profiles: list[GeneProfile],
    all_variants: list[VcfVariant],
    parse_success: bool,
) -> list[PharmaGuardResponse]:
    """Build one PharmaGuardResponse per DrugRiskResult."""

    # Index gene profiles by gene name for O(1) lookup
    profile_by_gene: dict[str, GeneProfile] = {p.gene: p for p in gene_profiles}

    # Shared across all drugs in the same request
    patient_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    qm = QualityMetricsResponse(vcf_parsing_success=parse_success)

    return [
        _build_response(risk, profile_by_gene, all_variants, patient_id, timestamp, qm)
        for risk in drug_risks
    ]


def _build_response(
    risk: DrugRiskResult,
    profile_by_gene: dict[str, GeneProfile],
    all_variants: list[VcfVariant],
    patient_id: str,
    timestamp: str,
    qm: QualityMetricsResponse,
) -> PharmaGuardResponse:
    gene = risk.based_on_gene
    profile = profile_by_gene.get(gene) if gene else None

    pgx_profile = _build_pgx_profile(gene, profile, all_variants)

    risk_label = risk.risk_assessment.risk_label if risk.risk_assessment else "Unknown"

    recommendation = clinical_recommendation_service.recommend(risk.drug, risk_label)

    # Generate LLM explanation
    summary = llm_explanation_service.generate_summary(
        drug=risk.drug,
        gene=gene,
        diplotype=pgx_profile.diplotype,
        phenotype=pgx_profile.phenotype,
        risk_label=risk_label,
        severity=risk.risk_assessment.severity if risk.risk_assessment else None,
        action=recommendation.action if recommendation else None,
    )

    return PharmaGuardResponse(
        patient_id=patient_id,
        drug=risk.drug,
        timestamp=timestamp,
        risk_assessment=RiskAssessmentResponse(
            riskLabel=risk.risk_assessment.risk_label,
            confidenceScore=risk.risk_assessment.confidence_score,
            severity=risk.risk_assessment.severity,
        ),
        pharmacogenomic_profile=pgx_profile,
        clinical_recommendation=ClinicalRecommendationResponse(
            action=recommendation.action,
            recommendation=recommendation.recommendation,
            monitoring=recommendation.monitoring,
        ),
        llm_generated_explanation=LlmExplanationResponse(summary=summary),
        quality_metrics=qm,
    )


def _build_pgx_profile(
    gene: str | None,
    profile: GeneProfile | None,
    all_variants: list[VcfVariant],
) -> PharmacogenomicProfileResponse:
    """Build a PharmacogenomicProfile for the response."""
    if gene is None:
        return PharmacogenomicProfileResponse(
            primary_gene=None, diplotype=None, phenotype="Unknown", detected_variants=[]
        )

    diplotype = profile.diplotype if profile else None
    phenotype_raw = profile.phenotype if profile else None
    phenotype = _to_short_phenotype(phenotype_raw)

    detected_variants = [
        DetectedVariantResponse(
            rsid=v.rsid,
            star_allele=v.star_allele,
            genotype=v.genotype or "",
        )
        for v in all_variants
        if v.gene == gene and (v.is_heterozygous() or v.is_homozygous_alt())
    ]

    return PharmacogenomicProfileResponse(
        primary_gene=gene,
        diplotype=diplotype,
        phenotype=phenotype,
        detected_variants=detected_variants,
    )


def _to_short_phenotype(verbose: str | None) -> str:
    """Convert verbose phenotype label to CPIC short code."""
    if verbose is None or verbose.startswith("UNKNOWN"):
        return "Unknown"

    for prefix, code in PHENOTYPE_SHORT_CODES:
        if verbose.startswith(prefix):
            return code

    return "Unknown"
