from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.models.schemas.enrichment import EnrichmentRequest, EnrichmentResponse
from app.services.enrichment import enrichment_service
from app.services.session import session_service
from app.core.exceptions import (
    EnrichmentError,
    SessionNotFoundError,
    ValidationError,
)

router = APIRouter(prefix="/enrichment", tags=["enrichment"])


@router.post("", response_model=EnrichmentResponse)
async def enrich_business_data(request: EnrichmentRequest) -> Dict[str, Any]:
    """
    Enrich business data with TIB verification API

    Takes business name and zip code, calls the TIB API (simulated)
    and returns enriched business data

    Args:
        request: Enrichment request with business_name, zip_code, and session_id

    Returns:
        Enriched business data

    Raises:
        HTTPException: If session not found or enrichment fails
    """
    # Verify request parameters
    if not request.business_name or not request.zip_code:
        raise ValidationError(
            "Business name and ZIP code are required",
            details={
                "business_name": bool(request.business_name),
                "zip_code": bool(request.zip_code),
            },
        )

    try:
        # Verify session exists first
        session_service.get_session(request.session_id)

        # Call enrichment service
        enrichment_data = await enrichment_service.enrich_business_data(
            request.business_name, request.zip_code, request.session_id
        )

        return enrichment_data

    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except EnrichmentError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"X-Error-Details": str(e.details)} if e.details else None,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"X-Error-Details": str(e.details)} if e.details else None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during enrichment: {str(e)}",
        )
