# -*- coding: utf-8 -*-
from datetime import date, datetime
from typing import Annotated, Any, Literal, Optional, List
from pydantic import BaseModel, BeforeValidator, Field, ConfigDict, field_validator, model_validator
from pydantic_core import PydanticUseDefault


def default_if_none(value: Any) -> Any:
    if value is None:
        raise PydanticUseDefault()
    return value

# -------------------------
# Base Schemas (Mixins)
# -------------------------
class ContactBase(BaseModel):
    """Базовая схема для контактной информации"""
    idContact: Annotated[int, BeforeValidator(default_if_none)]= -1
    idContactType: Annotated[int, BeforeValidator(default_if_none)]= -1
    value: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    created_at: Optional[datetime] = None


class AddressBase(BaseModel):
    """Базовая схема для адресной информации"""
    idAddress: Annotated[int, BeforeValidator(default_if_none)]= -1
    idAddrType: Annotated[int, BeforeValidator(default_if_none)]= -1
    idCodeOksm: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    oksmShort: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    idSubject: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    idDistrict: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    idCity: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    idLocality: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    idStreet: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    idHouse: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    flat: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    postCode: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    fullAddress: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    gln: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    foreignDistrict: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    foreignCity: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    foreignLocality: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    foreignStreet: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    foreignHouse: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    uniqueAddress: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    otherGln: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    glonass: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    @field_validator(
        "oksmShort",
        mode="before"
    )
    @classmethod
    def convert_bool_to_int(cls, v: Any) -> int:
        """Конвертация bool в int: True=1, False=0, None=-1"""
        if v is None:
            return -1
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, int):
            return v
        return -1


# -------------------------
# Certificate Annexes Schemas
# -------------------------
class CertificateAnnexBlankBase(BaseModel):
    """Базовая схема для бланков приложений"""
    idBlank: int
    blankNumber: Annotated[str, BeforeValidator(default_if_none)]= None


class CertificateAnnexBlankCreate(CertificateAnnexBlankBase):
    pass


class CertificateAnnexBlankRead(CertificateAnnexBlankBase):
    id_annexes: int
    
    model_config = ConfigDict(from_attributes=True)


class CertificateAnnexBase(BaseModel):
    """Базовая схема для приложений сертификата"""
    idAnnex: int
    idType: Annotated[int, BeforeValidator(default_if_none)]= None
    ord: Annotated[int, BeforeValidator(default_if_none)]= None
    pageCount: Annotated[int, BeforeValidator(default_if_none)]= None


class CertificateAnnexCreate(CertificateAnnexBase):
    blanks: Optional[List[CertificateAnnexBlankCreate]] = Field(default_factory=list, alias="annexBlanks")


class CertificateAnnexRead(CertificateAnnexBase):
    id: int
    id_certificate: int
    blanks: List[CertificateAnnexBlankRead] = Field(default_factory=list, alias="annexBlanks")
    
    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Applicant Schemas
# -------------------------
class ApplicantContactCreate(ContactBase):
    pass


class ApplicantContactRead(ContactBase):
    id: int
    id_applicant: int
    
    model_config = ConfigDict(from_attributes=True)


class ApplicantAddressCreate(AddressBase):
    pass


class ApplicantAddressRead(AddressBase):
    id: int
    id_applicant: int
    
    model_config = ConfigDict(from_attributes=True)


class ApplicantBase(BaseModel):
    """Базовая схема для заявителя"""
    idLegalSubject: int
    idEgrul: Annotated[int, BeforeValidator(default_if_none)]= -1
    idApplicantType: Annotated[int, BeforeValidator(default_if_none)]= -1
    idLegalSubjectType: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    fullName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    shortName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    idPerson: Annotated[int, BeforeValidator(default_if_none)]= -1
    surname: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    firstName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    patronymic: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    headPosition: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    ogrn: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    ogrnAssignDate: Optional[date] = None
    
    inn: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    kpp: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    idLegalForm: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    regDate: Optional[date] = None
    regOrganName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    addlRegInfo: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    isEecRegister: Annotated[int, BeforeValidator(default_if_none)]= -1
    transnational: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    passportIssueDate: Optional[date] = None
    passportIssuedBy: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    passportNum: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    idPersonDoc: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    @field_validator(
        "isEecRegister",
        mode="before"
    )
    @classmethod
    def convert_bool_to_int(cls, v: Any) -> int:
        """Конвертация bool в int: True=1, False=0, None=-1"""
        if v is None:
            return -1
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, int):
            return v
        return -1
    
    @field_validator("transnational", mode="before")
    def list_to_comma_string(cls, v):
        if v is None or v == []:
            return None
        if isinstance(v, list):
            return ",".join(str(x) for x in v)
        return v


