# -*- coding: utf-8 -*-
from contextvars import ContextVar
import logging
from typing import Any, Optional
from sqlalchemy import (Column, Date, DateTime, ForeignKey, Index, Integer, String,
                        UniqueConstraint, func, Integer, Text, TypeDecorator, 
                        ForeignKeyConstraint, BigInteger, text, types)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.core.db import Base
from app.log import log_function

# Контекстная переменная для хранения информации о текущей записи
current_record_context: ContextVar[Optional[dict]] = ContextVar('current_record_context', default=None)


class RecordContext:
    """Контекстный менеджер для установки информации о текущей записи"""
    
    def __init__(self, record_type: str, record_id: Any = None, extra_info: str = None):
        """
        Args:
            record_type: Тип записи (Certificate, Applicant, Manufacturer и т.д.)
            record_id: ID записи (idCertificate, inn и т.д.)
            extra_info: Дополнительная информация (номер сертификата и т.д.)
        """
        self.context_data = {
            "record_type": record_type,
            "record_id": record_id,
            "extra_info": extra_info
        }
        self.token = None
    
    def __enter__(self):
        self.token = current_record_context.set(self.context_data)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        current_record_context.reset(self.token)
        return False
    
    @staticmethod
    def get_context_string() -> str:
        """Получить строку с информацией о текущем контексте"""
        ctx = current_record_context.get()
        if ctx is None:
            return "Контекст не установлен"
        
        parts = []
        if ctx.get("record_type"):
            parts.append(f"Тип: {ctx['record_type']}")
        if ctx.get("record_id"):
            parts.append(f"ID: {ctx['record_id']}")
        if ctx.get("extra_info"):
            parts.append(f"Доп.инфо: {ctx['extra_info']}")
        
        return " | ".join(parts) if parts else "Контекст пуст"
    
    
class TruncatedStringWithLog(types.TypeDecorator):
    impl = types.String
    cache_ok = True
    
    def __init__(self, length=255, *args, **kwargs):
        super().__init__(length, *args, **kwargs)
        self.length = length
    
    def process_bind_param(self, value, dialect):
        if value is not None and isinstance(value, str) and len(value) > self.length:
            original_length = len(value)
            truncated_value = value[:self.length]
            
            # Получаем контекст текущей записи
            context_info = RecordContext.get_context_string()
            
            logging.warning(
                f"Обрезка строки. [{context_info}] "
                f"Исходная длина: {original_length}, обрезано до: {self.length}. "
                f"Начало строки: '{truncated_value[:50]}...'"
            )
            
            return truncated_value
        return value
    
    
class ContactMixin:
    """Абстрактный набор колонок для контактных таблиц."""
    idContact = Column(Integer, nullable=False)
    idContactType = Column(Integer)
    value = Column(TruncatedStringWithLog(255))

    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)
    

class AddressMixin:
    """Абстрактный набор колонок для адресных таблиц."""
    idAddress = Column(Integer, nullable=False)
    idAddrType = Column(Integer)
    idCodeOksm = Column(TruncatedStringWithLog(255))
    oksmShort = Column(Integer)

    idSubject = Column(TruncatedStringWithLog(255))
    idDistrict = Column(TruncatedStringWithLog(255))
    idCity = Column(TruncatedStringWithLog(255))
    idLocality = Column(TruncatedStringWithLog(255))
    idStreet = Column(TruncatedStringWithLog(255))
    idHouse = Column(TruncatedStringWithLog(255))

    flat = Column(TruncatedStringWithLog(255))
    postCode = Column(TruncatedStringWithLog(255))

    fullAddress = Column(TruncatedStringWithLog(255))
    gln = Column(TruncatedStringWithLog(255))

    foreignDistrict = Column(TruncatedStringWithLog(255))
    foreignCity = Column(TruncatedStringWithLog(255))
    foreignLocality = Column(TruncatedStringWithLog(255))
    foreignStreet = Column(TruncatedStringWithLog(255))
    foreignHouse = Column(TruncatedStringWithLog(255))

    uniqueAddress = Column(TruncatedStringWithLog(255))
    otherGln = Column(TruncatedStringWithLog(255))
    glonass = Column(TruncatedStringWithLog(255))

    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)


# -------------------------
# certificate
# -------------------------
class Certificate(Base):
    """
    Attributes:
        id (BigInteger): Primary key.
        idCertificate (BigInteger): Certificate identifier.
        idCertScheme (BigInteger): Certification scheme identifier.
        idObjectCertType (BigInteger): Object certification type identifier.
        idCertType (BigInteger): Certificate type identifier.
        isTs (Integer): Indicates if it is a TS certificate.
        idProductSingleLists (BigInteger): Product single list identifier.
        awaitForApprove (Integer): Awaiting approval status.
        idStatus (BigInteger): Status identifier.
        expiredInspectionControl (Integer): Expired inspection control flag.
        editApp (Integer): Edit application flag.
        assignRegNumber (Integer): Assign registration number flag.
        number (TruncatedStringWithLog(255)): Certificate number.
        certRegDate (Date): Certificate registration date.
        certEndDate (Date): Certificate end date.
        idBlank (BigInteger): Blank identifier.
        blankNumber (TruncatedStringWithLog(255)): Blank number.
        noSanction (Integer): No sanction flag.
        batchInspection (TruncatedStringWithLog(255)): Batch inspection information.
        inspectionControlPlanDate (TruncatedStringWithLog(255)): Inspection control plan date.
        idSigner (BigInteger): Signer identifier.
        idEmployee (BigInteger): Employee identifier.
        firstName (TruncatedStringWithLog(255)): First name of the employee.
        surname (TruncatedStringWithLog(255)): Surname of the employee.
        patronymic (TruncatedStringWithLog(255)): Patronymic of the employee.
        date_from (DateTime): Start date.
        date_to (DateTime): End date.
        created_at (DateTime): Creation timestamp.

    Relationships:
        annexes: List of related CertificateAnnex objects.
    """
    #ссылка на файл добавить 
    idCertificate = Column(Integer, nullable=False)
    idCertScheme = Column(Integer)
    idObjectCertType = Column(Integer)
    idCertType = Column(Integer, nullable=False)
    isTs = Column(Integer)
    # store as CSV TruncatedStringWithLog(255) in DB, expose as list[int] via property
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

    # relations
    annexes = relationship("Certificate_Annex", back_populates="certificate")
    applicants = relationship(
        "Certificate_applicant",
        back_populates="certificate"
    )
    manufacturers = relationship(
        "Certificate_Manufacturer",
        back_populates="certificate"
    )

    # add relation for certification authorities (used later)
    certification_authorities = relationship(
        "Certificate_Certification_Authority",
        back_populates="certificate"
    )
    
    # add one-to-many relation to tech reglaments
    tech_reglaments = relationship(
        "Certificate_has_tech_reglaments",
        back_populates="certificate"
    )
    
    
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


# Utility: attach tech reglament ids to a Certificate instance
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
    
    
# -------------------------
# certificate_annexes
# -------------------------
class Certificate_Annex(Base):
    """
    Attributes:
        idAnnex (Integer): Annex identifier.
        idType (Integer): Type identifier of the annex.
        ord (Integer): Order of the annex.
        pageCount (Integer): Number of pages in the annex.
        id_certificate (Integer): Foreign key to the parent certificate.

    Relationships:
        certificate: The parent Certificate object.
        blanks: List of related CertificateAnnexBlank objects.
    """
    idAnnex = Column(Integer, nullable=False)
    idType = Column(Integer)
    ord = Column(Integer)
    pageCount = Column(Integer)

    id_certificate = Column(
        Integer,
        ForeignKey("certificate.id", ondelete="CASCADE"),
        nullable=False
    )

    certificate = relationship("Certificate", back_populates="annexes")
    blanks = relationship("Certificate_AnnexBlank", back_populates="annex")
    


# -------------------------
# certificate_annexes_annexBlanks
# -------------------------
class Certificate_AnnexBlank(Base):
    """
    Attributes:
        idBlank (Integer): Identifier of the blank.
        blankNumber (TruncatedStringWithLog(255)): Number of the blank.
        id_annexes (Integer): Foreign key to the parent annex.

    Relationships:
        annex: The parent Certificate_Annex object.
    """
    idBlank = Column(Integer, nullable=False)
    blankNumber = Column(TruncatedStringWithLog(255))
    id_annexes = Column(
        Integer,
        ForeignKey("certificate_annex.id", ondelete="CASCADE"),
        nullable=False
    )

    annex = relationship("Certificate_Annex", back_populates="blanks")
    

