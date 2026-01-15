from pydantic import BaseModel
from typing import Optional

# Certificate_Manufacturer, Certificate_Manufacturer_Contact, Certificate_Manufacturer_Address schemas
# Define Pydantic schemas for these models here

class CertificateManufacturerBase(BaseModel):
    idLegalSubject: int
    idEgrul: Optional[int]
    idLegalSubjectType: Optional[int]
    fullName: Optional[str]
    shortName: Optional[str]
    idPerson: int
    surname: Optional[str]
    firstName: Optional[str]
    patronymic: Optional[str]
    headPosition: Optional[str]
    ogrn: Optional[str]
    ogrnAssignDate: Optional[str]
    inn: Optional[str]
    kpp: Optional[str]
    idLegalForm: Optional[int]
    regDate: Optional[str]
    regOrganName: Optional[str]
    addlRegInfo: Optional[str]
    isEecRegister: Optional[int]
    transnational: Optional[str]
    passportIssueDate: Optional[str]
    passportIssuedBy: Optional[str]
    passportNum: Optional[int]
    idPersonDoc: Optional[int]
    id_certificate: int
    date_from: Optional[str]
    date_to: Optional[str]
    created_at: Optional[str]

class CertificateManufacturerCreate(CertificateManufacturerBase):
    pass

class CertificateManufacturer(CertificateManufacturerBase):
    pass

class CertificateManufacturerContactBase(BaseModel):
    id_manufacturer: int
    # остальные поля контакта по необходимости

class CertificateManufacturerAddressBase(BaseModel):
    id_manufacturer: int
    # остальные поля адреса по необходимости
