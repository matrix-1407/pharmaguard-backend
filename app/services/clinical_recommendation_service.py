"""Deterministic rule-based clinical recommendation engine.

Lookup key: "DRUG:RISK_LABEL" e.g. "CODEINE:Toxic"
All guidance follows published CPIC guidelines (cpicpgx.org).
"""

from __future__ import annotations

from dataclasses import dataclass

UNKNOWN_ACTION = "Seek specialist review"
UNKNOWN_RECOMMENDATION = "Pharmacogenomic result is inconclusive. Consult clinical pharmacologist."
UNKNOWN_MONITORING = "Monitor clinically and consider repeat genotyping."


@dataclass
class ClinicalRecommendation:
    """Structured clinical recommendation."""

    action: str
    recommendation: str
    monitoring: str


# Key format: "DRUG:RISK_LABEL"
RULES: dict[str, ClinicalRecommendation] = {
    # CODEINE (CYP2D6)
    "CODEINE:Safe": ClinicalRecommendation(
        "Proceed with standard dosing",
        "Codeine can be used at standard doses. No dose adjustment required.",
        "Standard pain reassessment at follow-up.",
    ),
    "CODEINE:Adjust Dosage": ClinicalRecommendation(
        "Consider dose reduction or alternative",
        "Reduced CYP2D6 activity may lower morphine conversion. Start at 50% of standard dose or switch to a non-codeine analgesic.",
        "Monitor analgesic efficacy and sedation. Reassess within 48 hours.",
    ),
    "CODEINE:Ineffective": ClinicalRecommendation(
        "Avoid codeine \u2014 use alternative analgesic",
        "CYP2D6 Poor Metabolizer: codeine cannot be converted to active morphine. Drug will be ineffective.",
        "Switch to a non-opioid analgesic (e.g., ibuprofen, paracetamol) or a non-CYP2D6-dependent opioid (e.g., oxycodone).",
    ),
    "CODEINE:Toxic": ClinicalRecommendation(
        "Contraindicated \u2014 use alternative analgesic immediately",
        "CYP2D6 Ultrarapid Metabolizer: rapid conversion to morphine creates risk of respiratory depression and death at standard doses.",
        "Do not use codeine. Use a non-CYP2D6-dependent analgesic. Monitor for opioid toxicity signs if already administered.",
    ),
    "CODEINE:Unknown": ClinicalRecommendation(UNKNOWN_ACTION, UNKNOWN_RECOMMENDATION, UNKNOWN_MONITORING),
    # WARFARIN (CYP2C9)
    "WARFARIN:Safe": ClinicalRecommendation(
        "Proceed with standard initiation protocol",
        "CYP2C9 Normal Metabolizer. Use standard warfarin initiation dose per local protocol.",
        "Monitor INR at day 3, day 7, then weekly until stable.",
    ),
    "WARFARIN:Adjust Dosage": ClinicalRecommendation(
        "Reduce initial warfarin dose by 25\u201350%",
        "Reduced CYP2C9 activity will slow warfarin clearance. Initiate at 25\u201350% of standard dose to avoid supratherapeutic INR.",
        "Increase INR monitoring frequency: days 3, 5, 7, 10. Target INR 2.0\u20133.0.",
    ),
    "WARFARIN:Toxic": ClinicalRecommendation(
        "Significantly reduce dose or consider alternative anticoagulant",
        "CYP2C9 Poor Metabolizer: severely impaired warfarin clearance. Risk of major bleeding at standard doses. Reduce initial dose by \u226550% or switch to a DOAC.",
        "Daily INR monitoring until stable. Watch for bleeding signs. Consider haematology review.",
    ),
    "WARFARIN:Ineffective": ClinicalRecommendation(
        "Proceed with standard dosing",
        "No evidence of reduced warfarin efficacy from CYP2C9 status alone.",
        "Standard INR monitoring.",
    ),
    "WARFARIN:Unknown": ClinicalRecommendation(UNKNOWN_ACTION, UNKNOWN_RECOMMENDATION, UNKNOWN_MONITORING),
    # CLOPIDOGREL (CYP2C19)
    "CLOPIDOGREL:Safe": ClinicalRecommendation(
        "Proceed with standard clopidogrel therapy",
        "CYP2C19 Normal/Rapid Metabolizer. Standard clopidogrel dose provides adequate platelet inhibition.",
        "Routine cardiovascular monitoring per indication.",
    ),
    "CLOPIDOGREL:Adjust Dosage": ClinicalRecommendation(
        "Consider prasugrel or ticagrelor as alternative",
        "Reduced CYP2C19 activity may lead to suboptimal platelet inhibition. Consider switching to prasugrel or ticagrelor if clinically indicated.",
        "Platelet function testing recommended if clopidogrel is continued.",
    ),
    "CLOPIDOGREL:Ineffective": ClinicalRecommendation(
        "Avoid clopidogrel \u2014 use prasugrel or ticagrelor",
        "CYP2C19 Poor Metabolizer: clopidogrel cannot be adequately activated. Risk of stent thrombosis or adverse cardiovascular events.",
        "Switch to prasugrel 10 mg/day or ticagrelor 90 mg twice daily per cardiology guidance.",
    ),
    "CLOPIDOGREL:Toxic": ClinicalRecommendation(
        "Proceed with standard dosing",
        "No toxicity risk identified from CYP2C19 status for clopidogrel.",
        "Standard monitoring.",
    ),
    "CLOPIDOGREL:Unknown": ClinicalRecommendation(UNKNOWN_ACTION, UNKNOWN_RECOMMENDATION, UNKNOWN_MONITORING),
    # SIMVASTATIN (SLCO1B1)
    "SIMVASTATIN:Safe": ClinicalRecommendation(
        "Proceed with standard simvastatin dosing",
        "SLCO1B1 Normal Function. Standard simvastatin dose is appropriate.",
        "Annual CK monitoring. Report unexplained muscle pain immediately.",
    ),
    "SIMVASTATIN:Adjust Dosage": ClinicalRecommendation(
        "Reduce simvastatin dose or switch statin",
        "Decreased SLCO1B1 function increases simvastatin plasma exposure. Use \u226420 mg/day or switch to a lower-risk statin (pravastatin, rosuvastatin).",
        "CK levels at baseline and 3 months. Counsel patient on myopathy symptoms.",
    ),
    "SIMVASTATIN:Toxic": ClinicalRecommendation(
        "Avoid simvastatin \u2014 switch to pravastatin or rosuvastatin",
        "SLCO1B1 Poor Function: high risk of simvastatin-induced myopathy and rhabdomyolysis at standard doses.",
        "Switch to pravastatin 40 mg or rosuvastatin 20 mg. Baseline CK. Urgent review if muscle symptoms develop.",
    ),
    "SIMVASTATIN:Ineffective": ClinicalRecommendation(
        "Proceed with standard dosing",
        "No efficacy concern identified from SLCO1B1 status.",
        "Standard monitoring.",
    ),
    "SIMVASTATIN:Unknown": ClinicalRecommendation(UNKNOWN_ACTION, UNKNOWN_RECOMMENDATION, UNKNOWN_MONITORING),
    # AZATHIOPRINE (TPMT)
    "AZATHIOPRINE:Safe": ClinicalRecommendation(
        "Proceed with standard azathioprine dosing",
        "TPMT Normal Metabolizer. Standard dose is appropriate.",
        "CBC monthly for 3 months, then every 3 months. LFTs at baseline.",
    ),
    "AZATHIOPRINE:Adjust Dosage": ClinicalRecommendation(
        "Reduce azathioprine dose by 30\u201370%",
        "Reduced TPMT activity increases thiopurine metabolite accumulation. Reduce dose by 30\u201370% and titrate to clinical response.",
        "CBC weekly for first 4 weeks, then monthly. Monitor for leukopenia.",
    ),
    "AZATHIOPRINE:Toxic": ClinicalRecommendation(
        "Contraindicated \u2014 use alternative immunosuppressant",
        "TPMT Poor Metabolizer: azathioprine at any standard dose will cause life-threatening myelosuppression.",
        "Do not use azathioprine. Consider mycophenolate mofetil or another non-thiopurine agent. Haematology review required.",
    ),
    "AZATHIOPRINE:Ineffective": ClinicalRecommendation(
        "Proceed with standard dosing",
        "No efficacy concern from TPMT status alone.",
        "Standard CBC monitoring.",
    ),
    "AZATHIOPRINE:Unknown": ClinicalRecommendation(UNKNOWN_ACTION, UNKNOWN_RECOMMENDATION, UNKNOWN_MONITORING),
    # FLUOROURACIL (DPYD)
    "FLUOROURACIL:Safe": ClinicalRecommendation(
        "Proceed with standard 5-FU dosing",
        "DPYD Normal Metabolizer. Standard 5-FU dose and schedule are appropriate.",
        "Standard oncology monitoring: CBC, mucositis assessment, hand-foot syndrome review.",
    ),
    "FLUOROURACIL:Adjust Dosage": ClinicalRecommendation(
        "Reduce 5-FU starting dose by 25\u201350%",
        "Reduced DPYD activity will impair 5-FU clearance. Reduce starting dose by 25\u201350% and escalate only if tolerated.",
        "Close toxicity monitoring: CBC weekly, mucositis, diarrhoea, and neurotoxicity assessment each cycle.",
    ),
    "FLUOROURACIL:Toxic": ClinicalRecommendation(
        "Contraindicated at standard dose \u2014 oncology review required",
        "DPYD Poor Metabolizer: 5-FU cannot be adequately cleared. Standard doses will cause severe or fatal toxicity (mucositis, neutropenia, neurotoxicity).",
        "Do not administer standard 5-FU. Consider capecitabine dose reduction per DPYD guidelines or switch to an alternative regimen. Urgent oncology and clinical pharmacology review.",
    ),
    "FLUOROURACIL:Ineffective": ClinicalRecommendation(
        "Proceed with standard dosing",
        "No efficacy concern from DPYD status alone.",
        "Standard oncology monitoring.",
    ),
    "FLUOROURACIL:Unknown": ClinicalRecommendation(UNKNOWN_ACTION, UNKNOWN_RECOMMENDATION, UNKNOWN_MONITORING),
}

# Fallback for any combination not explicitly listed
FALLBACK = ClinicalRecommendation(UNKNOWN_ACTION, UNKNOWN_RECOMMENDATION, UNKNOWN_MONITORING)


def recommend(drug: str | None, risk_label: str | None) -> ClinicalRecommendation:
    """Returns a deterministic ClinicalRecommendation for the given drug and risk label.

    Never returns None - falls back to a safe "seek specialist review" entry.
    """
    if drug is None or risk_label is None:
        return FALLBACK
    key = f"{drug.upper()}:{risk_label}"
    return RULES.get(key, FALLBACK)
