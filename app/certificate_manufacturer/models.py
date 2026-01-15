from app.core.db import Base
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from app.models_for_new_db_certs import TruncatedStringWithLog, AddressMixin, ContactMixin

class Certificate_Manufacturer(Base):
    __tablename__ = 'certificate_manufacturer'

    idLegalSubject = Column(Integer, nullable=False)
    idEgrul = Column(Integer)
    idLegalSubjectType = Column(Integer)
    fullName = Column(TruncatedStringWithLog(255))
    shortName = Column(TruncatedStringWithLog(255))
    idPerson = Column(Integer, nullable=False)
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
    passportNum = Column(Integer)
    idPersonDoc = Column(Integer)
    id_certificate = Column(Integer, ForeignKey("certificate.id", ondelete="CASCADE"), nullable=False)
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)
    certificate = relationship("Certificate", back_populates='manufacturers')
    contacts = relationship("Certificate_Manufacturer_Contact", back_populates='manufacturer')
    addresses = relationship("Certificate_Manufacturer_Address", back_populates='manufacturer')

class Certificate_Manufacturer_Contact(Base, ContactMixin):
    __tablename__ = 'certificate_manufacturer_contact'

    id_manufacturer = Column(Integer, ForeignKey("certificate_manufacturer.id", ondelete="CASCADE"), nullable=False)
    manufacturer = relationship("Certificate_Manufacturer", back_populates="contacts")

class Certificate_Manufacturer_Address(Base, AddressMixin):
    __tablename__ = 'certificate_manufacturer_address'

    id_manufacturer = Column(Integer, ForeignKey("certificate_manufacturer.id", ondelete="CASCADE"), nullable=False)
    manufacturer = relationship("Certificate_Manufacturer", back_populates="addresses")
