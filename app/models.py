from sqlalchemy import Column, Integer, String, DateTime, Time, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StoreStatus(Base):
    __tablename__ = 'store_status'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    store_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    timestamp_utc = Column(DateTime, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('store_id', 'timestamp_utc', name='unique_store_timestamp'),
    )

class BusinessHours(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    store_id = Column(String, nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)
    start_time_local = Column(Time, nullable=False)
    end_time_local = Column(Time, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('store_id', 'day_of_week', name="unique_business_hour"),
    )

class StoreTimeZone(Base):
    __tablename__ = "store_timezone"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    store_id = Column(String, nullable=False, unique=True, index=True)
    timezone_str = Column(String, nullable=False)