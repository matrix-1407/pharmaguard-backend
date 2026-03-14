"""Diplotype resolver — resolves variants for one gene into exactly two alleles.

BIOLOGICAL REASONING:
Humans are diploid: every autosomal gene has exactly 2 copies.
The VCF only records positions that differ from the reference genome:
  0/0 -> both chromosomes are reference (*1/*1)
  0/1 -> one chromosome has the ALT allele (heterozygous carrier)
  1/1 -> both chromosomes have the ALT allele (homozygous variant)

Priority order:
  1. HOMOZYGOUS ALT (1/1) -> star/star
  2. SINGLE HETEROZYGOUS -> *1/star
  3. COMPOUND HETEROZYGOUS (two distinct 0/1 alleles) -> starA/starB
  4. HARD LIMIT (>2 distinct het alleles) -> first two, hard_limit_exceeded=True
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.vcf_variant import VcfVariant

REFERENCE_ALLELE = "*1"


@dataclass
class Resolution:
    """Result of diplotype resolution."""

    allele1: str
    allele2: str
    hard_limit_exceeded: bool = False


def resolve(variants: list[VcfVariant] | None) -> Resolution | None:
    """Resolve variants for a SINGLE gene into exactly two alleles.

    Args:
        variants: Pre-grouped variants for a single gene. May contain 0/0 entries.

    Returns:
        Resolution, or None if no actionable variants exist.
    """
    if not variants:
        return None

    # Priority 1: homozygous ALT takes the whole diplotype
    for v in variants:
        if v.is_homozygous_alt():
            star = _normalise(v.star_allele)
            return Resolution(allele1=star, allele2=star)

    # Priority 2 & 3: collect distinct het alleles (insertion-ordered)
    seen: dict[str, None] = {}  # ordered dict as ordered set
    for v in variants:
        if v.is_heterozygous():
            normalised = _normalise(v.star_allele)
            if normalised not in seen:
                seen[normalised] = None

    if not seen:
        return None

    alleles = list(seen.keys())

    # Single het -> one allele is the variant, the other chromosome is *1
    if len(alleles) == 1:
        return Resolution(allele1=REFERENCE_ALLELE, allele2=alleles[0])

    # Two or more -> compound heterozygous; enforce diploid max of 2
    exceeded = len(alleles) > 2
    return Resolution(allele1=alleles[0], allele2=alleles[1], hard_limit_exceeded=exceeded)


def _normalise(allele: str | None) -> str:
    """Guarantee the '*' prefix — tolerates bare numbers like '2' or '3A'."""
    if not allele or not allele.strip():
        return REFERENCE_ALLELE
    allele = allele.strip()
    return allele if allele.startswith("*") else f"*{allele}"
