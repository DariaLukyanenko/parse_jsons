# Certificate_Certification_Authority, Certificate_Auth_Contact, Certificate_Auth_Address models
from app.core.db import Base
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from app.models_for_new_db_certs import TruncatedStringWithLog, AddressMixin, ContactMixin

class Certificate_Certification_Authority(Base):
    __tablename__ = "certificate_certification_authority"

    idCertificationAuthority = Column(Integer, nullable=False, primary_key=True)
    fullName = Column(TruncatedStringWithLog(255))
    accredOrgName = Column(TruncatedStringWithLog(255))
    attestatRegNumber = Column(TruncatedStringWithLog(255))
    attestatRegDate = Column(Date)
    attestatEndDate = Column(Date)
    idRal = Column(Integer, nullable=False)
    ogrn = Column(TruncatedStringWithLog(255))
    idPerson = Column(Integer)
    firstName = Column(TruncatedStringWithLog(255))
    surname = Column(TruncatedStringWithLog(255))
    patronymic = Column(TruncatedStringWithLog(255))
    prevAttestatRegNumber = Column(TruncatedStringWithLog(255))
    prevIdRal = Column(Integer)
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)
    certificate_id = Column(Integer, ForeignKey("certificate.id", ondelete="CASCADE"), nullable=False)

    certificate = relationship("Certificate", back_populates="certification_authorities")
    contacts = relationship("Certificate_Auth_Contact", back_populates="auth")
    addresses = relationship("Certificate_Auth_Address", back_populates="auth")

class Certificate_Auth_Contact(Base, ContactMixin):
    __tablename__ = "certificate_auth_contact"

    id_auth = Column(Integer, ForeignKey("certificate_certification_authority.id", ondelete="CASCADE"), nullable=False)

    auth = relationship("Certificate_Certification_Authority", back_populates="contacts")

class Certificate_Auth_Address(Base, AddressMixin):
    __tablename__ = "certificate_auth_address"

    id_auth = Column(Integer, ForeignKey("certificate_certification_authority.id", ondelete="CASCADE"), nullable=False)

    auth = relationship("Certificate_Certification_Authority", back_populates="addresses")
