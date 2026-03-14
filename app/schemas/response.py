"""Pydantic response models — matches the JSON contract the frontend expects."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DetectedVariantResponse(BaseModel):
    """A single detected pharmacogenomic variant."""

    model_config = ConfigDict(populate_by_name=True)

    rsid: str = ""
    star_allele: str | None = Field(default=None, alias="star_allele")
    genotype: str = ""


class PharmacogenomicProfileResponse(BaseModel):
    """Pharmacogenomic profile for one drug-gene pair."""

    model_config = ConfigDict(populate_by_name=True)

    primary_gene: str | None = Field(default=None, alias="primary_gene")
    diplotype: str | None = None
    phenotype: str = "Unknown"
    detected_variants: list[DetectedVariantResponse] = Field(
        default_factory=list, alias="detected_variants"
    )


class RiskAssessmentResponse(BaseModel):
    """Risk assessment with label, confidence, and severity."""

    model_config = ConfigDict(populate_by_name=True)

    riskLabel: str = Field(default="Unknown", alias="riskLabel")
    confidenceScore: float = Field(default=0.0, alias="confidenceScore")
    severity: str = "low"


class ClinicalRecommendationResponse(BaseModel):
    """Clinical recommendation for a drug-gene interaction."""

    action: str = ""
    recommendation: str = ""
    monitoring: str = ""


class LlmExplanationResponse(BaseModel):
    """LLM-generated plain-language clinical explanation."""

    summary: str = ""


class QualityMetricsResponse(BaseModel):
    """VCF parsing quality metrics."""

    model_config = ConfigDict(populate_by_name=True)

    vcf_parsing_success: bool = Field(default=True, alias="vcf_parsing_success")


class PharmaGuardResponse(BaseModel):
    """Top-level response envelope for one drug analysis."""

    model_config = ConfigDict(populate_by_name=True)

    patient_id: str = Field(default="", alias="patient_id")
    drug: str = ""
    timestamp: str = ""
    risk_assessment: RiskAssessmentResponse = Field(
        default_factory=RiskAssessmentResponse, alias="risk_assessment"
    )
    pharmacogenomic_profile: PharmacogenomicProfileResponse = Field(
        default_factory=PharmacogenomicProfileResponse, alias="pharmacogenomic_profile"
    )
    clinical_recommendation: ClinicalRecommendationResponse = Field(
        default_factory=ClinicalRecommendationResponse, alias="clinical_recommendation"
    )
    llm_generated_explanation: LlmExplanationResponse = Field(
        default_factory=LlmExplanationResponse, alias="llm_generated_explanation"
    )
    quality_metrics: QualityMetricsResponse = Field(
        default_factory=QualityMetricsResponse, alias="quality_metrics"
    )
