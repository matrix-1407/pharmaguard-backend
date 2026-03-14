"""Unit tests for DiplotypeResolver."""

from app.interpretation.diplotype_resolver import resolve, REFERENCE_ALLELE
from app.models.vcf_variant import VcfVariant


def _make_variant(star: str, genotype: str) -> VcfVariant:
    return VcfVariant(gene="CYP2D6", star_allele=star, genotype=genotype)


def test_homozygous_alt_takes_both_slots():
    """1/1 should fill both allele slots with the same star allele."""
    variants = [_make_variant("*4", "1/1")]
    result = resolve(variants)
    assert result is not None
    assert result.allele1 == "*4"
    assert result.allele2 == "*4"
    assert not result.hard_limit_exceeded


def test_single_heterozygous():
    """Single 0/1 should pair with *1 reference."""
    variants = [_make_variant("*2", "0/1")]
    result = resolve(variants)
    assert result is not None
    assert result.allele1 == REFERENCE_ALLELE
    assert result.allele2 == "*2"


def test_compound_heterozygous():
    """Two distinct 0/1 alleles -> compound het."""
    variants = [
        _make_variant("*2", "0/1"),
        _make_variant("*3", "0/1"),
    ]
    result = resolve(variants)
    assert result is not None
    assert result.allele1 == "*2"
    assert result.allele2 == "*3"
    assert not result.hard_limit_exceeded


def test_more_than_two_het_alleles_sets_hard_limit():
    """>2 distinct het alleles should set hard_limit_exceeded."""
    variants = [
        _make_variant("*2", "0/1"),
        _make_variant("*3", "0/1"),
        _make_variant("*4", "0/1"),
    ]
    result = resolve(variants)
    assert result is not None
    assert result.allele1 == "*2"
    assert result.allele2 == "*3"
    assert result.hard_limit_exceeded


def test_homozygous_overrides_het():
    """1/1 should take priority over any 0/1 variants."""
    variants = [
        _make_variant("*2", "0/1"),
        _make_variant("*4", "1/1"),
    ]
    result = resolve(variants)
    assert result is not None
    assert result.allele1 == "*4"
    assert result.allele2 == "*4"


def test_empty_returns_none():
    assert resolve([]) is None
    assert resolve(None) is None


def test_normalise_bare_number():
    """Bare numbers like '2' should get '*' prefix."""
    variants = [_make_variant("2", "0/1")]
    result = resolve(variants)
    assert result is not None
    assert result.allele2 == "*2"
