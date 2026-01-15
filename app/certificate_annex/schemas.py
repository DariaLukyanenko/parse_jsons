from pydantic import BaseModel
from typing import Optional

class CertificateAnnexBase(BaseModel):
    idAnnex: int
    idType: Optional[int]
    ord: Optional[int]
    pageCount: Optional[int]
    id_certificate: int

class CertificateAnnexCreate(CertificateAnnexBase):
    pass

class CertificateAnnex(CertificateAnnexBase):
    pass

class CertificateAnnexBlankBase(BaseModel):
    idBlank: int
    blankNumber: Optional[str]
    id_annexes: int

class CertificateAnnexBlankCreate(CertificateAnnexBlankBase):
    pass

class CertificateAnnexBlank(CertificateAnnexBlankBase):
    pass
