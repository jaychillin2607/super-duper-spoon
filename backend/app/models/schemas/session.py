from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SessionBase(BaseModel):
    """Base session schema with common fields"""

    session_id: str
    expires_at: datetime


class SessionCreate(SessionBase):
    """Schema for creating a new session"""

    pass


class SessionUpdate(BaseModel):
    """Schema for updating session data"""

    form_data: Dict[str, Any] = Field(...)


class SessionResponse(SessionBase):
    """Schema for session response"""

    form_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class FormData(BaseModel):
    """Schema for the complete form data stored in the session"""

    # Step 1 fields (optional until completed)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    # Step 2 fields (optional until completed)
    business_name: Optional[str] = None
    tin: Optional[str] = None
    zip_code: Optional[str] = None

    # Step 3 fields (optional until completed)
    monthly_revenue: Optional[float] = None
    years_in_business: Optional[float] = None

    # Track completed steps
    completed_steps: Dict[str, bool] = Field(
        default_factory=lambda: {"step1": False, "step2": False, "step3": False}
    )

    # Enrichment data (populated after business name + zip code submitted)
    enrichment_data: Optional[Dict[str, Any]] = None

    # Current step
    current_step: int = 1
