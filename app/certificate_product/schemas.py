from datetime import datetime
from typing import Annotated, Any, List, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator
from app.models_for_new_db_certs import default_if_none


class CertProductIdentDocumentBase(BaseModel):
    id_doc: Annotated[int, BeforeValidator(default_if_none)] = -1
    name: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    number: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    date: Optional[datetime] = None
    created_at: Optional[datetime] = None


class CertProductIdentDocumentCreate(CertProductIdentDocumentBase):
    pass


class CertProductIdentDocumentRead(CertProductIdentDocumentBase):
    id: int
    id_identificate: int

    model_config = ConfigDict(from_attributes=True)


class CertProductIdentStandardBase(BaseModel):
    idStandard: Annotated[int, BeforeValidator(default_if_none)] = -1
    annex: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    idDictStandard: Annotated[int, BeforeValidator(default_if_none)] = -1
    new_column: Annotated[int, BeforeValidator(default_if_none)] = -1
    designation: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    name: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    section: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    addlInfo: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    idStatus: Annotated[int, BeforeValidator(default_if_none)] = -1


class CertProductIdentStandardCreate(CertProductIdentStandardBase):
    pass


class CertProductIdentStandardRead(CertProductIdentStandardBase):
    id: int
    id_identificate: int

    model_config = ConfigDict(from_attributes=True)


class CertProductIdentificationBase(BaseModel):
    idIdentification: Annotated[int, BeforeValidator(default_if_none)] = -1
    annex: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    name: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    type: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    tradeMark: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    model: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    article: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    sort: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    idOkpds: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    idTnveds: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    gtin: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    lifeTime: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    storageTime: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    description: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    amount: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    idOkei: Annotated[int, BeforeValidator(default_if_none)] = -1
    factoryNumber: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    productionDate: Optional[datetime] = None
    expiryDate: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @field_validator("idOkpds", "idTnveds", "gtin", mode="before")
    @classmethod
    def list_to_comma_string(cls, v: Any) -> str:
        if v is None or v == []:
            return "нет"
        if isinstance(v, list):
            return ",".join(str(x) for x in v)
        return v


class CertProductIdentificationCreate(CertProductIdentificationBase):
    documents: Optional[List[CertProductIdentDocumentCreate]] = Field(default_factory=list)
    standards: Optional[List[CertProductIdentStandardCreate]] = Field(default_factory=list)


class CertProductIdentificationRead(CertProductIdentificationBase):
    id: int
    id_product: int
    documents: List[CertProductIdentDocumentRead] = Field(default_factory=list)
    standards: List[CertProductIdentStandardRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CertificateProductBase(BaseModel):
    idProduct: Annotated[int, BeforeValidator(default_if_none)] = -1
    idProductOrigin: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    fullName: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    marking: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    usageScope: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    storageCondition: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    usageCondition: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    batchSize: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    batchId: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    identification: Annotated[str, BeforeValidator(default_if_none)] = "нет"
    created_at: Optional[datetime] = None


class CertificateProductCreate(CertificateProductBase):
    identifications: Optional[List[CertProductIdentificationCreate]] = Field(default_factory=list)


class CertificateProductRead(CertificateProductBase):
    id: int
    id_certificate: int
    identifications: List[CertProductIdentificationRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