class ApplicantCreate(ApplicantBase):
    addresses: Optional[List[ApplicantAddressCreate]] = Field(default_factory=list)
    contacts: Optional[List[ApplicantContactCreate]] = Field(default_factory=list)


class ApplicantRead(ApplicantBase):
    id: int
    id_certificate: int
    addresses: List[ApplicantAddressRead] = Field(default_factory=list)
    contacts: List[ApplicantContactRead] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Manufacturer Schemas
# -------------------------
class ManufacturerContactCreate(ContactBase):
    pass


class ManufacturerContactRead(ContactBase):
    id: int
    id_manufacturer: int
    
    model_config = ConfigDict(from_attributes=True)


class ManufacturerAddressCreate(AddressBase):
    pass


class ManufacturerAddressRead(AddressBase):
    id: int
    id_manufacturer: int
    
    model_config = ConfigDict(from_attributes=True)


class ManufacturerBase(BaseModel):
    """Базовая схема для производителя"""
    idLegalSubject: int
    idEgrul: Annotated[int, BeforeValidator(default_if_none)]= -1
    idLegalSubjectType: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    fullName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    shortName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    idPerson: int
    surname: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    firstName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    patronymic: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    headPosition: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    ogrn: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    ogrnAssignDate: Optional[date] = None
    
    inn: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    kpp: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    idLegalForm: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    regDate: Optional[date] = None
    regOrganName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    addlRegInfo: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    isEecRegister: Annotated[int, BeforeValidator(default_if_none)]= -1
    transnational: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    passportIssueDate: Optional[date] = None
    passportIssuedBy: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    passportNum: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    idPersonDoc: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    @field_validator(
        "isEecRegister",
        mode="before"
    )
    @classmethod
    def convert_bool_to_int(cls, v: Any) -> int:
        """Конвертация bool в int: True=1, False=0, None=-1"""
        if v is None:
            return -1
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, int):
            return v
        return -1
    
    @field_validator("transnational", mode="before")
    def list_to_comma_string(cls, v):
        if v is None or v == []:
            return None
        if isinstance(v, list):
            return ",".join(str(x) for x in v)
        return v

class ManufacturerCreate(ManufacturerBase):
    addresses: Optional[List[ManufacturerAddressCreate]] = Field(default_factory=list)
    contacts: Optional[List[ManufacturerContactCreate]] = Field(default_factory=list)


class Manufacturer(ManufacturerBase):
    id: int
    id_certificate: int
    addresses: List[ManufacturerAddressRead] = Field(default_factory=list)
    contacts: List[ManufacturerContactRead] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Certification Authority Schemas
# -------------------------
class CertAuthContactCreate(ContactBase):
    pass


class CertAuthContactRead(ContactBase):
    id: int
    id_auth: int
    
    model_config = ConfigDict(from_attributes=True)


class CertAuthAddressCreate(AddressBase):
    pass


class CertAuthAddressRead(AddressBase):
    id: int
    id_auth: int
    
    model_config = ConfigDict(from_attributes=True)


class CertificationAuthorityBase(BaseModel):
    """Базовая схема для органа сертификации"""
    idCertificationAuthority: int
    fullName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    accredOrgName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    attestatRegNumber: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    attestatRegDate: Optional[date] = None
    attestatEndDate: Optional[date] = None
    
    idRal: Annotated[int, BeforeValidator(default_if_none)]= -1
    ogrn: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    idPerson: Annotated[int, BeforeValidator(default_if_none)]= -1
    firstName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    surname: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    patronymic: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    
    prevAttestatRegNumber: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    prevIdRal: Annotated[int, BeforeValidator(default_if_none)]= -1
    
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    created_at: Optional[datetime] = None


