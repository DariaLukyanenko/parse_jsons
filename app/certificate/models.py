# Certificate model
from app.core.db import Base
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models_for_new_db_certs import TruncatedStringWithLog

class Certificate(Base):
    idCertificate = Column(Integer, nullable=False)
    idCertScheme = Column(Integer)
    idObjectCertType = Column(Integer)
    idCertType = Column(Integer, nullable=False)
    isTs = Column(Integer)
    idProductSingleLists_str = Column("idProductSingleLists", TruncatedStringWithLog(255))
    awaitForApprove = Column(Integer)
    idStatus = Column(String(255), nullable=False)
    expiredInspectionControl = Column(Integer)
    editApp = Column(Integer)
    assignRegNumber = Column(Integer)
    number = Column(TruncatedStringWithLog(255), nullable=False)
    certRegDate = Column(Date)
    certEndDate = Column(Date)
    idBlank = Column(Integer, nullable=False)
    blankNumber = Column(TruncatedStringWithLog(255))
    noSanction = Column(Integer)
    batchInspection = Column(TruncatedStringWithLog(255))
    inspectionControlPlanDate = Column(TruncatedStringWithLog(255))
    idSigner = Column(Integer)
    idEmployee = Column(Integer)
    firstName = Column(TruncatedStringWithLog(255))
    surname = Column(TruncatedStringWithLog(255))
    patronymic = Column(TruncatedStringWithLog(255))
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)
    
    annexes = relationship("Certificate_Annex", back_populates="certificate")
    applicants = relationship("Certificate_applicant", back_populates="certificate")
    manufacturers = relationship("Certificate_Manufacturer", back_populates="certificate")
    certification_authorities = relationship("Certificate_Certification_Authority", back_populates="certificate")
    tech_reglaments = relationship("Certificate_has_tech_reglaments", back_populates="certificate")

class Certificate_has_tech_reglaments(Base):
    id_certificate = Column(Integer, ForeignKey("certificate.id"), nullable=False)
    idTechnicalReglaments = Column(Integer)
    
    certificate = relationship("Certificate", back_populates="tech_reglaments")

def attach_tech_reglaments_to_certificate(certificate_obj, tech_ids):
    certificate_obj.tech_reglaments = [
        Certificate_has_tech_reglaments(tech_reglaments=int(t))
        for t in (tech_ids or [])
    ]
