"""Gene profile model — pharmacogenomic interpretation result for a single gene."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeneProfile:
    """Represents the pharmacogenomic interpretation for one gene.

    Humans are diploid: two copies of every autosomal gene.
    The diplotype (allele1/allele2) determines the metabolizer phenotype.
    """

    gene: str
    allele1: str
    allele2: str
    phenotype: str

    @property
    def diplotype(self) -> str:
        """Canonical diplotype string, e.g. '*1/*2'."""
        return f"{self.allele1}/{self.allele2}"