class CertificationAuthorityCreate(CertificationAuthorityBase):
    addresses: Optional[List[CertAuthAddressCreate]] = Field(default_factory=list)
    contacts: Optional[List[CertAuthContactCreate]] = Field(default_factory=list)


class CertificationAuthorityRead(CertificationAuthorityBase):
    id: int
    certificate_id: int
    addresses: List[CertAuthAddressRead] = Field(default_factory=list)
    contacts: List[CertAuthContactRead] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# -------------------------
# TechReglament (association) Schemas
# -------------------------
class CertificateTechReglamentCreate(BaseModel):
    """Схема для создания записи связки сертификат -> техрегламент"""
    tech_reglaments: int


class CertificateTechReglamentRead(BaseModel):
    """Схема чтения записи связки"""
    tech_reglaments: int
    id_certificate: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Certificate Schemas
# -------------------------
class CertificateBase(BaseModel):
    """Базовая схема для сертификата"""
    idCertificate: int
    idTechnicalReglaments: Optional[List[int]] = []
    idProductSingleLists: Annotated[str, BeforeValidator(default_if_none)]= '-1'
    idCertScheme: Annotated[int, BeforeValidator(default_if_none)]= -1
    idObjectCertType: Annotated[int, BeforeValidator(default_if_none)]= -1
    idCertType: Annotated[int, BeforeValidator(default_if_none)]= -1
    isTs: Annotated[int, BeforeValidator(default_if_none)]= -1
    awaitForApprove: Annotated[int, BeforeValidator(default_if_none)]= -1
    idStatus: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    expiredInspectionControl: Annotated[int, BeforeValidator(default_if_none)]= -1
    editApp: Annotated[int, BeforeValidator(default_if_none)]= -1
    assignRegNumber: Annotated[int, BeforeValidator(default_if_none)]= -1
    number: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    certRegDate: Optional[date] = None
    certEndDate: Optional[date] = None
    idBlank: Annotated[int, BeforeValidator(default_if_none)]= -1
    blankNumber: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    noSanction: Annotated[int, BeforeValidator(default_if_none)]= -1
    batchInspection: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    inspectionControlPlanDate: Optional[date] = None
    idSigner: Annotated[int, BeforeValidator(default_if_none)]= -1
    idEmployee: Annotated[int, BeforeValidator(default_if_none)]= -1
    firstName: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    surname: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    patronymic: Annotated[str, BeforeValidator(default_if_none)]= 'нет'
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    @field_validator(
        "isTs", 
        "awaitForApprove", 
        "expiredInspectionControl", 
        "editApp", 
        "assignRegNumber", 
        "noSanction",
        mode="before"
    )
    @classmethod
    def convert_bool_to_int(cls, v: Any) -> int:
        """Конвертация bool в int: True=1, False=0, None=-1"""
        if v is None:
            return -1
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, int):
            return v
        return -1
    
    @field_validator("idProductSingleLists", mode="before")
    def list_to_comma_string(cls, v):
        if v is None or v == []:
            return None
        if isinstance(v, list):
            return ",".join(str(x) for x in v)
        return v

    @field_validator("idTechnicalReglaments", mode="before")
    def convert_tech_regs(cls, v):
        if isinstance(v, list):
            # список Annotated[int, BeforeValidator(default_if_none)]→ список объектов модели
            return [
                {"tech_reglaments": item} if isinstance(item, int) else item
                for item in v
            ]
        return v
    
    @field_validator("certRegDate", "certEndDate", mode="before")
    def parse_date(cls, v):
        if v is None:
            return None

        # Уже date → проверяем год
        if isinstance(v, date):
            return v if v.year >= 1753 else None

        # ISO формат: "YYYY-MM-DD"
        if isinstance(v, str):
            try:
                d = date.fromisoformat(v)
                return d if d.year >= 1753 else None
            except:
                pass

            # Формат "DD.MM.YYYY"
            try:
                d = datetime.strptime(v, "%d.%m.%Y").date()
                return d if d.year >= 1753 else None
            except:
                pass

        return None
            
        
    @field_validator("idStatus", mode="before")
    def convert_status(cls, value):
        status_map = {
            1: 'Архивный',  
            3: 'Возобновлен',
            6: 'Действует',
            11: 'Недействителен',
            13: 'Отправлен',
            14: 'Прекращён',  
            15: 'Приостановлен',
            16: 'Продлен',
        }
        return status_map.get(value, value)


