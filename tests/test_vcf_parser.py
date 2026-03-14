"""Unit tests for VCF parser."""

import io
from app.parser.vcf_parser import parse_vcf


def _vcf():
    header = "#CHROM" + "\t" + "POS" + "\t" + "ID" + "\t" + "REF" + "\t" + "ALT" + "\t" + "QUAL" + "\t" + "FILTER" + "\t" + "INFO" + "\t" + "FORMAT" + "\t" + "PATIENT_001"
    line1 = "\t".join(["chr22","42128945","rs16947","C","T","99","PASS","RS=rs16947;GENE=CYP2D6;STAR=*2;FUNC=synonymous","GT:DP","0/1:64"])
    line2 = "\t".join(["chr10","94781859","rs4244285","G","A","99","PASS","RS=rs4244285;GENE=CYP2C19;STAR=*2;FUNC=splice_defect","GT:DP","1/1:62"])
    line3 = "\t".join(["chr1","97450058","rs3918290","C","T","99","PASS","RS=rs3918290;GENE=DPYD;STAR=*2A;FUNC=splice_acceptor","GT:DP","0/0:68"])
    return ("##fileformat=VCFv4.2\n##reference=GRCh38.p13\n" + header + "\n" + line1 + "\n" + line2 + "\n" + line3 + "\n").encode("utf-8")


def test_parse_vcf_extracts_target_gene_variants():
    result = parse_vcf(io.BytesIO(_vcf()))
    assert len(result.errors) == 0
    genes = {v.gene for v in result.variants}
    assert "CYP2D6" in genes
    assert "CYP2C19" in genes
    assert "DPYD" in genes


def test_parse_vcf_extracts_metadata():
    result = parse_vcf(io.BytesIO(_vcf()))
    assert result.metadata.get("fileformat") == "VCFv4.2"
    assert result.metadata.get("reference") == "GRCh38.p13"


def test_parse_vcf_extracts_genotype():
    result = parse_vcf(io.BytesIO(_vcf()))
    cyp2d6 = [v for v in result.variants if v.gene == "CYP2D6"]
    assert len(cyp2d6) == 1
    assert cyp2d6[0].genotype == "0/1"
    assert cyp2d6[0].is_heterozygous()
    cyp2c19 = [v for v in result.variants if v.gene == "CYP2C19"]
    assert len(cyp2c19) == 1
    assert cyp2c19[0].genotype == "1/1"
    assert cyp2c19[0].is_homozygous_alt()


def test_parse_vcf_extracts_star_allele():
    result = parse_vcf(io.BytesIO(_vcf()))
    cyp2d6 = [v for v in result.variants if v.gene == "CYP2D6"][0]
    assert cyp2d6.star_allele == "*2"


def test_parse_vcf_handles_malformed_line():
    header = "#CHROM" + "\t" + "POS" + "\t" + "ID" + "\t" + "REF" + "\t" + "ALT" + "\t" + "QUAL" + "\t" + "FILTER" + "\t" + "INFO"
    bad = "chr1" + "\t" + "100"
    vcf_str = "##fileformat=VCFv4.2\n" + header + "\n" + bad + "\n"
    result = parse_vcf(io.BytesIO(vcf_str.encode("utf-8")))
    assert len(result.errors) > 0
