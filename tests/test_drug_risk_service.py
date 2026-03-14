"""Unit tests for DrugRiskService."""

from app.models.gene_profile import GeneProfile
from app.services.drug_risk_service import evaluate


def _profiles() -> list[GeneProfile]:
    """Standard set of gene profiles for testing."""
    return [
        GeneProfile(gene="CYP2D6", allele1="*1", allele2="*1", phenotype="NM \u2013 Normal Metabolizer"),
        GeneProfile(gene="CYP2C19", allele1="*2", allele2="*2", phenotype="PM \u2013 Poor Metabolizer"),
        GeneProfile(gene="CYP2C9", allele1="*1", allele2="*2", phenotype="IM \u2013 Intermediate Metabolizer"),
        GeneProfile(gene="SLCO1B1", allele1="*1", allele2="*1", phenotype="Normal Function"),
        GeneProfile(gene="TPMT", allele1="*1", allele2="*1", phenotype="NM \u2013 Normal Metabolizer"),
        GeneProfile(gene="DPYD", allele1="*1", allele2="*1", phenotype="NM \u2013 Normal Metabolizer"),
    ]


def test_codeine_safe():
    results = evaluate(_profiles(), "CODEINE")
    assert len(results) == 1
    assert results[0].risk_assessment.risk_label == "Safe"


def test_clopidogrel_ineffective():
    """CYP2C19 PM should make clopidogrel ineffective."""
    results = evaluate(_profiles(), "CLOPIDOGREL")
    assert len(results) == 1
    assert results[0].risk_assessment.risk_label == "Ineffective"


def test_warfarin_adjust():
    """CYP2C9 IM should require warfarin dose adjustment."""
    results = evaluate(_profiles(), "WARFARIN")
    assert len(results) == 1
    assert results[0].risk_assessment.risk_label == "Adjust Dosage"


def test_simvastatin_safe():
    results = evaluate(_profiles(), "SIMVASTATIN")
    assert len(results) == 1
    assert results[0].risk_assessment.risk_label == "Safe"


def test_multiple_drugs():
    results = evaluate(_profiles(), "CODEINE,WARFARIN,CLOPIDOGREL")
    assert len(results) == 3


def test_unsupported_drug():
    results = evaluate(_profiles(), "ASPIRIN")
    assert len(results) == 1
    assert results[0].risk_assessment.risk_label == "Unknown"


def test_empty_drugs():
    results = evaluate(_profiles(), "")
    assert len(results) == 0


def test_confidence_explicit_rule():
    results = evaluate(_profiles(), "CODEINE")
    assert results[0].risk_assessment.confidence_score == 0.95


def test_severity_safe_is_none():
    results = evaluate(_profiles(), "CODEINE")
    assert results[0].risk_assessment.severity == "none"
