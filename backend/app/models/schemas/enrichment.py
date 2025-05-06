from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class EnrichmentRequest(BaseModel):
    """Schema for enrichment API request"""

    business_name: str = Field(..., min_length=1)
    zip_code: str = Field(..., min_length=5, max_length=10)
    session_id: str = Field(..., min_length=1)


class EnrichmentResponse(BaseModel):
    """Schema for enrichment API response"""

    business_name: str
    zip_code: str
    verified: bool = False
    business_start_date: Optional[str] = None
    sos_status: Optional[str] = None
    industry_code: Optional[str] = None
    naics_code: Optional[str] = None
    business_address: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