class CertificateCreate(CertificateBase):
    """Схема для создания сертификата"""
    annexes: Optional[List[CertificateAnnexCreate]] = Field(default_factory=list)
    applicant: Optional[ApplicantCreate] = None
    manufacturer: Optional[ManufacturerCreate] = None
    certificationAuthority: Optional[CertificationAuthorityCreate] = None
    idTechnicalReglaments: List[CertificateTechReglamentCreate] = Field(default_factory=list)

'''
class CertificateUpdate(BaseModel):
    """Схема для обновления сертификата"""
    idCertScheme: Annotated[int, BeforeValidator(default_if_none)]= None
    idObjectCertType: Annotated[int, BeforeValidator(default_if_none)]= None
    idCertType: Annotated[int, BeforeValidator(default_if_none)]= None
    isTs: Optional[bool] = None
    idProductSingleLists: Annotated[int, BeforeValidator(default_if_none)]= None
    awaitForApprove: Optional[bool] = None
    idStatus: Annotated[int, BeforeValidator(default_if_none)]= None
    expiredInspectionControl: Optional[bool] = None
    editApp: Optional[bool] = None
    assignRegNumber: Optional[bool] = None
    number: Annotated[str, BeforeValidator(default_if_none)]= None
    certRegDate: Optional[date] = None
    certEndDate: Optional[date] = None
    idBlank: Annotated[int, BeforeValidator(default_if_none)]= None
    blankNumber: Annotated[str, BeforeValidator(default_if_none)]= None
    noSanction: Optional[bool] = None
    batchInspection: Annotated[str, BeforeValidator(default_if_none)]= None
    inspectionControlPlanDate: Annotated[str, BeforeValidator(default_if_none)]= None
    idSigner: Annotated[int, BeforeValidator(default_if_none)]= None
    idEmployee: Annotated[int, BeforeValidator(default_if_none)]= None
    firstName: Annotated[str, BeforeValidator(default_if_none)]= None
    surname: Annotated[str, BeforeValidator(default_if_none)]= None
    patronymic: Annotated[str, BeforeValidator(default_if_none)]= None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None'''


class Certificate(CertificateBase):
    """Полная схема сертификата с вложенными объектами"""
    id: int
    annexes: List[CertificateAnnexRead] = []
    applicants: List[ApplicantRead] = []
    manufacturers: List[Manufacturer] = []
    certification_authorities: List[CertificationAuthorityRead] = []
    tech_reglaments: List[CertificateTechReglamentRead] = []
    
    model_config = ConfigDict(from_attributes=True)


'''class CertificateList(BaseModel):
    """Схема для списка сертификатов с пагинацией"""
    items: List[Certificate]
    total: int
    page: Annotated[int, BeforeValidator(default_if_none)]= Field(ge=1)
    size: Annotated[int, BeforeValidator(default_if_none)]= Field(ge=1, le=100)
    pages: int


# -------------------------
# Response Schemas
# -------------------------
class CertificateResponse(BaseModel):
    """Схема ответа для сертификата"""
    success: bool = True
    data: Certificate
    message: Annotated[str, BeforeValidator(default_if_none)]= None


class CertificateListResponse(BaseModel):
    """Схема ответа для списка сертификатов"""
    success: bool = True
    data: CertificateList
    message: Annotated[str, BeforeValidator(default_if_none)]= None


class ErrorResponse(BaseModel):
    """Схема для ошибок"""
    success: bool = False
    message: str
    details: Optional[dict] = None


# -------------------------
# Filter Schemas
# -------------------------
class CertificateFilter(BaseModel):
    """Схема для фильтрации сертификатов"""
    number: Annotated[str, BeforeValidator(default_if_none)]= None
    certRegDateFrom: Optional[date] = None
    certRegDateTo: Optional[date] = None
    certEndDateFrom: Optional[date] = None
    certEndDateTo: Optional[date] = None
    idStatus: Annotated[int, BeforeValidator(default_if_none)]= None
    idCertType: Annotated[int, BeforeValidator(default_if_none)]= None
    applicantInn: Annotated[str, BeforeValidator(default_if_none)]= None
    manufacturerInn: Annotated[str, BeforeValidator(default_if_none)]= None'''