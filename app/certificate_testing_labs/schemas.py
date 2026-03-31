from datetime import date, datetime  # date используется в CertificateTestingLabBase и Protocol
from typing import Annotated, Any, List, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator
from app.models_for_new_db_certs import default_if_none


class CertTestingLabDocConfirmCustomInfoBase(BaseModel):
    idCustomInfo: Annotated[int, BeforeValidator(default_if_none)] = -1
    customDeclNumber: Annotated[str, BeforeValidator(default_if_none)] = "нет"


class CertTestingLabDocConfirmCustomInfoCreate(CertTestingLabDocConfirmCustomInfoBase):
    pass


class CertTestingLabDocConfirmCustomInfoRead(CertTestingLabDocConfirmCustomInfoBase):
    id: int
    id_doc_confirm_custom: int

    model_config = ConfigDict(from_attributes=True)


class CertTestingLabDocConfirmCustomBase(BaseModel):
    idDocConfirmCustom: Annotated[int, BeforeValidator(default_if_none)] = -1
    idDocConfirmCustomType: Annotated[int, BeforeValidator(default_if_none)] = -1
    otherDocs: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    reasonNonRegistrCustomsDeclaration: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    created_at: Optional[datetime] = None


class CertTestingLabDocConfirmCustomCreate(CertTestingLabDocConfirmCustomBase):
    custom_infos: Optional[List[CertTestingLabDocConfirmCustomInfoCreate]] = Field(default_factory=list)


class CertTestingLabDocConfirmCustomRead(CertTestingLabDocConfirmCustomBase):
    id: int
    id_test_lab: int
    custom_infos: List[CertTestingLabDocConfirmCustomInfoRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CertTestingLabProtocolBase(BaseModel):
    idProtocol: Annotated[int, BeforeValidator(default_if_none)] = -1
    idProtocolRpi: Annotated[int, BeforeValidator(default_if_none)] = -1
    number: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    date: Optional[date] = None
    standards: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    isProtocolInvalid: Annotated[int, BeforeValidator(default_if_none)] = -1
    created_at: Optional[datetime] = None

    @field_validator("isProtocolInvalid", mode="before")
    @classmethod
    def convert_bool_to_int(cls, v: Any) -> int:
        if v is None:
            return -1
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, int):
            return v
        return -1

    @field_validator("standards", mode="before")
    @classmethod
    def list_to_comma_string(cls, v: Any) -> str:
        if v is None or v == []:
            return "нет"
        if isinstance(v, list):
            return ",".join(str(x) for x in v)
        return v

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> Optional[date]:
        if v is None:
            return None
        if isinstance(v, date):
            return v if v.year >= 1753 else None
        if isinstance(v, str):
            for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                try:
                    d = datetime.strptime(v, fmt).date()
                    return d if d.year >= 1753 else None
                except ValueError:
                    pass
        return None


class CertTestingLabProtocolCreate(CertTestingLabProtocolBase):
    pass


class CertTestingLabProtocolRead(CertTestingLabProtocolBase):
    id: int
    id_test_lab: int

    model_config = ConfigDict(from_attributes=True)


class CertificateTestingLabBase(BaseModel):
    idTestingLab: Annotated[int, BeforeValidator(default_if_none)] = -1
    annex: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    idRal: Annotated[int, BeforeValidator(default_if_none)] = -1
    regNumber: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    fullName: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    beginDate: Optional[date] = None
    endDate: Optional[date] = None
    basis: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    accredEec: Annotated[int, BeforeValidator(default_if_none)] = -1
    idAccredPlace: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    importedForResearchTesting: Annotated[int, BeforeValidator(default_if_none)] = -1
    actNumber: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    actDate: Optional[date] = None
    actIdentificationNumber: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    actIdentificationDate: Optional[date] = None
    created_at: Optional[datetime] = None

    @field_validator("accredEec", "importedForResearchTesting", mode="before")
    @classmethod
    def convert_bool_to_int(cls, v: Any) -> int:
        if v is None:
            return -1
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, int):
            return v
        return -1

    @field_validator("beginDate", "endDate", "actDate", "actIdentificationDate", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> Optional[date]:
        if v is None:
            return None
        if isinstance(v, date):
            return v if v.year >= 1753 else None
        if isinstance(v, str):
            for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                try:
                    d = datetime.strptime(v, fmt).date()
                    return d if d.year >= 1753 else None
                except ValueError:
                    pass
        return None


class CertificateTestingLabCreate(CertificateTestingLabBase):
    doc_confirm_customs: Optional[List[CertTestingLabDocConfirmCustomCreate]] = Field(default_factory=list)
    protocols: Optional[List[CertTestingLabProtocolCreate]] = Field(default_factory=list)


class CertificateTestingLabRead(CertificateTestingLabBase):
    id: int
    certificate_id: int
    doc_confirm_customs: List[CertTestingLabDocConfirmCustomRead] = Field(default_factory=list)
    protocols: List[CertTestingLabProtocolRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
