"""SQLAlchemy models for customer data migration."""
from sqlalchemy import Column, Date, Float, String, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CustomerRecord(Base):
    __tablename__ = "customers"
    customer_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    risk_profile = Column(String, nullable=False)
    language = Column(String, default="en")
    snapshot_json = Column(JSON, nullable=False)


class AuditChainRecord(Base):
    __tablename__ = "audit_chains"
    plan_id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False, index=True)
    chain_json = Column(JSON, nullable=False)
    confidence = Column(Float)
    decision = Column(String)
    integrity_hash = Column(String)
