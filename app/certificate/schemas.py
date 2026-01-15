from pydantic import BaseModel
from typing import Optional

# Certificate schemas
# Define Pydantic schemas for Certificate here

class CertificateBase(BaseModel):
    idCertificate: int
    idCertScheme: Optional[int]
    idObjectCertType: Optional[int]
    idCertType: int
    isTs: Optional[int]
    idProductSingleLists_str: Optional[str]
    awaitForApprove: Optional[int]
    idStatus: str
    expiredInspectionControl: Optional[int]
    editApp: Optional[int]
    assignRegNumber: Optional[int]
    number: str
    certRegDate: Optional[str]
    certEndDate: Optional[str]
    idBlank: int
    blankNumber: Optional[str]
    noSanction: Optional[int]
    batchInspection: Optional[str]
    inspectionControlPlanDate: Optional[str]
    idSigner: Optional[int]
    idEmployee: Optional[int]
    firstName: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]
    created_at: Optional[str]

class CertificateCreate(CertificateBase):
    pass

class Certificate(CertificateBase):
    pass
