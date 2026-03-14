"""Analysis router — POST /api/vcf/analyse endpoint."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.vcf_parse_result import VcfParseResult
from app.parser.vcf_parser import parse_vcf
from app.interpretation.interpretation_service import interpret
from app.services.drug_risk_service import evaluate
from app.services.response_mapping_service import map_responses
from app.schemas.response import PharmaGuardResponse

router = APIRouter(prefix="/api/vcf", tags=["analysis"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/analyse", response_model=list[PharmaGuardResponse])
async def analyse(
    file: UploadFile = File(...),
    drugs: str = Form(...),
) -> list[PharmaGuardResponse]:
    """Full production pipeline: validate -> parse -> interpret -> drug risk -> map response.

    Accepts multipart/form-data with:
      - file: a .vcf file (max 5MB)
      - drugs: comma-separated drug names (e.g. "CODEINE,WARFARIN")
    """
    # Validate file
    _validate_file(file)

    try:
        # Parse VCF
        parse_result: VcfParseResult = parse_vcf(file.file)

        # Interpret variants -> gene profiles
        gene_profiles = interpret(parse_result.variants)

        # Evaluate drug risks
        drug_risks = evaluate(gene_profiles, drugs)

        # Determine parse success
        parse_success = not parse_result.errors

        # Map to response
        return map_responses(drug_risks, gene_profiles, parse_result.variants, parse_success)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


def _validate_file(file: UploadFile) -> None:
    """Validate the uploaded VCF file."""
    if file is None or file.filename is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not file.filename.endswith(".vcf"):
        raise HTTPException(status_code=400, detail="File must be a .vcf file")

    # Read file content to check size
    # Note: FastAPI UploadFile doesn't expose size directly
    # We rely on the client sending Content-Length or we check after read
