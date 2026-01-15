# Certificate_applicant, Certificate_Applicant_Address, Certificate_Applicant_Contact models
from app.core.db import Base
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from app.models_for_new_db_certs import TruncatedStringWithLog, AddressMixin, ContactMixin

class Certificate_applicant(Base):
    __tablename__ = 'certificate_applicant'

    idLegalSubject = Column(Integer, nullable=False)
    idEgrul = Column(Integer)
    idApplicantType = Column(Integer)
    idLegalSubjectType = Column(Integer)
    fullName = Column(TruncatedStringWithLog(255))
    shortName = Column(TruncatedStringWithLog(255))
    idPerson = Column(Integer)
    surname = Column(TruncatedStringWithLog(255))
    firstName = Column(TruncatedStringWithLog(255))
    patronymic = Column(TruncatedStringWithLog(255))
    headPosition = Column(TruncatedStringWithLog(255))
    ogrn = Column(TruncatedStringWithLog(255))
    ogrnAssignDate = Column(Date)
    inn = Column(TruncatedStringWithLog(255))
    kpp = Column(TruncatedStringWithLog(255))
    idLegalForm = Column(Integer)
    regDate = Column(Date)
    regOrganName = Column(TruncatedStringWithLog(255))
    addlRegInfo = Column(TruncatedStringWithLog(255))
    isEecRegister = Column(Integer)
    transnational = Column(TruncatedStringWithLog(255))
    passportIssueDate = Column(Date)
    passportIssuedBy = Column(TruncatedStringWithLog(255))
    passportNum = Column(TruncatedStringWithLog(255))
    idPersonDoc = Column(Integer)
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)
    id_certificate = Column(Integer, ForeignKey("certificate.id", ondelete="CASCADE"), nullable=False)
    certificate = relationship("Certificate", back_populates="applicants")
    addresses = relationship("Certificate_Applicant_Address", back_populates="applicant", cascade="all, delete")
    contacts = relationship("Certificate_Applicant_Contact", back_populates="applicant", cascade="all, delete")

class Certificate_Applicant_Address(Base, AddressMixin):
    __tablename__ = 'certificate_applicant_address'

    id_applicant = Column(Integer, ForeignKey("certificate_applicant.id", ondelete="CASCADE"), nullable=False)
    applicant = relationship("Certificate_applicant", back_populates="addresses")

class Certificate_Applicant_Contact(Base, ContactMixin):
    __tablename__ = 'certificate_applicant_contact'

    id_applicant = Column(Integer, ForeignKey("certificate_applicant.id", ondelete="CASCADE"), nullable=False)
    applicant = relationship("Certificate_applicant", back_populates="contacts")
