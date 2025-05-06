from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.schemas.lead import LeadCreate, LeadResponse
from app.services.lead import lead_service
from app.db.session import get_db
from app.core.exceptions import (
    ValidationError,
    DuplicateEntryError,
    DatabaseError,
    SessionNotFoundError,
    IncompleteFormError,
)

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead: LeadCreate, request: Request, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new lead directly

    Args:
        lead: Lead data
        db: Database session

    Returns:
        Created lead

    Raises:
        HTTPException: If lead creation fails
    """
    try:
        lead_obj = lead_service.create_lead(db, lead.dict())
        return lead_obj

    except ValidationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"X-Error-Details": str(e.details)} if e.details else None,
        )
    except DuplicateEntryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DatabaseError as e:
        # Log the client IP for troubleshooting database errors
        client_ip = request.client.host if request.client else "unknown"
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/submit/{session_id}",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_lead_from_session(
    session_id: str, request: Request, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Submit a lead from session data

    Args:
        session_id: Session ID with form data
        db: Database session

    Returns:
        Created lead

    Raises:
        HTTPException: If session not found, form incomplete, or database error
    """
    try:
        lead_obj = lead_service.submit_lead_from_session(db, session_id)
        return lead_obj

    except SessionNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except IncompleteFormError as e:
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
    except DuplicateEntryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DatabaseError as e:
        # Log the client IP for troubleshooting database errors
        client_ip = request.client.host if request.client else "unknown"
        raise HTTPException(status_code=e.status_code, detail=e.message)
