"""VCF Variant model — equivalent of Java VcfVariant."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VcfVariant:
    """Represents a single variant row parsed from a VCF file."""

    chrom: str = ""
    position: int = 0
    rsid: str = ""
    ref: str = ""
    alt: str = ""
    filter_status: str = ""
    gene: str = ""
    star_allele: str = ""
    genotype: str | None = None
    info_fields: dict[str, str] = field(default_factory=dict)

    def is_homozygous_alt(self) -> bool:
        """Both chromosomes carry the ALT allele (1/1 or 1|1)."""
        return self.genotype in ("1/1", "1|1")

    def is_heterozygous(self) -> bool:
        """One chromosome carries the ALT allele (0/1, 1|0, 0|1)."""
        return self.genotype in ("0/1", "1|0", "0|1")
