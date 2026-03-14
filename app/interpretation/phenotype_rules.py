"""In-memory phenotype rule tables for all supported pharmacogenes.

Each gene encodes a drug-metabolising enzyme. Star alleles (*1, *2, *17...)
are named haplotypes. The DIPLOTYPE (both alleles together) determines
total enzyme activity. These rules follow CPIC guidelines (cpicpgx.org).

Lookup key: "ALLELE_A/ALLELE_B" - always sorted so *1/*2 == *2/*1.
"""

from __future__ import annotations

# gene -> {diplotype-key -> phenotype label}
RULES: dict[str, dict[str, str]] = {
    # CYP2C19 - metabolises clopidogrel, PPIs, SSRIs, voriconazole
    "CYP2C19": {
        "*1/*1": "NM \u2013 Normal Metabolizer",
        "*1/*2": "IM \u2013 Intermediate Metabolizer",
        "*1/*3": "IM \u2013 Intermediate Metabolizer",
        "*2/*2": "PM \u2013 Poor Metabolizer",
        "*2/*3": "PM \u2013 Poor Metabolizer",
        "*3/*3": "PM \u2013 Poor Metabolizer",
        "*1/*17": "RM \u2013 Rapid Metabolizer",
        "*2/*17": "IM \u2013 Intermediate Metabolizer",
        "*17/*17": "UM \u2013 Ultrarapid Metabolizer",
    },
    # CYP2D6 - metabolises codeine, tamoxifen, many antidepressants
    "CYP2D6": {
        "*1/*1": "NM \u2013 Normal Metabolizer",
        "*1/*2": "NM \u2013 Normal Metabolizer",
        "*2/*2": "NM \u2013 Normal Metabolizer",
        "*1/*4": "IM \u2013 Intermediate Metabolizer",
        "*1/*5": "IM \u2013 Intermediate Metabolizer",
        "*1/*6": "IM \u2013 Intermediate Metabolizer",
        "*4/*4": "PM \u2013 Poor Metabolizer",
        "*4/*5": "PM \u2013 Poor Metabolizer",
        "*5/*5": "PM \u2013 Poor Metabolizer",
        "*3/*4": "PM \u2013 Poor Metabolizer",
        "*4/*6": "PM \u2013 Poor Metabolizer",
        "*1/*1xN": "UM \u2013 Ultrarapid Metabolizer",
        "*1/*2xN": "UM \u2013 Ultrarapid Metabolizer",
    },
    # CYP2C9 - metabolises warfarin, NSAIDs, phenytoin
    "CYP2C9": {
        "*1/*1": "NM \u2013 Normal Metabolizer",
        "*1/*2": "IM \u2013 Intermediate Metabolizer",
        "*1/*3": "IM \u2013 Intermediate Metabolizer",
        "*2/*2": "IM \u2013 Intermediate Metabolizer",
        "*2/*3": "PM \u2013 Poor Metabolizer",
        "*3/*3": "PM \u2013 Poor Metabolizer",
    },
    # SLCO1B1 - hepatic uptake transporter; affects statin myopathy risk
    "SLCO1B1": {
        "*1/*1": "Normal Function",
        "*1/*5": "Decreased Function \u2013 Increased Statin Myopathy Risk",
        "*1/*15": "Decreased Function \u2013 Increased Statin Myopathy Risk",
        "*5/*5": "Poor Function \u2013 High Statin Myopathy Risk",
        "*5/*15": "Poor Function \u2013 High Statin Myopathy Risk",
        "*15/*15": "Poor Function \u2013 High Statin Myopathy Risk",
    },
    # TPMT - thiopurine methyltransferase
    "TPMT": {
        "*1/*1": "NM \u2013 Normal Metabolizer",
        "*1/*2": "IM \u2013 Intermediate Metabolizer",
        "*1/*3A": "IM \u2013 Intermediate Metabolizer",
        "*1/*3B": "IM \u2013 Intermediate Metabolizer",
        "*1/*3C": "IM \u2013 Intermediate Metabolizer",
        "*2/*3A": "PM \u2013 Poor Metabolizer",
        "*3A/*3A": "PM \u2013 Poor Metabolizer",
        "*3A/*3C": "PM \u2013 Poor Metabolizer",
        "*3C/*3C": "PM \u2013 Poor Metabolizer",
    },
    # DPYD - dihydropyrimidine dehydrogenase
    "DPYD": {
        "*1/*1": "NM \u2013 Normal Metabolizer",
        "*1/*2A": "IM \u2013 Intermediate Metabolizer",
        "*1/*13": "IM \u2013 Intermediate Metabolizer",
        "*2A/*2A": "PM \u2013 Poor Metabolizer",
        "*2A/*13": "PM \u2013 Poor Metabolizer",
        "*13/*13": "PM \u2013 Poor Metabolizer",
    },
}


def lookup(gene: str, allele1: str, allele2: str) -> str:
    """Look up a phenotype for a given gene + two alleles.

    The lookup is order-independent: *1/*2 and *2/*1 return the same result.
    """
    gene_rules = RULES.get(gene)
    if gene_rules is None:
        return f"UNKNOWN \u2013 gene '{gene}' not in rule set"

    key_ab = f"{allele1}/{allele2}"
    key_ba = f"{allele2}/{allele1}"

    if key_ab in gene_rules:
        return gene_rules[key_ab]
    if key_ba in gene_rules:
        return gene_rules[key_ba]

    return "UNKNOWN"
