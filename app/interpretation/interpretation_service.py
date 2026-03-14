"""Interpretation service — orchestrates the full interpretation pipeline.

Pipeline:
  VcfVariant list
    -> [1] Filter: drop 0/0, keep only het or hom-alt
    -> [2] Group: bucket remaining variants by gene name
    -> [3] Resolve: DiplotypeResolver converts to exactly two alleles
    -> [4] Lookup: PhenotypeRules maps diplotype to clinical phenotype
    -> [5] Backfill: required panel genes with no variants -> *1/*1
  => List[GeneProfile]
"""

from __future__ import annotations

import sys
from collections import defaultdict

from app.models.vcf_variant import VcfVariant
from app.models.gene_profile import GeneProfile
from app.interpretation import diplotype_resolver
from app.interpretation.diplotype_resolver import REFERENCE_ALLELE
from app.interpretation import phenotype_rules

# Required pharmacogenomic panel
REQUIRED_PANEL = frozenset({"CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"})


def interpret(variants: list[VcfVariant] | None) -> list[GeneProfile]:
    """Full interpretation pipeline.

    Returns one GeneProfile per panel gene, sorted alphabetically.
    """
    if variants is None:
        variants = []

    # Step 1: filter — keep only heterozygous or homozygous-alt
    actionable = [
        v
        for v in variants
        if (v.is_heterozygous() or v.is_homozygous_alt())
        and v.gene
        and v.gene.strip()
    ]

    # Step 2: group by gene
    by_gene: dict[str, list[VcfVariant]] = defaultdict(list)
    for v in actionable:
        by_gene[v.gene].append(v)

    # Steps 3 + 4: resolve + lookup for genes that have variants
    resolved: dict[str, GeneProfile] = {}
    for gene, gene_variants in by_gene.items():
        profile = _build_profile(gene, gene_variants)
        if profile is not None:
            resolved[gene] = profile

    # Step 5: backfill required panel genes with no variants
    for gene in REQUIRED_PANEL:
        if gene not in resolved:
            phenotype = phenotype_rules.lookup(gene, REFERENCE_ALLELE, REFERENCE_ALLELE)
            resolved[gene] = GeneProfile(
                gene=gene,
                allele1=REFERENCE_ALLELE,
                allele2=REFERENCE_ALLELE,
                phenotype=phenotype,
            )

    # Sort alphabetically for deterministic output
    return sorted(resolved.values(), key=lambda p: p.gene)


def _build_profile(gene: str, variants: list[VcfVariant]) -> GeneProfile | None:
    """Build a GeneProfile from resolved diplotype and phenotype lookup."""
    resolution = diplotype_resolver.resolve(variants)
    if resolution is None:
        return None

    if resolution.hard_limit_exceeded:
        print(
            f"[InterpretationService] WARNING: >2 het variants for {gene} — "
            "only first two alleles used. Check VCF annotation quality.",
            file=sys.stderr,
        )

    phenotype = phenotype_rules.lookup(gene, resolution.allele1, resolution.allele2)
    return GeneProfile(
        gene=gene,
        allele1=resolution.allele1,
        allele2=resolution.allele2,
        phenotype=phenotype,
    )
