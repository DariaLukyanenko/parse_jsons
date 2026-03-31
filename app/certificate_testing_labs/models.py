from app.core.db import Base
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models_for_new_db_certs import TruncatedStringWithLog


class Certificate_Testing_Lab(Base):
    __tablename__ = "certificate_testing_labs"

    idTestingLab = Column(Integer)
    annex = Column(TruncatedStringWithLog(255))
    idRal = Column(Integer)
    regNumber = Column(TruncatedStringWithLog(255))
    fullName = Column(TruncatedStringWithLog(255))
    beginDate = Column(Date)
    endDate = Column(Date)
    basis = Column(TruncatedStringWithLog(255))
    accredEec = Column(Integer)
    idAccredPlace = Column(TruncatedStringWithLog(255))
    importedForResearchTesting = Column(Integer)
    actNumber = Column(TruncatedStringWithLog(255))
    actDate = Column(Date)
    actIdentificationNumber = Column(TruncatedStringWithLog(255))
    actIdentificationDate = Column(Date)
    created_at = Column(DateTime)

    certificate_id = Column(
        Integer,
        ForeignKey("certificate.id", ondelete="CASCADE"),
        nullable=False,
    )

    certificate = relationship("Certificate", back_populates="testing_labs")
    doc_confirm_customs = relationship(
        "Certificate_Testing_Lab_DocConfirmCustom",
        back_populates="testing_lab",
        cascade="all, delete",
    )
    protocols = relationship(
        "Certificate_Testing_Lab_Protocol",
        back_populates="testing_lab",
        cascade="all, delete",
    )


class Certificate_Testing_Lab_DocConfirmCustom(Base):
    __tablename__ = "certificate_testing_labs_docconfirmcustom"

    idDocConfirmCustom = Column(Integer)
    idDocConfirmCustomType = Column(Integer)
    otherDocs = Column(TruncatedStringWithLog(255))
    reasonNonRegistrCustomsDeclaration = Column(TruncatedStringWithLog(255))
    created_at = Column(DateTime)

    id_test_lab = Column(
        Integer,
        ForeignKey("certificate_testing_labs.id", ondelete="CASCADE"),
        nullable=False,
    )

    testing_lab = relationship("Certificate_Testing_Lab", back_populates="doc_confirm_customs")
    custom_infos = relationship(
        "Certificate_Testing_Lab_DocConfirmCustom_CustomInfo",
        back_populates="doc_confirm_custom",
        cascade="all, delete",
    )


class Certificate_Testing_Lab_DocConfirmCustom_CustomInfo(Base):
    __tablename__ = "certificate_testing_labs_docconfirmcustom_custominfo"

    idCustomInfo = Column(Integer)
    customDeclNumber = Column(TruncatedStringWithLog(255))

    id_doc_confirm_custom = Column(
        Integer,
        ForeignKey("certificate_testing_labs_docconfirmcustom.id", ondelete="CASCADE"),
        nullable=False,
    )

    doc_confirm_custom = relationship(
        "Certificate_Testing_Lab_DocConfirmCustom",
        back_populates="custom_infos",
    )


class Certificate_Testing_Lab_Protocol(Base):
    __tablename__ = "certificate_testing_labs_protocols"

    idProtocol = Column(Integer)
    idProtocolRpi = Column(Integer)
    number = Column(TruncatedStringWithLog(255))
    date = Column(Date)
    standards = Column(TruncatedStringWithLog(255))
    isProtocolInvalid = Column(Integer)
    created_at = Column(DateTime)

    id_test_lab = Column(
        Integer,
        ForeignKey("certificate_testing_labs.id", ondelete="CASCADE"),
        nullable=False,
    )

    testing_lab = relationship("Certificate_Testing_Lab", back_populates="protocols")
