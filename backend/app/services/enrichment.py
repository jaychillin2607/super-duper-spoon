import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import traceback

from app.core.config import get_settings
from app.services.session import session_service
from app.core.exceptions import EnrichmentError, SessionNotFoundError, SessionError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class EnrichmentService:
    """Service for enriching business data with TIB API"""

    def __init__(self):
        """Initialize the enrichment service"""
        self.api_url = settings.ENRICHMENT_API_URL
        self.timeout = settings.ENRICHMENT_API_TIMEOUT
        self.simulate_delay = settings.ENRICHMENT_SIMULATE_DELAY
        self.failure_rate = settings.ENRICHMENT_SIMULATE_FAILURE_RATE
        logger.info(f"Enrichment service initialized with API URL: {self.api_url}")

    def _simulate_api_delay(self):
        """Simulate realistic API latency"""
        try:
            min_delay, max_delay = self.simulate_delay
            delay = random.uniform(min_delay, max_delay)
            logger.debug(f"Simulating API delay of {delay:.2f} seconds")
            time.sleep(delay)
        except Exception as e:
            logger.warning(f"Error simulating API delay: {str(e)}", exc_info=True)
            # Default delay if configuration is invalid
            time.sleep(1.0)

    def _should_simulate_failure(self) -> bool:
        """Determine if we should simulate an API failure"""
        try:
            failure = random.random() < self.failure_rate
            if failure:
                logger.debug(
                    f"Simulating API failure (failure rate: {self.failure_rate})"
                )
            return failure
        except Exception as e:
            logger.warning(f"Error in failure simulation: {str(e)}", exc_info=True)
            # Default to no failure if configuration is invalid
            return False

    def _generate_mock_enrichment_data(
        self, business_name: str, zip_code: str
    ) -> Dict[str, Any]:
        """
        Generate mock enrichment data for demonstration purposes

        Args:
            business_name: Name of the business
            zip_code: ZIP code of the business

        Returns:
            Generated enrichment data
        """
        try:
            logger.debug(
                f"Generating mock enrichment data for {business_name} in {zip_code}"
            )

            # Generate random start date (1-20 years ago)
            years_ago = random.randint(1, 20)
            start_date = datetime.now() - timedelta(days=365 * years_ago)

            # Possible SOS statuses
            statuses = ["Active", "Good Standing", "Inactive", "Revoked", "Suspended"]

            # Industry codes (random NAICS codes)
            industry_codes = ["445110", "541330", "722511", "621111", "238220"]

            # Determine verification status
            is_verified = random.random() > 0.2  # 80% chance of verification

            # Generate random data
            enrichment_data = {
                "business_name": business_name,
                "zip_code": zip_code,
                "verified": is_verified,
                "business_start_date": start_date.strftime("%Y-%m-%d"),
                "sos_status": random.choice(statuses),
                "industry_code": random.choice(industry_codes),
                "naics_code": random.choice(industry_codes),
                "business_address": {
                    "street": f"{random.randint(100, 9999)} Main St",
                    "city": "Sample City",
                    "state": "CA",
                    "zip": zip_code,
                },
                "additional_data": {
                    "employee_count_range": f"{random.randint(1, 50)}-{random.randint(51, 200)}",
                    "revenue_range": f"${random.randint(100, 999)}K-${random.randint(1, 10)}M",
                    "credit_score_range": f"{random.randint(300, 850)}",
                },
            }

            # Log verification status
            if is_verified:
                logger.info(f"Business verified: {business_name} in {zip_code}")
            else:
                logger.info(f"Business not verified: {business_name} in {zip_code}")

            return enrichment_data

        except Exception as e:
            logger.error(f"Error generating mock data: {str(e)}", exc_info=True)
            # Return minimal data if an error occurs
            return {
                "business_name": business_name,
                "zip_code": zip_code,
                "verified": False,
                "message": "Error generating enrichment data",
            }

    async def enrich_business_data(
        self, business_name: str, zip_code: str, session_id: str
    ) -> Dict[str, Any]:
        """
        Enrich business data with TIB API

        In a real implementation, this would call an external API.
        For this example, we simulate the API call with random data.

        Args:
            business_name: Business name to verify
            zip_code: ZIP code of the business
            session_id: Session ID to update with enrichment data

        Returns:
            Enrichment data

        Raises:
            EnrichmentError: If API call fails
            SessionError: If session update fails
        """
        logger.info(
            f"Enrichment request received for {business_name} in {zip_code}",
            extra={
                "business_name": business_name,
                "zip_code": zip_code,
                "session_id": session_id,
            },
        )

        if not business_name or not zip_code:
            logger.warning(
                f"Missing required fields for enrichment: business_name={bool(business_name)}, zip_code={bool(zip_code)}",
                extra={
                    "business_name": bool(business_name),
                    "zip_code": bool(zip_code),
                    "session_id": session_id,
                },
            )
            raise EnrichmentError(
                "Business name and ZIP code are required for enrichment",
                details={
                    "business_name": bool(business_name),
                    "zip_code": bool(zip_code),
                },
            )

        try:
            # Log API request
            logger.debug(
                f"Making API request to {self.api_url}",
                extra={
                    "api_url": self.api_url,
                    "timeout": self.timeout,
                    "business_name": business_name,
                    "zip_code": zip_code,
                },
            )

            # Simulate API latency
            self._simulate_api_delay()

            # Simulate occasional failures
            if self._should_simulate_failure():
                logger.warning(
                    f"Simulated API failure for {business_name} in {zip_code}",
                    extra={
                        "business_name": business_name,
                        "zip_code": zip_code,
                        "failure_type": "simulated",
                        "session_id": session_id,
                    },
                )
                raise EnrichmentError(
                    "Unable to verify business at this time. Please try again later.",
                    details={"business_name": business_name, "zip_code": zip_code},
                )

            # Generate mock data
            enrichment_data = self._generate_mock_enrichment_data(
                business_name, zip_code
            )

            # Log enrichment results
            verification_status = (
                "verified" if enrichment_data.get("verified", False) else "not verified"
            )
            logger.info(
                f"Business {verification_status}: {business_name} in {zip_code}",
                extra={
                    "business_name": business_name,
                    "zip_code": zip_code,
                    "verified": enrichment_data.get("verified", False),
                    "start_date": enrichment_data.get("business_start_date"),
                    "status": enrichment_data.get("sos_status"),
                    "session_id": session_id,
                },
            )

            # Update session with enrichment data
            try:
                logger.debug(
                    f"Updating session {session_id} with enrichment data",
                    extra={"session_id": session_id},
                )
                session = session_service.get_session(session_id)
                form_data = session.get("form_data", {})
                form_data["enrichment_data"] = enrichment_data
                session_service.update_session(session_id, form_data)
            except SessionNotFoundError:
                logger.warning(
                    f"Session {session_id} not found for enrichment update",
                    extra={"session_id": session_id},
                )
                # We still return the enrichment data even if session update fails
            except SessionError as e:
                logger.error(
                    f"Session error during enrichment: {str(e)}",
                    extra={"session_id": session_id},
                    exc_info=True,
                )
                # We still return the enrichment data even if session update fails

            return enrichment_data

        except EnrichmentError:
            # Re-raise enrichment errors
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during enrichment: {str(e)}",
                extra={
                    "business_name": business_name,
                    "zip_code": zip_code,
                    "traceback": traceback.format_exc(),
                    "session_id": session_id,
                },
                exc_info=True,
            )
            raise EnrichmentError(
                "An unexpected error occurred during business verification",
                details={"business_name": business_name, "zip_code": zip_code},
            )


# Create singleton instance
enrichment_service = EnrichmentService()
