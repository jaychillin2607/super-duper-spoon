from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session

from app.db.session import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common database operations"""

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model class and database session

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        """
        Get by id

        Args:
            id: ID value (UUID or other primary key)

        Returns:
            Model instance or None if not found
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get multiple records with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, *, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        """
        Create new record

        Args:
            obj_in: Data to create object with (dict or model instance)

        Returns:
            Created model instance
        """
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
            db_obj = self.model(**obj_in_data)
        else:
            db_obj = obj_in

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self, *, db_obj: ModelType, obj_in: Union[Dict[str, Any], ModelType]
    ) -> ModelType:
        """
        Update record

        Args:
            db_obj: Database object to update
            obj_in: New data (dict or model instance)

        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.__dict__

        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, *, id: Any) -> ModelType:
        """
        Remove record

        Args:
            id: ID of record to remove (UUID or other primary key)

        Returns:
            Removed model instance
        """
        obj = self.db.query(self.model).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj
