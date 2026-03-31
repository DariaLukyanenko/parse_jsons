from app.core.db import Base
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey  # Date используется в Document
from sqlalchemy.orm import relationship
from app.models_for_new_db_certs import TruncatedStringWithLog


class Certificate_Product(Base):
    __tablename__ = "certificate_product"

    idProduct = Column(Integer)
    idProductOrigin = Column(TruncatedStringWithLog(255))
    fullName = Column(TruncatedStringWithLog(255))
    marking = Column(TruncatedStringWithLog(255))
    usageScope = Column(TruncatedStringWithLog(255))
    storageCondition = Column(TruncatedStringWithLog(255))
    usageCondition = Column(TruncatedStringWithLog(255))
    batchSize = Column(TruncatedStringWithLog(255))
    batchId = Column(TruncatedStringWithLog(255))
    identification = Column(TruncatedStringWithLog(255))
    created_at = Column(DateTime)

    id_certificate = Column(
        Integer,
        ForeignKey("certificate.id", ondelete="CASCADE"),
        nullable=False,
    )

    certificate = relationship("Certificate", back_populates="products")
    identifications = relationship(
        "Certificate_Product_Identification",
        back_populates="product",
        cascade="all, delete",
    )


class Certificate_Product_Identification(Base):
    __tablename__ = "certificate_product_identifications"

    idIdentification = Column(Integer)
    annex = Column(TruncatedStringWithLog(255))
    name = Column(TruncatedStringWithLog(255))
    type = Column(TruncatedStringWithLog(255))
    tradeMark = Column(TruncatedStringWithLog(255))
    model = Column(TruncatedStringWithLog(255))
    article = Column(TruncatedStringWithLog(255))
    sort = Column(TruncatedStringWithLog(255))
    idOkpds = Column(TruncatedStringWithLog(255))
    idTnveds = Column(TruncatedStringWithLog(255))
    gtin = Column(TruncatedStringWithLog(255))
    lifeTime = Column(TruncatedStringWithLog(255))
    storageTime = Column(TruncatedStringWithLog(255))
    description = Column(TruncatedStringWithLog(255))
    amount = Column(TruncatedStringWithLog(255))
    idOkei = Column(Integer)
    factoryNumber = Column(TruncatedStringWithLog(255))
    productionDate = Column(DateTime)
    expiryDate = Column(DateTime)
    created_at = Column(DateTime)

    id_product = Column(
        Integer,
        ForeignKey("certificate_product.id", ondelete="CASCADE"),
        nullable=False,
    )

    product = relationship("Certificate_Product", back_populates="identifications")
    documents = relationship(
        "Certificate_Product_Identification_Document",
        back_populates="identification",
        cascade="all, delete",
    )
    standards = relationship(
        "Certificate_Product_Identification_Standard",
        back_populates="identification",
        cascade="all, delete",
    )


class Certificate_Product_Identification_Document(Base):
    __tablename__ = "certificate_product_identifications_documents"

    id_doc = Column(Integer)
    name = Column(TruncatedStringWithLog(255))
    number = Column(TruncatedStringWithLog(255))
    date = Column(DateTime)
    created_at = Column(DateTime)

    id_identificate = Column(
        Integer,
        ForeignKey("certificate_product_identifications.id", ondelete="CASCADE"),
        nullable=False,
    )

    identification = relationship(
        "Certificate_Product_Identification",
        back_populates="documents",
    )


class Certificate_Product_Identification_Standard(Base):
    __tablename__ = "certificate_product_identifications_standarts"

    idStandard = Column(Integer)
    annex = Column(TruncatedStringWithLog(255))
    idDictStandard = Column(Integer)
    new_column = Column(Integer)
    designation = Column(TruncatedStringWithLog(255))
    name = Column(TruncatedStringWithLog(255))
    section = Column(TruncatedStringWithLog(255))
    addlInfo = Column(TruncatedStringWithLog(255))
    idStatus = Column(Integer)

    id_identificate = Column(
        Integer,
        ForeignKey("certificate_product_identifications.id", ondelete="CASCADE"),
        nullable=False,
    )

    identification = relationship(
        "Certificate_Product_Identification",
        back_populates="standards",
    )
