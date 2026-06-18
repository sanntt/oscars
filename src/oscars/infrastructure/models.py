from sqlalchemy import Column, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True)
    dealer = Column(String, nullable=False)
    daily_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False)
