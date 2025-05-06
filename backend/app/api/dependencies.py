from fastapi import Depends, HTTPException, status

from app.db.session import get_db
from app.db.repositories.leads import LeadRepository
from app.services.session import session_service
from sqlalchemy.orm import Session


def get_lead_repository(db: Session = Depends(get_db)) -> LeadRepository:
    """
    Dependency for getting LeadRepository

    Args:
        db: Database session from get_db dependency

    Returns:
        LeadRepository instance
    """
    return LeadRepository(db)


def get_session_or_404(session_id: str) -> dict:
    """
    Dependency for getting session data with 404 if not found

    Args:
        session_id: Session ID

    Returns:
        Session data

    Raises:
        HTTPException: 404 if session not found
    """
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return session


def validate_form_step(step: int, session_id: str) -> dict:
    """
    Validate that previous steps are completed

    Args:
        step: Current step number (1-3)
        session_id: Session ID

    Returns:
        Session data

    Raises:
        HTTPException: 400 if previous steps not completed
    """
    session = get_session_or_404(session_id)
    form_data = session.get("form_data", {})
    completed_steps = form_data.get("completed_steps", {})

    # For step 2, check if step 1 is completed
    if step == 2 and not completed_steps.get("step1"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step 1 must be completed first",
        )

    # For step 3, check if steps 1 and 2 are completed
    if step == 3 and (
        not completed_steps.get("step1") or not completed_steps.get("step2")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Steps 1 and 2 must be completed first",
        )

    return session
