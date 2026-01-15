from pydantic import BaseModel
from typing import Optional

# Certificate_applicant, Certificate_Applicant_Address, Certificate_Applicant_Contact schemas
# Define Pydantic schemas for these models here

class CertificateApplicantBase(BaseModel):
    idLegalSubject: int
    idEgrul: Optional[int]
    idApplicantType: Optional[int]
    idLegalSubjectType: Optional[int]
    fullName: Optional[str]
    shortName: Optional[str]
    idPerson: Optional[int]
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
    passportNum: Optional[str]
    idPersonDoc: Optional[int]
    date_from: Optional[str]
    date_to: Optional[str]
    created_at: Optional[str]
    id_certificate: int

class CertificateApplicantCreate(CertificateApplicantBase):
    pass

class CertificateApplicant(CertificateApplicantBase):
    pass

class CertificateApplicantAddressBase(BaseModel):
    id_applicant: int
    # остальные поля адреса по необходимости

class CertificateApplicantContactBase(BaseModel):
    id_applicant: int
    # остальные поля контакта по необходимости