# ---------------------------------------------------------
# certificate_applicant
# ---------------------------------------------------------
class Certificate_applicant(Base):
    """
    Attributes:
        id (Integer): Primary key.
        idLegalSubject (Integer): Legal subject identifier.
        idEgrul (Integer): EGRUL identifier.
        idApplicantType (Integer): Applicant type identifier.
        idLegalSubjectType (Integer): Legal subject type identifier.
        fullName (TruncatedStringWithLog(255)): Full name of the applicant.
        shortName (TruncatedStringWithLog(255)): Short name of the applicant.
        idPerson (Integer): Person identifier.
        surname (TruncatedStringWithLog(255)): Surname of the applicant.
        firstName (TruncatedStringWithLog(255)): First name of the applicant.
        patronymic (TruncatedStringWithLog(255)): Patronymic of the applicant.
        headPosition (TruncatedStringWithLog(255)): Head position.
        ogrn (TruncatedStringWithLog(255)): OGRN number.
        ogrnAssignDate (Date): OGRN assignment date.
        inn (TruncatedStringWithLog(255)): INN number.
        kpp (TruncatedStringWithLog(255)): KPP number.
        idLegalForm (Integer): Legal form identifier.
        regDate (Date): Registration date.
        regOrganName (TruncatedStringWithLog(255)): Registration authority name.
        addlRegInfo (TruncatedStringWithLog(255)): Additional registration information.
        isEecRegister (Integer): EEC register flag.
        transnational (Integer): Transnational flag.
        passportIssueDate (Date): Passport issue date.
        passportIssuedBy (TruncatedStringWithLog(255)): Passport issued by.
        passportNum (TruncatedStringWithLog(255)): Passport number.
        idPersonDoc (Integer): Person document identifier.
        date_from (DateTime): Start date.
        date_to (DateTime): End date.
        created_at (DateTime): Creation timestamp.
        id_certificate (Integer): Foreign key to the parent certificate.

    Relationships:
        addresses: List of related CertificateApplicantAddress objects.
        contacts: List of related CertificateApplicantContact objects.
    """
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

    id_certificate = Column(
        Integer,
        ForeignKey("certificate.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # relations
    certificate = relationship("Certificate", back_populates="applicants")
    
    addresses = relationship(
        "Certificate_Applicant_Address",
        back_populates="applicant",
        cascade="all, delete"
    )

    contacts = relationship(
        "Certificate_Applicant_Contact",
        back_populates="applicant",
        cascade="all, delete"
    )
    

# ---------------------------------------------------------
# certificate_applicant_addresses
# ---------------------------------------------------------
class Certificate_Applicant_Address(Base, AddressMixin):
    """
    Attributes:
        id_applicant (Integer): Foreign key to the parent applicant.
        idAddress (Integer): Address identifier.
        idAddType (Integer): Address type identifier.
        idCodeOksm (TruncatedStringWithLog(255)): OKSM code.
        oksmShort (Integer): Short OKSM flag.
        idSubject (Integer): Subject identifier.
        idDistrict (TruncatedStringWithLog(255)): District identifier.
        idCity (TruncatedStringWithLog(255)): City identifier.
        idLocality (TruncatedStringWithLog(255)): Locality identifier.
        idStreet (TruncatedStringWithLog(255)): Street identifier.
        idHouse (TruncatedStringWithLog(255)): House identifier.
        flat (TruncatedStringWithLog(255)): Flat/apartment.
        postCode (TruncatedStringWithLog(255)): Postal code.
        fullAddress (TruncatedStringWithLog(255)): Full address.
        gln (TruncatedStringWithLog(255)): GLN code.
        foreignDistrict (TruncatedStringWithLog(255)): Foreign district.
        foreignCity (TruncatedStringWithLog(255)): Foreign city.
        foreignLocality (TruncatedStringWithLog(255)): Foreign locality.
        foreignStreet (TruncatedStringWithLog(255)): Foreign street.
        foreignHouse (TruncatedStringWithLog(255)): Foreign house.
        uniqueAddress (TruncatedStringWithLog(255)): Unique address.
        otherGln (TruncatedStringWithLog(255)): Other GLN.
        glonass (TruncatedStringWithLog(255)): GLONASS coordinates.
        date_from (DateTime): Start date.
        date_to (DateTime): End date.
        created_at (DateTime): Creation timestamp.

    Relationships:
        applicant: The parent CertificateApplicant object.
    """
    id_applicant = Column(
        Integer,
        ForeignKey("certificate_applicant.id", ondelete="CASCADE"),
        nullable=False
    )

    applicant = relationship("Certificate_applicant", back_populates="addresses")
    


# ---------------------------------------------------------
# certificate_applicant_contacts
# ---------------------------------------------------------
class Certificate_Applicant_Contact(Base, ContactMixin):
    """
    Attributes:
        idContact (Integer): Contact identifier.
        id_applicant (Integer): Foreign key to the parent applicant.
        idContactType (Integer): Contact type identifier.
        value (TruncatedStringWithLog(255)): Contact value.
        date_from (DateTime): Start date.
        date_to (DateTime): End date.
        created_at (DateTime): Creation timestamp.

    Relationships:
        applicant: The parent CertificateApplicant object.
    """
    
    id_applicant = Column(
        Integer,
        ForeignKey("certificate_applicant.id", ondelete="CASCADE"),
        nullable=False
    )

    applicant = relationship("Certificate_applicant", back_populates="contacts")


# ---------------------------------------------------------
# certificate_manufacturer
# ---------------------------------------------------------
class Certificate_Manufacturer(Base):
    """
    Attributes:
        __table_args__ (tuple): Table-level constraints (unique constraint on inn,kpp).

        idLegalSubject (Integer): Identifier of the legal subject record (if manufacturer is a legal entity).
        idEgrul (Integer): Reference to EGRUL record.
        idLegalSubjectType (Integer): Type code of the legal subject.

        fullName (TruncatedStringWithLog(255)): Full legal name of the manufacturer.
        shortName (TruncatedStringWithLog(255)): Short/common name.

        idPerson (Integer): Identifier of the person record (if manufacturer is an individual).
        surname (TruncatedStringWithLog(255)): Person's surname.
        firstName (TruncatedStringWithLog(255)): Person's given name.
        patronymic (TruncatedStringWithLog(255)): Person's patronymic/middle name.

        headPosition (TruncatedStringWithLog(255)): Position/title of the head/representative.
        ogrn (TruncatedStringWithLog(255)): Primary State Registration Number for legal entities.
        ogrnAssignDate (Date): Date of OGRN assignment.

        inn (TruncatedStringWithLog(255)): Taxpayer Identification Number (required, part of unique key).
        kpp (TruncatedStringWithLog(255)): Tax Registration Reason Code (required, part of unique key).

        idLegalForm (Integer): Identifier of legal form/type.

        regDate (Date): Registration date of the legal subject.
        regOrganName (TruncatedStringWithLog(255)): Name of registering authority.
        addlRegInfo (TruncatedStringWithLog(255)): Additional registration information.

        isEecRegister (Integer): Flag indicating registration in EEC register.
        transnational (TruncatedStringWithLog(255)): Transnational flag or related info.

        passportIssueDate (Date): Passport issue date (for person).
        passportIssuedBy (TruncatedStringWithLog(255)): Issuing authority for passport.
        passportNum (Integer): Passport number (for person).

        idPersonDoc (Integer): Identifier for person document record.

        id_certificate (Integer): Foreign key to parent Certificate (required).

        date_from (DateTime): Validity start datetime.
        date_to (DateTime): Validity end datetime.
        created_at (DateTime): Record creation timestamp.

    Notes:
        - A unique constraint enforces uniqueness of (inn, kpp) across manufacturers.
        - Either legal-entity fields or person fields can be used depending on manufacturer type.
    """

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

    # --- связь с certificate ---
    id_certificate = Column(
        Integer,
        ForeignKey("certificate.id", ondelete="CASCADE"),
        nullable=False
    )

    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)

    # ORM-связь
    certificate = relationship("Certificate", back_populates='manufacturers')
    contacts = relationship("Certificate_Manufacturer_Contact", back_populates='manufacturer')
    addresses = relationship("Certificate_Manufacturer_Address", back_populates='manufacturer')


class Certificate_Manufacturer_Contact(Base, ContactMixin):
    id_manufacturer = Column(
        Integer,
        ForeignKey("certificate_manufacturer.id", ondelete="CASCADE"),
        nullable=False
    )

    manufacturer = relationship("Certificate_Manufacturer", back_populates="contacts")


class Certificate_Manufacturer_Address(Base, AddressMixin):
    id_manufacturer = Column(
        Integer,
        ForeignKey("certificate_manufacturer.id", ondelete="CASCADE"),
        nullable=False
    )

    manufacturer = relationship("Certificate_Manufacturer", back_populates="addresses")


class Certificate_Certification_Authority(Base):
    
    idCertificationAuthority = Column(Integer, nullable=False)
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

    # --- связь с certificate ---
    certificate_id = Column(
        Integer,
        ForeignKey("certificate.id", ondelete="CASCADE"),
        nullable=False
    )

    certificate = relationship("Certificate", back_populates="certification_authorities")
    contacts = relationship("Certificate_Auth_Contact", back_populates="auth")
    addresses = relationship("Certificate_Auth_Address", back_populates="auth")
    

class Certificate_Auth_Contact(Base, ContactMixin):
    id_auth = Column(
        Integer,
        ForeignKey("certificate_certification_authority.id", ondelete="CASCADE"),
        nullable=False
    )

    auth = relationship("Certificate_Certification_Authority", back_populates="contacts")


class Certificate_Auth_Address(Base, AddressMixin):
    id_auth = Column(
        Integer,
        ForeignKey("certificate_certification_authority.id", ondelete="CASCADE"),
        nullable=False
    )

    auth = relationship("Certificate_Certification_Authority", back_populates="addresses")
