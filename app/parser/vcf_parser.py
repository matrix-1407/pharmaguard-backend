"""VCF file parser — direct port of Java VcfParser."""

from __future__ import annotations

import io
from typing import BinaryIO

from app.models.vcf_variant import VcfVariant
from app.models.vcf_parse_result import VcfParseResult

# Target pharmacogenomic genes
TARGET_GENES = frozenset({"CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"})


def parse_vcf(file_content: BinaryIO) -> VcfParseResult:
    """Parse a VCF file and return structured variants, metadata, and errors.

    Only retains variants for TARGET_GENES.
    """
    variants: list[VcfVariant] = []
    metadata: dict[str, str] = {}
    errors: list[str] = []
    headers: list[str] | None = None

    reader = io.TextIOWrapper(file_content, encoding="utf-8")
    for line in reader:
        line = line.rstrip("\n").rstrip("\r")

        if line.startswith("##"):
            _parse_meta_line(line, metadata)
        elif line.startswith("#CHROM"):
            headers = line[1:].split("\t")
        elif line.strip():
            variant = _parse_data_line(line, headers, errors)
            if variant is not None and variant.gene in TARGET_GENES:
                variants.append(variant)

    return VcfParseResult(variants=variants, metadata=metadata, errors=errors)


def _parse_meta_line(line: str, metadata: dict[str, str]) -> None:
    """Parse ## metadata headers."""
    if line.startswith("##fileformat"):
        metadata["fileformat"] = line.split("=", 1)[1]
    elif line.startswith("##reference"):
        metadata["reference"] = line.split("=", 1)[1]


def _parse_data_line(
    line: str, headers: list[str] | None, errors: list[str]
) -> VcfVariant | None:
    """Parse a single VCF data line."""
    cols = line.split("\t")
    if len(cols) < 8:
        errors.append(f"Malformed line (too few columns): {line[:50]}")
        return None

    try:
        chrom = cols[0]
        pos = int(cols[1])
        variant_id = cols[2]  # rsID e.g. rs4244285
        ref = cols[3]
        alt = cols[4]
        filter_status = cols[6]
        info = cols[7]

        # Parse INFO field key=value pairs
        info_map = _parse_info(info)

        gene = info_map.get("GENE", "")
        star = info_map.get("STAR", "")
        rsid = variant_id if variant_id.startswith("rs") else info_map.get("RS", variant_id)

        # Genotype from sample column (index 9) if present
        genotype = None
        fmt = cols[8] if len(cols) > 8 else None
        sample = cols[9] if len(cols) > 9 else None
        if fmt is not None and sample is not None:
            genotype = _extract_genotype(fmt, sample)

        return VcfVariant(
            chrom=chrom,
            position=pos,
            rsid=rsid,
            ref=ref,
            alt=alt,
            filter_status=filter_status,
            gene=gene,
            star_allele=star,
            genotype=genotype,
            info_fields=info_map,
        )

    except ValueError:
        errors.append(f"Could not parse position in line: {line[:50]}")
        return None


def _parse_info(info: str) -> dict[str, str]:
    """Parse the INFO field into a dict."""
    result: dict[str, str] = {}
    if not info or info == ".":
        return result
    for token in info.split(";"):
        parts = token.split("=", 1)
        result[parts[0]] = parts[1] if len(parts) > 1 else "true"
    return result


def _extract_genotype(fmt: str, sample: str) -> str | None:
    """Extract the GT (genotype) value from FORMAT and SAMPLE columns."""
    fmt_keys = fmt.split(":")
    smp_vals = sample.split(":")
    for i, key in enumerate(fmt_keys):
        if key == "GT" and i < len(smp_vals):
            return smp_vals[i]  # e.g. "0/1" or "1|1"
    return None
