from sqlalchemy import Column, ForeignKey, Integer
from app.core.db import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column


class Certificate_has_tech_reglaments(Base):
    """
    Attributes:
        id_certificate (Integer): Foreign key to the parent certificate.
        tech_reglaments (Integer): Technical regulations identifier.

    Relationships:
        certificate: The parent Certificate object.
    """
    id_certificate = Column(
        Integer,
        ForeignKey("certificate.id"),
        nullable=False
    )
    idTechnicalReglaments = Column(Integer)

    certificate = relationship("Certificate", back_populates="tech_reglaments")
  
    
def attach_tech_reglaments_to_certificate(certificate_obj, tech_ids):
    """
    Создаёт объекты Certificate_has_tech_regламents для каждого id из tech_ids и
    прикрепляет их к certificate_obj.tech_reglaments.
    - certificate_obj: экземпляр SQLAlchemy Certificate (новый или загруженный).
    - tech_ids: iterable[int|str] или None.
    Не выполняет session.add/commit — вызовите перед сохранением в сессии.
    """
    certificate_obj.tech_reglaments = [
        Certificate_has_tech_reglaments(tech_reglaments=int(t))
        for t in (tech_ids or [])
    ]