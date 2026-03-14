"""Unit tests for PhenotypeRules."""

from app.interpretation.phenotype_rules import lookup


def test_cyp2c19_normal():
    assert "NM" in lookup("CYP2C19", "*1", "*1")


def test_cyp2c19_poor():
    assert "PM" in lookup("CYP2C19", "*2", "*2")


def test_order_independent():
    """*1/*2 and *2/*1 should return the same result."""
    result_ab = lookup("CYP2C19", "*1", "*2")
    result_ba = lookup("CYP2C19", "*2", "*1")
    assert result_ab == result_ba
    assert "IM" in result_ab


def test_unknown_diplotype():
    result = lookup("CYP2C19", "*99", "*99")
    assert "UNKNOWN" in result.upper()


def test_unknown_gene():
    result = lookup("FAKE_GENE", "*1", "*1")
    assert "UNKNOWN" in result.upper()


def test_slco1b1_normal():
    assert "Normal Function" in lookup("SLCO1B1", "*1", "*1")


def test_slco1b1_poor():
    result = lookup("SLCO1B1", "*5", "*5")
    assert "Poor Function" in result


def test_all_six_genes_have_wildtype():
    """All 6 genes should have *1/*1 defined."""
    for gene in ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]:
        result = lookup(gene, "*1", "*1")
        assert "UNKNOWN" not in result.upper(), f"{gene} missing *1/*1 rule"
