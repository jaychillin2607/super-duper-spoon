from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.models.domain.lead import Lead


class LeadRepository:
    """Repository for Lead database operations"""

    def __init__(self, db: Session):
        """Initialize with database session"""
        self.db = db

    def create(self, lead_data: Dict[str, Any]) -> Lead:
        """
        Create a new lead

        Args:
            lead_data: Dictionary with lead data

        Returns:
            Created Lead object
        """
        lead = Lead(**lead_data)
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get_by_id(self, lead_id: uuid.UUID) -> Optional[Lead]:
        """
        Get lead by ID

        Args:
            lead_id: Lead UUID

        Returns:
            Lead object or None if not found
        """
        return self.db.query(Lead).filter(Lead.id == lead_id).first()

    def get_by_email(self, email: str) -> Optional[Lead]:
        """
        Get lead by email

        Args:
            email: Lead email address

        Returns:
            Lead object or None if not found
        """
        return self.db.query(Lead).filter(Lead.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Lead]:
        """
        Get all leads with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Lead objects
        """
        return self.db.query(Lead).offset(skip).limit(limit).all()

    def update(self, lead_id: uuid.UUID, lead_data: Dict[str, Any]) -> Optional[Lead]:
        """
        Update lead data

        Args:
            lead_id: Lead UUID
            lead_data: New lead data

        Returns:
            Updated Lead object or None if not found
        """
        lead = self.get_by_id(lead_id)
        if not lead:
            return None

        for key, value in lead_data.items():
            if hasattr(lead, key):
                setattr(lead, key, value)

        self.db.commit()
        self.db.refresh(lead)
        return lead

    def delete(self, lead_id: uuid.UUID) -> bool:
        """
        Delete lead

        Args:
            lead_id: Lead UUID

        Returns:
            True if deleted, False if not found
        """
        lead = self.get_by_id(lead_id)
        if not lead:
            return False

        self.db.delete(lead)
        self.db.commit()
        return True
