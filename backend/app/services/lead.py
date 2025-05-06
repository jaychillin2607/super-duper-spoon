from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import traceback
import uuid

from app.models.domain.lead import Lead
from app.services.session import session_service
from app.core.exceptions import (
    DatabaseError,
    DuplicateEntryError,
    ValidationError,
    SessionNotFoundError,
    IncompleteFormError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class LeadService:
    """Service for handling lead submission"""

    def create_lead(self, db: Session, lead_data: Dict[str, Any]) -> Lead:
        """
        Create a new lead in the database

        Args:
            db: Database session
            lead_data: Lead data from form submission

        Returns:
            Created Lead object

        Raises:
            ValidationError: If required fields are missing
            DuplicateEntryError: If lead with same email and business exists
            DatabaseError: For other database errors
        """
        # Generate a log context for tracking this operation
        operation_id = str(uuid.uuid4())
        log_context = {
            "operation_id": operation_id,
            "operation": "create_lead",
            "email": lead_data.get("email"),
            "business_name": lead_data.get("business_name"),
        }

        logger.info(
            f"Creating new lead for {lead_data.get('business_name')}", extra=log_context
        )

        # Validate required fields
        required_fields = [
            # Step 1
            "first_name",
            "last_name",
            "email",
            "phone",
            # Step 2
            "business_name",
            "tin",
            "zip_code",
            # Step 3
            "monthly_revenue",
            "years_in_business",
        ]

        missing_fields = [
            field for field in required_fields if not lead_data.get(field)
        ]
        if missing_fields:
            logger.warning(
                f"Missing required fields: {missing_fields}",
                extra={**log_context, "missing_fields": missing_fields},
            )
            raise ValidationError(
                "Required fields are missing",
                details={"missing_fields": missing_fields},
            )

        try:
            # Create new lead object
            lead = Lead(
                # Step 1
                first_name=lead_data.get("first_name"),
                last_name=lead_data.get("last_name"),
                email=lead_data.get("email"),
                phone=lead_data.get("phone"),
                # Step 2
                business_name=lead_data.get("business_name"),
                tin=lead_data.get("tin"),
                zip_code=lead_data.get("zip_code"),
                # Step 3
                monthly_revenue=lead_data.get("monthly_revenue"),
                years_in_business=lead_data.get("years_in_business"),
                # Enrichment data (if available)
                enrichment_data=lead_data.get("enrichment_data"),
            )

            # Log lead data (excluding sensitive info)
            logger.debug(
                f"Lead data prepared for {lead_data.get('business_name')}",
                extra={
                    **log_context,
                    "zip_code": lead_data.get("zip_code"),
                    "monthly_revenue": lead_data.get("monthly_revenue"),
                    "years_in_business": lead_data.get("years_in_business"),
                    "has_enrichment": "enrichment_data" in lead_data
                    and bool(lead_data.get("enrichment_data")),
                },
            )

            # Add to database
            db.add(lead)
            db.commit()
            db.refresh(lead)

            logger.info(
                f"Created new lead {lead.id}: {lead.business_name}",
                extra={**log_context, "lead_id": str(lead.id)},
            )
            return lead

        except IntegrityError as e:
            db.rollback()
            error_msg = str(e)
            logger.warning(
                f"IntegrityError creating lead: {error_msg}",
                extra={**log_context, "error": error_msg},
            )

            # Check if this is a uniqueness violation
            if "uq_lead_email_business" in error_msg:
                logger.info(
                    f"Duplicate application detected: {lead_data.get('email')} + {lead_data.get('business_name')}",
                    extra=log_context,
                )
                raise DuplicateEntryError(
                    "An application for this business with this email already exists.",
                    details={
                        "email": lead_data.get("email"),
                        "business_name": lead_data.get("business_name"),
                    },
                )

            # Generic integrity error
            raise DatabaseError(f"Database integrity error: {error_msg}")

        except SQLAlchemyError as e:
            db.rollback()
            error_msg = str(e)
            logger.error(
                f"Database error creating lead: {error_msg}",
                extra={**log_context, "error": error_msg},
                exc_info=True,
            )
            raise DatabaseError(f"Database error: {error_msg}")

        except Exception as e:
            db.rollback()
            error_msg = str(e)
            logger.error(
                f"Unexpected error creating lead: {error_msg}",
                extra={
                    **log_context,
                    "error": error_msg,
                    "traceback": traceback.format_exc(),
                },
                exc_info=True,
            )
            raise DatabaseError(f"Unexpected error: {error_msg}")

    def submit_lead_from_session(self, db: Session, session_id: str) -> Lead:
        """
        Submit a lead from session data

        Args:
            db: Database session
            session_id: Session ID with form data

        Returns:
            Created Lead object

        Raises:
            SessionNotFoundError: If session not found
            IncompleteFormError: If form steps not completed
            ValidationError: If required fields are missing
            DuplicateEntryError: If lead with same email and business exists
            DatabaseError: For other database errors
        """
        logger.info(
            f"Submitting lead from session {session_id}",
            extra={"session_id": session_id},
        )

        try:
            # Get session data
            session = session_service.get_session(session_id)
            form_data = session.get("form_data", {})

            # Create log context for tracking
            log_context = {
                "session_id": session_id,
                "email": form_data.get("email"),
                "business_name": form_data.get("business_name"),
            }

            # Log session data (excluding sensitive info)
            logger.debug(
                f"Form data retrieved from session",
                extra={
                    **log_context,
                    "has_step1": "first_name" in form_data
                    and bool(form_data.get("first_name")),
                    "has_step2": "business_name" in form_data
                    and bool(form_data.get("business_name")),
                    "has_step3": "monthly_revenue" in form_data
                    and bool(form_data.get("monthly_revenue")),
                    "has_enrichment": "enrichment_data" in form_data
                    and bool(form_data.get("enrichment_data")),
                },
            )

            # Check if all steps are completed
            completed_steps = form_data.get("completed_steps", {})
            if not all(completed_steps.values()):
                incomplete_steps = [
                    step for step, completed in completed_steps.items() if not completed
                ]
                logger.warning(
                    f"Not all steps completed for session {session_id}: {incomplete_steps}",
                    extra={**log_context, "incomplete_steps": incomplete_steps},
                )
                raise IncompleteFormError(
                    "All form steps must be completed",
                    details={"incomplete_steps": incomplete_steps},
                )

            logger.info(
                f"All steps completed, creating lead from session {session_id}",
                extra=log_context,
            )

            # Create lead from form data
            lead = self.create_lead(db, form_data)

            # Delete session after successful submission
            try:
                logger.debug(
                    f"Deleting session {session_id} after successful lead creation",
                    extra={"session_id": session_id, "lead_id": str(lead.id)},
                )
                session_service.delete_session(session_id)
            except Exception as e:
                # Log but don't fail the submission if session deletion fails
                logger.warning(
                    f"Error deleting session {session_id} after lead creation: {str(e)}",
                    extra={"session_id": session_id, "error": str(e)},
                )

            logger.info(
                f"Lead successfully created and session cleared: {lead.id}",
                extra={"session_id": session_id, "lead_id": str(lead.id)},
            )
            return lead

        except SessionNotFoundError as e:
            logger.warning(
                f"Session not found: {session_id}", extra={"session_id": session_id}
            )
            # Re-raise session not found errors
            raise
        except (
            ValidationError,
            DuplicateEntryError,
            DatabaseError,
            IncompleteFormError,
        ) as e:
            # Log specific error and re-raise business logic errors
            logger.warning(
                f"Business logic error during lead submission: {str(e)}",
                extra={
                    "session_id": session_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            )
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"Unexpected error submitting lead from session: {error_msg}",
                extra={
                    "session_id": session_id,
                    "error": error_msg,
                    "traceback": traceback.format_exc(),
                },
                exc_info=True,
            )
            raise DatabaseError(f"Unexpected error submitting lead: {error_msg}")


# Create singleton instance
lead_service = LeadService()
