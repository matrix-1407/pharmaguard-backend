"""VCF parse result model."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.vcf_variant import VcfVariant


@dataclass
class VcfParseResult:
    """Result of parsing a VCF file."""

    variants: list[VcfVariant] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return len(self.errors) == 0
