from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set. Please create a .env file with it.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InjuryRecord(Base):
    __tablename__ = "injury_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True) # Made nullable as per typical user ID handling
    mechanism_of_injury = Column(Text, nullable=True)
    reported_symptoms = Column(Text, nullable=True) # Stored as JSON string
    severity_level = Column(String, nullable=True)
    conscious = Column(Boolean, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    obvious_bleeding = Column(Boolean, nullable=True)
    assessment_result = Column(Text, nullable=True) # Stored as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

# This line will attempt to create tables if they don't exist when this module is imported.
# For more complex migrations, Alembic is recommended (which you're installing).
# Consider managing schema changes with Alembic separately from app startup.
Base.metadata.create_all(bind=engine)
