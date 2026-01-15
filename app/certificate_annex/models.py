# Certificate_Annex and Certificate_AnnexBlank models
from app.core.db import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models_for_new_db_certs import TruncatedStringWithLog

class Certificate_Annex(Base):
    __tablename__ = 'certificate_annex'

    idAnnex = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idType = Column(Integer)
    ord = Column(Integer)
    pageCount = Column(Integer)
    id_certificate = Column(Integer, ForeignKey("certificate.id", ondelete="CASCADE"), nullable=False)
    certificate = relationship("Certificate", back_populates="annexes")
    blanks = relationship("Certificate_AnnexBlank", back_populates="annex")

class Certificate_AnnexBlank(Base):
    __tablename__ = 'certificate_annex_blank'

    idBlank = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    blankNumber = Column(TruncatedStringWithLog(255))
    id_annexes = Column(Integer, ForeignKey("certificate_annex.id", ondelete="CASCADE"), nullable=False)
    annex = relationship("Certificate_Annex", back_populates="blanks")
