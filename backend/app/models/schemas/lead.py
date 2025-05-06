from pydantic import BaseModel, EmailStr, Field, validator, UUID4
from typing import Optional, Dict, Any
from datetime import datetime


class FormStep1(BaseModel):
    """Schema for step 1 of the form: personal information"""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)


class FormStep2(BaseModel):
    """Schema for step 2 of the form: business information"""

    business_name: str = Field(..., min_length=1, max_length=200)
    tin: str = Field(..., min_length=9, max_length=11)
    zip_code: str = Field(..., min_length=5, max_length=10)

    @validator("tin")
    def validate_tin(cls, v):
        # Strip any hyphens or spaces
        v = v.replace("-", "").replace(" ", "")

        # Check if it's a valid format (basic validation)
        if not v.isdigit():
            raise ValueError("TIN must contain only digits")

        if len(v) not in [9, 10]:
            raise ValueError("TIN must be 9 digits for SSN or 9-10 digits for EIN")

        return v


class FormStep3(BaseModel):
    """Schema for step 3 of the form: business details"""

    monthly_revenue: float = Field(..., gt=0)
    years_in_business: float = Field(..., ge=0)


class EnrichmentData(BaseModel):
    """Schema for business data enrichment results"""

    business_start_date: Optional[str] = None
    sos_status: Optional[str] = None
    industry_code: Optional[str] = None
    verified: bool = False
    additional_info: Optional[Dict[str, Any]] = None


class LeadCreate(BaseModel):
    """Schema for creating a complete lead"""

    # Step 1
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

    # Step 2
    business_name: str
    tin: str
    zip_code: str

    # Step 3
    monthly_revenue: float
    years_in_business: float

    # Optional enrichment data
    enrichment_data: Optional[Dict[str, Any]] = None


class LeadResponse(LeadCreate):
    """Schema for lead response including database fields"""

    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
