"""Drug risk result model."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.risk_assessment import RiskAssessment


@dataclass
class DrugRiskResult:
    """One drug risk evaluation result.

    risk_label is always one of: Safe | Adjust Dosage | Toxic | Ineffective | Unknown
    """

    drug: str
    based_on_gene: str | None
    phenotype: str | None
    risk_assessment: RiskAssessment
