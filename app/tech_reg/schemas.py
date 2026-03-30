# -------------------------
# TechReglament (association) Schemas
# -------------------------
from pydantic import BaseModel, ConfigDict


class CertificateTechReglamentCreate(BaseModel):
    """Схема для создания записи связки сертификат -> техрегламент"""
    tech_reglaments: int


class CertificateTechReglamentRead(BaseModel):
    """Схема чтения записи связки"""
    tech_reglaments: int
    id_certificate: int

    model_config = ConfigDict(from_attributes=True)
