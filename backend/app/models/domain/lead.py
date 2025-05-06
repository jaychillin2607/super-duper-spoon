from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

from app.db.session import Base


class Lead(Base):
    """Database model for merchant leads"""

    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Step 1: Personal information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)

    # Step 2: Business information
    business_name = Column(String, nullable=False, index=True)
    tin = Column(String, nullable=False)  # Tax Identification Number (EIN or SSN)
    zip_code = Column(String, nullable=False)

    # Step 3: Business details
    monthly_revenue = Column(Float, nullable=False)
    years_in_business = Column(Float, nullable=False)

    # Enrichment data from TIB API
    enrichment_data = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Add composite unique constraint for email and business_name
    __table_args__ = (
        UniqueConstraint("email", "business_name", name="uq_lead_email_business"),
    )

    def __repr__(self):
        return f"<Lead {self.id}: {self.business_name}>"
