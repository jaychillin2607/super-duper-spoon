from fastapi import APIRouter, HTTPException, status, Request
from typing import Dict, Any

from app.models.schemas.session import SessionUpdate, SessionResponse
from app.services.session import session_service
from app.core.exceptions import SessionError, SessionNotFoundError
from app.core.logging import get_logger

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = get_logger(__name__)


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: Request) -> Dict[str, Any]:
    """
    Create a new session

    Returns:
        New session object with session_id and expiration

    Raises:
        HTTPException: If session creation fails
    """
    try:
        logger.info(
            "API: Creating new session",
            extra={"client_ip": request.client.host if request.client else "unknown"},
        )

        session = session_service.create_session()

        logger.info(
            f"API: Session created successfully: {session['session_id']}",
            extra={"session_id": session["session_id"]},
        )
        return session
    except SessionError as e:
        # Log client IP for troubleshooting
        client_ip = request.client.host if request.client else "unknown"
        logger.error(
            f"API: Session creation failed: {str(e)}",
            extra={"client_ip": client_ip, "error": str(e)},
        )

        # Re-raise as HTTP exception
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, request: Request) -> Dict[str, Any]:
    """
    Get session by ID

    Args:
        session_id: Session identifier

    Returns:
        Session object with form data

    Raises:
        HTTPException: If session not found or retrieval fails
    """
    logger.info(
        f"API: Retrieving session: {session_id}",
        extra={
            "session_id": session_id,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    try:
        session = session_service.get_session(session_id)

        # Log session status - which steps are completed
        completed_steps = []
        if "form_data" in session and "completed_steps" in session["form_data"]:
            completed_steps = [
                step
                for step, completed in session["form_data"]["completed_steps"].items()
                if completed
            ]

        logger.info(
            f"API: Session {session_id} retrieved successfully",
            extra={
                "session_id": session_id,
                "completed_steps": completed_steps,
                "current_step": session.get("form_data", {}).get("current_step", 1),
            },
        )

        return session
    except SessionNotFoundError as e:
        logger.warning(
            f"API: Session not found: {session_id}",
            extra={"session_id": session_id, "error": str(e)},
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SessionError as e:
        logger.error(
            f"API: Error retrieving session {session_id}: {str(e)}",
            extra={"session_id": session_id, "error": str(e)},
        )

        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str, session_update: SessionUpdate, request: Request
) -> Dict[str, Any]:
    """
    Update session data

    Args:
        session_id: Session identifier
        session_update: New form data

    Returns:
        Updated session object

    Raises:
        HTTPException: If session not found or update fails
    """
    logger.info(
        f"API: Updating session: {session_id}",
        extra={
            "session_id": session_id,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    # Log what's being updated (avoid logging sensitive data)
    update_fields = []
    if "completed_steps" in session_update.form_data:
        update_fields.append("completed_steps")
    if "current_step" in session_update.form_data:
        update_fields.append("current_step")
    if "enrichment_data" in session_update.form_data:
        update_fields.append("enrichment_data")

    form_fields = [
        field
        for field in session_update.form_data.keys()
        if field not in ["completed_steps", "current_step", "enrichment_data"]
    ]
    if form_fields:
        update_fields.append("form_fields")

    logger.debug(
        f"API: Updating fields in session {session_id}: {', '.join(update_fields)}",
        extra={"session_id": session_id, "updated_fields": update_fields},
    )

    try:
        updated_session = session_service.update_session(
            session_id, session_update.form_data
        )

        logger.info(
            f"API: Session {session_id} updated successfully",
            extra={"session_id": session_id},
        )

        return updated_session
    except SessionNotFoundError as e:
        logger.warning(
            f"API: Session not found for update: {session_id}",
            extra={"session_id": session_id, "error": str(e)},
        )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SessionError as e:
        logger.error(
            f"API: Error updating session {session_id}: {str(e)}",
            extra={"session_id": session_id, "error": str(e)},
        )

        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, request: Request) -> None:
    """
    Delete a session

    Args:
        session_id: Session identifier

    Raises:
        HTTPException: If session deletion fails
    """
    logger.info(
        f"API: Deleting session: {session_id}",
        extra={
            "session_id": session_id,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    try:
        success = session_service.delete_session(session_id)
        if not success:
            logger.warning(
                f"API: Session not found for deletion: {session_id}",
                extra={"session_id": session_id},
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        logger.info(
            f"API: Session {session_id} deleted successfully",
            extra={"session_id": session_id},
        )

    except SessionError as e:
        logger.error(
            f"API: Error deleting session {session_id}: {str(e)}",
            extra={"session_id": session_id, "error": str(e)},
        )

        raise HTTPException(status_code=e.status_code, detail=e.message)
