from pydantic import BaseModel
from typing import Optional

# Certificate_Certification_Authority, Certificate_Auth_Contact, Certificate_Auth_Address schemas
# Define Pydantic schemas for these models here

class CertificationAuthorityBase(BaseModel):
    idCertificationAuthority: int
    fullName: Optional[str]
    accredOrgName: Optional[str]
    attestatRegNumber: Optional[str]
    attestatRegDate: Optional[str]
    attestatEndDate: Optional[str]
    idRal: int
    ogrn: Optional[str]
    idPerson: Optional[int]
    firstName: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    prevAttestatRegNumber: Optional[str]
    prevIdRal: Optional[int]
    date_from: Optional[str]
    date_to: Optional[str]
    created_at: Optional[str]
    certificate_id: int

class CertificationAuthorityCreate(CertificationAuthorityBase):
    pass

class CertificationAuthority(CertificationAuthorityBase):
    pass

class CertAuthContactBase(BaseModel):
    id_auth: int
    # остальные поля контакта по необходимости

class CertAuthAddressBase(BaseModel):
    id_auth: int
    # остальные поля адреса по необходимости
