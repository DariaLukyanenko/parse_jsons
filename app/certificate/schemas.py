from datetime import date, datetime
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator
from typing import Annotated, Optional

from pyparsing import Any, List

from app.schemas import (ApplicantCreate, 
                         ApplicantRead, 
                         CertificateAnnexCreate, 
                         CertificateAnnexRead, 
                         CertificateTechReglamentCreate, 
                         CertificateTechReglamentRead, 
                         CertificationAuthorityCreate, 
                         CertificationAuthorityRead, 
                         Manufacturer, ManufacturerCreate, 
                         default_if_none,
                         CertificateAnnexCreate, 
                         CertificateAnnexRead, 
                         CertificateTechReglamentCreate, 
                         CertificateTechReglamentRead, 
                         CertificationAuthorityCreate, 
                         CertificationAuthorityRead, 
                         Manufacturer, 
                         ManufacturerCreate)

# Certificate schemas
# Define Pydantic schemas for Certificate here

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
    
    
    @field_validator('batchInspection', mode='before')
    @classmethod
    def validate_batch_inspection(cls, value: Any) -> str:
        if value is None or value is False:
            return 'нет'
        return str(value)
    
    
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
    


class Certificate(CertificateBase):
    """Полная схема сертификата с вложенными объектами"""
    id: int
    annexes: List[CertificateAnnexRead] = []
    applicants: List[ApplicantRead] = []
    manufacturers: List[Manufacturer] = []
    certification_authorities: List[CertificationAuthorityRead] = []
    tech_reglaments: List[CertificateTechReglamentRead] = []
    
    model_config = ConfigDict(from_attributes=True)