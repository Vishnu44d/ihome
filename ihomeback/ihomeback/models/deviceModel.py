from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime, Table, ForeignKeyConstraint, Boolean
from sqlalchemy.orm import relationship
from .meta import Base
import datetime

class Device(Base):
    __tablename__ = "device"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    port = Column(String(5), unique=True, nullable=False)
    status = Column(Boolean, nullable=False, default=False)

    alias = Column(String(50), unique=True, nullable=False)
    monitoring = Column(Boolean, nullable=False, default=False)
    measurement = Column(String(20))

    min_intensity = Column(String(5))
    max_intensity = Column(String(5))
    cur_intensity = Column(String(5))

    location = Column(String(50))
    desc = Column(String(255))
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=False)
    