from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Enum, DateTime, Numeric
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class PriorityEnum(str, enum.Enum):
    Alta = "Alta"
    Media = "Media"
    Baja = "Baja"

class StatusEnum(str, enum.Enum):
    pendiente = "pendiente"
    en_progreso = "en_progreso"
    resuelto = "resuelto"
    cerrado = "cerrado"
    re_abierto = "re_abierto"

class Incident(Base):
    __tablename__ = "incident"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    image_url = Column(Text)
    priority = Column(Enum(PriorityEnum, name="priority_enum"))
    report_date = Column(DateTime, default=datetime.utcnow)
    location_id = Column(Integer, ForeignKey("location.id"))
    location = relationship("Location", backref="incidents")

class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True)
    latitude = Column(Numeric(15, 10))
    longitude = Column(Numeric(15, 10))
    altitude = Column(Numeric(15, 10))
