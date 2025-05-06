import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

import redis

from app.core.config import get_settings
from app.core.exceptions import SessionError, SessionNotFoundError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class SessionService:
    """Service for managing user sessions in Redis"""

    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.ttl = settings.SESSION_TTL
            # Test connection
            self.redis.ping()
            logger.info("Redis connection established successfully")
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}", exc_info=True)
            # Initialize with None - we'll handle this in the methods
            self.redis = None
            self.ttl = settings.SESSION_TTL

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())

    def _get_key(self, session_id: str) -> str:
        """Generate Redis key for a session"""
        return f"session:{session_id}"

    def create_session(self) -> Dict[str, Any]:
        """
        Create a new session

        Returns:
            Session data with ID and expiration

        Raises:
            SessionError: If Redis connection fails
        """
        if not self.redis:
            logger.error("Redis connection not available")
            raise SessionError("Cannot create session - storage service unavailable")

        try:
            session_id = self._generate_session_id()
            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=self.ttl)

            session_data = {
                "session_id": session_id,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "form_data": {
                    "completed_steps": {"step1": False, "step2": False, "step3": False},
                    "current_step": 1,
                },
            }

            logger.debug(f"Creating new session with ID: {session_id}")

            # Store in Redis
            self.redis.setex(
                self._get_key(session_id), self.ttl, json.dumps(session_data)
            )

            logger.info(
                f"Created new session: {session_id}", extra={"session_id": session_id}
            )
            return session_data

        except redis.RedisError as e:
            logger.error(f"Redis error creating session: {str(e)}", exc_info=True)
            raise SessionError(f"Failed to create session: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON error creating session: {str(e)}", exc_info=True)
            raise SessionError(f"Failed to serialize session data: {str(e)}")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session data by ID

        Args:
            session_id: Session identifier

        Returns:
            Session data

        Raises:
            SessionNotFoundError: If session not found
            SessionError: If Redis operation fails
        """
        if not self.redis:
            logger.error("Redis connection not available")
            raise SessionError("Cannot retrieve session - storage service unavailable")

        try:
            key = self._get_key(session_id)
            logger.debug(f"Retrieving session with ID: {session_id}")

            data = self.redis.get(key)

            if not data:
                logger.warning(
                    f"Session not found: {session_id}", extra={"session_id": session_id}
                )
                raise SessionNotFoundError(f"Session {session_id} not found or expired")

            # Extend TTL on access
            self.redis.expire(key, self.ttl)
            logger.debug(
                f"Extended TTL for session: {session_id}",
                extra={"session_id": session_id},
            )

            try:
                session_data = json.loads(data)
                logger.debug(
                    f"Successfully retrieved session: {session_id}",
                    extra={"session_id": session_id},
                )
                return session_data
            except json.JSONDecodeError as e:
                logger.error(
                    f"JSON decode error for session {session_id}: {str(e)}",
                    extra={"session_id": session_id},
                    exc_info=True,
                )
                raise SessionError(f"Failed to parse session data: {str(e)}")

        except SessionNotFoundError:
            # Re-raise not found error
            raise
        except redis.RedisError as e:
            logger.error(
                f"Redis error retrieving session {session_id}: {str(e)}",
                extra={"session_id": session_id},
                exc_info=True,
            )
            raise SessionError(f"Failed to retrieve session: {str(e)}")

    def update_session(
        self, session_id: str, form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update session data

        Args:
            session_id: Session identifier
            form_data: New form data

        Returns:
            Updated session data

        Raises:
            SessionNotFoundError: If session not found
            SessionError: If Redis operation fails
        """
        if not self.redis:
            logger.error("Redis connection not available")
            raise SessionError("Cannot update session - storage service unavailable")

        try:
            key = self._get_key(session_id)
            logger.debug(
                f"Updating session with ID: {session_id}",
                extra={"session_id": session_id},
            )

            data_str = self.redis.get(key)

            if not data_str:
                logger.warning(
                    f"Session not found for update: {session_id}",
                    extra={"session_id": session_id},
                )
                raise SessionNotFoundError(f"Session {session_id} not found or expired")

            try:
                data = json.loads(data_str)
            except json.JSONDecodeError as e:
                logger.error(
                    f"JSON decode error for session {session_id}: {str(e)}",
                    extra={"session_id": session_id},
                    exc_info=True,
                )
                raise SessionError(f"Failed to parse session data: {str(e)}")

            # Update form data
            if "form_data" not in data:
                data["form_data"] = {}

            # Log steps being marked as completed
            if "completed_steps" in form_data:
                completed = [
                    step
                    for step, value in form_data["completed_steps"].items()
                    if value
                ]
                if completed:
                    logger.info(
                        f"Steps completed in session {session_id}: {', '.join(completed)}",
                        extra={"session_id": session_id, "completed_steps": completed},
                    )

            # Log current step changes
            if "current_step" in form_data and form_data["current_step"] != data[
                "form_data"
            ].get("current_step"):
                logger.info(
                    f"Current step changed to {form_data['current_step']} in session {session_id}",
                    extra={
                        "session_id": session_id,
                        "old_step": data["form_data"].get("current_step"),
                        "new_step": form_data["current_step"],
                    },
                )

            data["form_data"].update(form_data)
            data["updated_at"] = datetime.utcnow().isoformat()

            # Store updated data
            try:
                self.redis.setex(key, self.ttl, json.dumps(data))
            except (redis.RedisError, TypeError, ValueError) as e:
                logger.error(
                    f"Error storing updated session {session_id}: {str(e)}",
                    extra={"session_id": session_id},
                    exc_info=True,
                )
                raise SessionError(f"Failed to store updated session: {str(e)}")

            logger.info(
                f"Updated session: {session_id}", extra={"session_id": session_id}
            )
            return data

        except SessionNotFoundError:
            # Re-raise not found error
            raise
        except redis.RedisError as e:
            logger.error(
                f"Redis error updating session {session_id}: {str(e)}",
                extra={"session_id": session_id},
                exc_info=True,
            )
            raise SessionError(f"Failed to update session: {str(e)}")

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session data

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found

        Raises:
            SessionError: If Redis operation fails
        """
        if not self.redis:
            logger.error("Redis connection not available")
            raise SessionError("Cannot delete session - storage service unavailable")

        try:
            key = self._get_key(session_id)
            logger.debug(
                f"Deleting session with ID: {session_id}",
                extra={"session_id": session_id},
            )

            result = self.redis.delete(key)

            if result:
                logger.info(
                    f"Deleted session: {session_id}", extra={"session_id": session_id}
                )
                return True
            else:
                logger.warning(
                    f"Session not found for deletion: {session_id}",
                    extra={"session_id": session_id},
                )
                return False

        except redis.RedisError as e:
            logger.error(
                f"Redis error deleting session {session_id}: {str(e)}",
                extra={"session_id": session_id},
                exc_info=True,
            )
            raise SessionError(f"Failed to delete session: {str(e)}")


# Create singleton instance
session_service = SessionService()
