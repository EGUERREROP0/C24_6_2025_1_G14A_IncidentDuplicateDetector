from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Incident, Location
from similitud import verificar_incidente_nuevo

Base.metadata.create_all(bind=engine)
app = FastAPI()

class IncidentInput(BaseModel):
    description: str
    image_url: str
    latitude: float
    longitude: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/verificar")
def verificar_incidente(incidente: IncidentInput, db: Session = Depends(get_db)):
    # Buscar incidentes anteriores (últimos 50)
    incidentes = db.query(Incident).join(Location).order_by(Incident.report_date.desc()).limit(50).all()

    anteriores = []
    for inc in incidentes:
        anteriores.append({
            "description": inc.description,
            "image_url": inc.image_url,
            "latitude": inc.location.latitude,
            "longitude": inc.location.longitude,
            "report_date": inc.report_date
        })

    nuevo = incidente.dict()
    duplicado, sugerido, score = verificar_incidente_nuevo(nuevo, anteriores)

    return {
        "duplicado": duplicado,
        "incidente_sugerido": sugerido,
        "score": score
    }
