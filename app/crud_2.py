from datetime import datetime, timezone
import logging
from zoneinfo import ZoneInfo
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.db import get_session
from app.certificate.models import Certificate, Certificate_has_tech_reglaments
from app.certificate_annex.models import Certificate_Annex, Certificate_AnnexBlank
from app.certificate_applicant.models import Certificate_applicant, Certificate_Applicant_Address, Certificate_Applicant_Contact
from app.certificate_manufacturer.models import Certificate_Manufacturer, Certificate_Manufacturer_Address, Certificate_Manufacturer_Contact
from app.certificate_authority.models import Certificate_Certification_Authority, Certificate_Auth_Address, Certificate_Auth_Contact

from app.schemas import (
    CertificateCreate,
    ApplicantCreate, ApplicantAddressCreate, ApplicantContactCreate,
    ManufacturerCreate, ManufacturerAddressCreate, ManufacturerContactCreate,
    CertificationAuthorityCreate, CertAuthAddressCreate, CertAuthContactCreate,
    CertificateAnnexCreate, CertificateAnnexBlankCreate,
    CertificateTechReglamentCreate,
)


DATE_MIN = datetime.strptime("01.01.2001", "%d.%m.%Y").replace(
    tzinfo=ZoneInfo("Europe/Moscow")
)
DATE_MAX = datetime.strptime("31.12.2399", "%d.%m.%Y").replace(
    tzinfo=ZoneInfo("Europe/Moscow")
)


def execute_sp_return_scalar(db: Session, sql: str, params: dict) -> int:
    """
    Выполнить произвольный T-SQL (обычно EXEC хранимой процедуры + SELECT id)
    и вернуть одно скалярное значение (id).
    """
    result = db.execute(text(sql), params)
    return result.scalar_one()


def call_certificate_change(db: Session, data: CertificateCreate) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate__change
          @id                  = @new_id OUTPUT,
          @idCertificate       = :idCertificate,
          @idCertScheme        = :idCertScheme,
          @idObjectCertType    = :idObjectCertType,
          @idCertType          = :idCertType,
          @isTs                = :isTs,
          @idProductSingleLists = :idProductSingleLists,
          @awaitForApprove     = :awaitForApprove,
          @idStatus            = :idStatus,
          @expiredInspectionControl = :expiredInspectionControl,
          @editApp             = :editApp,
          @assignRegNumber     = :assignRegNumber,
          @number              = :number,
          @certRegDate         = :certRegDate,
          @certEndDate         = :certEndDate,
          @idBlank             = :idBlank,
          @blankNumber         = :blankNumber,
          @noSanction          = :noSanction,
          @batchInspection     = :batchInspection,
          @inspectionControlPlanDate = :inspectionControlPlanDate,
          @idSigner            = :idSigner,
          @idEmployee          = :idEmployee,
          @firstName           = :firstName,
          @surname             = :surname,
          @patronymic          = :patronymic,
          @date_from           = :date_from,
          @date_to             = :date_to;

    SELECT @new_id AS id;
    """

    params = {
        "idCertificate":             data.idCertificate,
        "idCertScheme":              data.idCertScheme,
        "idObjectCertType":          data.idObjectCertType,
        "idCertType":                data.idCertType,
        "isTs":                      data.isTs,
        "idProductSingleLists":      data.idProductSingleLists,
        "awaitForApprove":           data.awaitForApprove,
        "idStatus":                  data.idStatus,
        "expiredInspectionControl":  data.expiredInspectionControl,
        "editApp":                   data.editApp,
        "assignRegNumber":           data.assignRegNumber,
        "number":                    data.number,
        "certRegDate":               data.certRegDate,
        "certEndDate":               data.certEndDate,
        "idBlank":                   data.idBlank,
        "blankNumber":               data.blankNumber,
        "noSanction":                data.noSanction,
        "batchInspection":           data.batchInspection,
        "inspectionControlPlanDate": data.inspectionControlPlanDate,
        "idSigner":                  data.idSigner,
        "idEmployee":                data.idEmployee,
        "firstName":                 data.firstName,
        "surname":                   data.surname,
        "patronymic":                data.patronymic,
        "date_from":                 DATE_MIN,
        "date_to":                   DATE_MAX,
    }

    return execute_sp_return_scalar(db, sql, params)


def create_certificate_core(db: Session, data: CertificateCreate) -> Certificate:
    """Создаём / обновляем запись в dbo.certificate через хранимую процедуру."""
    cert_id = call_certificate_change(db, data)
    cert = db.get(Certificate, cert_id)
    if cert is None:
        raise RuntimeError(f"certificate__change вернула id={cert_id}, но запись не найдена")
    return cert


def create_certificate_annexes(db: Session, cert_id: int, annexes_data):
    for annex_data in annexes_data:
        annex = Certificate_Annex(
            idAnnex=annex_data.idAnnex,
            idType=annex_data.idType,
            ord=annex_data.ord,
            pageCount=annex_data.pageCount,
            id_certificate=cert_id,
        )
        db.add(annex)
        db.flush()

        for blank in annex_data.blanks:
            db.add(
                Certificate_AnnexBlank(
                    idBlank=blank.idBlank,
                    blankNumber=blank.blankNumber,
                    id_annexes=annex.id,
                )
            )


def create_certificate_tech_reglaments(db: Session, cert_id: int, regl_list):
    for tr in regl_list:
        db.add(
            Certificate_has_tech_reglaments(
                id_certificate=cert_id,
                idTechnicalReglaments=tr.tech_reglaments,
            )
        )


def call_certificate_applicant_change(
    db: Session,
    cert_id: int,
    applicant_data,
) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_applicant__change
          @id                 = @new_id OUTPUT,
          @id_certificate     = :id_certificate,
          @idLegalSubject     = :idLegalSubject,
          @idEgrul            = :idEgrul,
          @idApplicantType    = :idApplicantType,
          @idLegalSubjectType = :idLegalSubjectType,
          @fullName           = :fullName,
          @shortName          = :shortName,
          @idPerson           = :idPerson,
          @surname            = :surname,
          @firstName          = :firstName,
          @patronymic         = :patronymic,
          @headPosition       = :headPosition,
          @ogrn               = :ogrn,
          @ogrnAssignDate     = :ogrnAssignDate,
          @inn                = :inn,
          @kpp                = :kpp,
          @idLegalForm        = :idLegalForm,
          @regDate            = :regDate,
          @regOrganName       = :regOrganName,
          @addlRegInfo        = :addlRegInfo,
          @isEecRegister      = :isEecRegister,
          @transnational      = :transnational,
          @passportIssueDate  = :passportIssueDate,
          @passportIssuedBy   = :passportIssuedBy,
          @passportNum        = :passportNum,
          @idPersonDoc        = :idPersonDoc,
          @date_from          = :date_from,
          @date_to            = :date_to;

    SELECT @new_id AS id;
    """

    params = {
        "id_certificate":     cert_id,
        "idLegalSubject":     applicant_data.idLegalSubject,
        "idEgrul":            applicant_data.idEgrul,
        "idApplicantType":    applicant_data.idApplicantType,
        "idLegalSubjectType": applicant_data.idLegalSubjectType,
        "fullName":           applicant_data.fullName,
        "shortName":          applicant_data.shortName,
        "idPerson":           applicant_data.idPerson,
        "surname":            applicant_data.surname,
        "firstName":          applicant_data.firstName,
        "patronymic":         applicant_data.patronymic,
        "headPosition":       applicant_data.headPosition,
        "ogrn":               applicant_data.ogrn,
        "ogrnAssignDate":     applicant_data.ogrnAssignDate,
        "inn":                applicant_data.inn,
        "kpp":                applicant_data.kpp,
        "idLegalForm":        applicant_data.idLegalForm,
        "regDate":            applicant_data.regDate,
        "regOrganName":       applicant_data.regOrganName,
        "addlRegInfo":        applicant_data.addlRegInfo,
        "isEecRegister":      applicant_data.isEecRegister,
        "transnational":      applicant_data.transnational,
        "passportIssueDate":  applicant_data.passportIssueDate,
        "passportIssuedBy":   applicant_data.passportIssuedBy,
        "passportNum":        applicant_data.passportNum,
        "idPersonDoc":        applicant_data.idPersonDoc,
        "date_from":          DATE_MIN,
        "date_to":            DATE_MAX,
    }

    return execute_sp_return_scalar(db, sql, params)


def call_certificate_applicant_address_change(
    db: Session,
    applicant_id: int,
    addr,
) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_applicant_address__change
          @id              = @new_id OUTPUT,
          @id_applicant    = :id_applicant,
          @idAddress       = :idAddress,
          @idCodeOksm      = :idCodeOksm,
          @oksmShort       = :oksmShort,
          @idSubject       = :idSubject,
          @idDistrict      = :idDistrict,
          @idCity          = :idCity,
          @idLocality      = :idLocality,
          @idStreet        = :idStreet,
          @idHouse         = :idHouse,
          @flat            = :flat,
          @postCode        = :postCode,
          @fullAddress     = :fullAddress,
          @gln             = :gln,
          @foreignDistrict = :foreignDistrict,
          @foreignCity     = :foreignCity,
          @foreignLocality = :foreignLocality,
          @foreignStreet   = :foreignStreet,
          @foreignHouse    = :foreignHouse,
          @uniqueAddress   = :uniqueAddress,
          @otherGln        = :otherGln,
          @glonass         = :glonass,
          @idAddrType      = :idAddrType,
          @date_from       = :date_from,
          @date_to         = :date_to;

    SELECT @new_id AS id;
    """

    params = {
        "id_applicant":    applicant_id,
        "idAddress":       addr.idAddress,
        "idCodeOksm":      addr.idCodeOksm,
        "oksmShort":       addr.oksmShort,
        "idSubject":       addr.idSubject,
        "idDistrict":      addr.idDistrict,
        "idCity":          addr.idCity,
        "idLocality":      addr.idLocality,
        "idStreet":        addr.idStreet,
        "idHouse":         addr.idHouse,
        "flat":            addr.flat,
        "postCode":        addr.postCode,
        "fullAddress":     addr.fullAddress,
        "gln":             addr.gln,
        "foreignDistrict": addr.foreignDistrict,
        "foreignCity":     addr.foreignCity,
        "foreignLocality": addr.foreignLocality,
        "foreignStreet":   addr.foreignStreet,
        "foreignHouse":    addr.foreignHouse,
        "uniqueAddress":   addr.uniqueAddress,
        "otherGln":        addr.otherGln,
        "glonass":         addr.glonass,
        "idAddrType":      addr.idAddrType,
        "date_from":       DATE_MIN,
        "date_to":         DATE_MAX,
    }

    return execute_sp_return_scalar(db, sql, params)


def call_certificate_applicant_contact_change(
    db: Session,
    applicant_id: int,
    contact,
) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_applicant_contact__change
          @id            = @new_id OUTPUT,
          @id_applicant  = :id_applicant,
          @idContact     = :idContact,
          @idContactType = :idContactType,
          @value         = :value,
          @date_from     = :date_from,
          @date_to       = :date_to;

    SELECT @new_id AS id;
    """

    params = {
        "id_applicant":  applicant_id,
        "idContact":     contact.idContact,
        "idContactType": contact.idContactType,
        "value":         contact.value,
        "date_from":     DATE_MIN,
        "date_to":       DATE_MAX,
    }

    return execute_sp_return_scalar(db, sql, params)


def create_certificate_applicant_block(
    db: Session,
    cert_id: int,
    applicant_data,
    time_now: datetime,
):
    if not applicant_data:
        return

    applicant_id = call_certificate_applicant_change(db, cert_id, applicant_data)

    for addr in applicant_data.addresses:
        call_certificate_applicant_address_change(db, applicant_id, addr)

    for c in applicant_data.contacts:
        call_certificate_applicant_contact_change(db, applicant_id, c)


def call_certificate_manufacturer_change(db: Session, cert_id: int, manufacturer_data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_manufacturer__change
          @id                 = @new_id OUTPUT,
          @id_certificate     = :id_certificate,
          @idLegalSubject     = :idLegalSubject,
          @idEgrul            = :idEgrul,
          @idLegalSubjectType = :idLegalSubjectType,
          @fullName           = :fullName,
          @shortName          = :shortName,
          @idPerson           = :idPerson,
          @surname            = :surname,
          @firstName          = :firstName,
          @patronymic         = :patronymic,
          @headPosition       = :headPosition,
          @ogrn               = :ogrn,
          @ogrnAssignDate     = :ogrnAssignDate,
          @inn                = :inn,
          @kpp                = :kpp,
          @idLegalForm        = :idLegalForm,
          @regDate            = :regDate,
          @regOrganName       = :regOrganName,
          @addlRegInfo        = :addlRegInfo,
          @isEecRegister      = :isEecRegister,
          @transnational      = :transnational,
          @passportIssueDate  = :passportIssueDate,
          @passportIssuedBy   = :passportIssuedBy,
          @passportNum        = :passportNum,
          @idPersonDoc        = :idPersonDoc,
          @date_from          = :date_from,
          @date_to            = :date_to,
          @created_at         = :created_at;

    SELECT @new_id AS id;
    """
    params = {
        "id_certificate":     cert_id,
        "idLegalSubject":     manufacturer_data.idLegalSubject,
        "idEgrul":            manufacturer_data.idEgrul,
        "idLegalSubjectType": manufacturer_data.idLegalSubjectType,
        "fullName":           manufacturer_data.fullName,
        "shortName":          manufacturer_data.shortName,
        "idPerson":           manufacturer_data.idPerson,
        "surname":            manufacturer_data.surname,
        "firstName":          manufacturer_data.firstName,
        "patronymic":         manufacturer_data.patronymic,
        "headPosition":       manufacturer_data.headPosition,
        "ogrn":               manufacturer_data.ogrn,
        "ogrnAssignDate":     manufacturer_data.ogrnAssignDate,
        "inn":                manufacturer_data.inn,
        "kpp":                manufacturer_data.kpp,
        "idLegalForm":        manufacturer_data.idLegalForm,
        "regDate":            manufacturer_data.regDate,
        "regOrganName":       manufacturer_data.regOrganName,
        "addlRegInfo":        manufacturer_data.addlRegInfo,
        "isEecRegister":      manufacturer_data.isEecRegister,
        "transnational":      manufacturer_data.transnational,
        "passportIssueDate":  manufacturer_data.passportIssueDate,
        "passportIssuedBy":   manufacturer_data.passportIssuedBy,
        "passportNum":        manufacturer_data.passportNum,
        "idPersonDoc":        manufacturer_data.idPersonDoc,
        "date_from":          DATE_MIN,
        "date_to":            DATE_MAX,
        "created_at":         datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_manufacturer_address_change(db: Session, manufacturer_id: int, addr) -> int:
    sql = """
    DECLARE @new_id INT;
    EXEC dbo.certificate_manufacturer_address__change
          @id              = @new_id OUTPUT,
          @id_manufacturer = :id_manufacturer,
          @idAddress       = :idAddress,
          @idCodeOksm      = :idCodeOksm,
          @oksmShort       = :oksmShort,
          @idSubject       = :idSubject,
          @idDistrict      = :idDistrict,
          @idCity          = :idCity,
          @idLocality      = :idLocality,
          @idStreet        = :idStreet,
          @idHouse         = :idHouse,
          @flat            = :flat,
          @postCode        = :postCode,
          @fullAddress     = :fullAddress,
          @gln             = :gln,
          @foreignDistrict = :foreignDistrict,
          @foreignCity     = :foreignCity,
          @foreignLocality = :foreignLocality,
          @foreignStreet   = :foreignStreet,
          @foreignHouse    = :foreignHouse,
          @uniqueAddress   = :uniqueAddress,
          @otherGln        = :otherGln,
          @glonass         = :glonass,
          @idAddrType      = :idAddrType,
          @date_from       = :date_from,
          @date_to         = :date_to,
          @created_at      = :created_at;
    SELECT @new_id AS id;
    """
    params = {
        "id_manufacturer": manufacturer_id,
        "idAddress":       addr.idAddress,
        "idCodeOksm":      addr.idCodeOksm,
        "oksmShort":       addr.oksmShort,
        "idSubject":       addr.idSubject,
        "idDistrict":      addr.idDistrict,
        "idCity":          addr.idCity,
        "idLocality":      addr.idLocality,
        "idStreet":        addr.idStreet,
        "idHouse":         addr.idHouse,
        "flat":            addr.flat,
        "postCode":        addr.postCode,
        "fullAddress":     addr.fullAddress,
        "gln":             addr.gln,
        "foreignDistrict": addr.foreignDistrict,
        "foreignCity":     addr.foreignCity,
        "foreignLocality": addr.foreignLocality,
        "foreignStreet":   addr.foreignStreet,
        "foreignHouse":    addr.foreignHouse,
        "uniqueAddress":   addr.uniqueAddress,
        "otherGln":        addr.otherGln,
        "glonass":         addr.glonass,
        "idAddrType":      addr.idAddrType,
        "date_from":       DATE_MIN,
        "date_to":         DATE_MAX,
        "created_at":      datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_manufacturer_contact_change(db: Session, manufacturer_id: int, contact) -> int:
    sql = """
    DECLARE @new_id INT;
    EXEC dbo.certificate_manufacturer_contact__change
          @id              = @new_id OUTPUT,
          @id_manufacturer = :id_manufacturer,
          @idContact       = :idContact,
          @idContactType   = :idContactType,
          @value           = :value,
          @date_from       = :date_from,
          @date_to         = :date_to,
          @created_at      = :created_at;
    SELECT @new_id AS id;
    """
    params = {
        "id_manufacturer": manufacturer_id,
        "idContact":       contact.idContact,
        "idContactType":   contact.idContactType,
        "value":           contact.value,
        "date_from":       DATE_MIN,
        "date_to":         DATE_MAX,
        "created_at":      datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def create_certificate_manufacturer_block(db: Session, cert_id: int, manufacturer_data, time_now: datetime):
    if not manufacturer_data:
        return
    manufacturer_id = call_certificate_manufacturer_change(db, cert_id, manufacturer_data)
    for addr in manufacturer_data.addresses:
        call_certificate_manufacturer_address_change(db, manufacturer_id, addr)
    for c in manufacturer_data.contacts:
        call_certificate_manufacturer_contact_change(db, manufacturer_id, c)


def call_certificate_auth_change(db: Session, cert_id: int, auth_data) -> int:
    sql = """
    DECLARE @new_id INT;
    EXEC dbo.certificate_certification_authority__change
          @id                  = @new_id OUTPUT,
          @certificate_id      = :certificate_id,
          @idCertificationAuthority = :idCertificationAuthority,
          @fullName            = :fullName,
          @accredOrgName       = :accredOrgName,
          @attestatRegNumber   = :attestatRegNumber,
          @attestatRegDate     = :attestatRegDate,
          @attestatEndDate     = :attestatEndDate,
          @idRal               = :idRal,
          @ogrn                = :ogrn,
          @idPerson            = :idPerson,
          @firstName           = :firstName,
          @surname             = :surname,
          @patronymic          = :patronymic,
          @prevAttestatRegNumber = :prevAttestatRegNumber,
          @prevIdRal           = :prevIdRal,
          @date_from           = :date_from,
          @date_to             = :date_to,
          @created_at          = :created_at;
    SELECT @new_id AS id;
    """
    params = {
        "certificate_id":           cert_id,
        "idCertificationAuthority": auth_data.idCertificationAuthority,
        "fullName":                 auth_data.fullName,
        "accredOrgName":            auth_data.accredOrgName,
        "attestatRegNumber":        auth_data.attestatRegNumber,
        "attestatRegDate":          auth_data.attestatRegDate,
        "attestatEndDate":          auth_data.attestatEndDate,
        "idRal":                    auth_data.idRal,
        "ogrn":                     auth_data.ogrn,
        "idPerson":                 auth_data.idPerson,
        "firstName":                auth_data.firstName,
        "surname":                  auth_data.surname,
        "patronymic":               auth_data.patronymic,
        "prevAttestatRegNumber":    auth_data.prevAttestatRegNumber,
        "prevIdRal":                auth_data.prevIdRal,
        "date_from":                DATE_MIN,
        "date_to":                  DATE_MAX,
        "created_at":               datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_auth_address_change(db: Session, auth_id: int, addr) -> int:
    sql = """
    DECLARE @new_id INT;
    EXEC dbo.certificate_certification_authority_address__change
          @id         = @new_id OUTPUT,
          @id_auth    = :id_auth,
          @idAddress  = :idAddress,
          @idCodeOksm = :idCodeOksm,
          @oksmShort  = :oksmShort,
          @idSubject  = :idSubject,
          @idDistrict = :idDistrict,
          @idCity     = :idCity,
          @idLocality = :idLocality,
          @idStreet   = :idStreet,
          @idHouse    = :idHouse,
          @flat       = :flat,
          @postCode   = :postCode,
          @fullAddress = :fullAddress,
          @gln        = :gln,
          @foreignDistrict = :foreignDistrict,
          @foreignCity    = :foreignCity,
          @foreignLocality = :foreignLocality,
          @foreignStreet  = :foreignStreet,
          @foreignHouse   = :foreignHouse,
          @uniqueAddress  = :uniqueAddress,
          @otherGln       = :otherGln,
          @glonass        = :glonass,
          @idAddrType     = :idAddrType,
          @date_from      = :date_from,
          @date_to        = :date_to,
          @created_at     = :created_at;
    SELECT @new_id AS id;
    """
    params = {
        "id_auth":      auth_id,
        "idAddress":    addr.idAddress,
        "idCodeOksm":   addr.idCodeOksm,
        "oksmShort":    addr.oksmShort,
        "idSubject":    addr.idSubject,
        "idDistrict":   addr.idDistrict,
        "idCity":       addr.idCity,
        "idLocality":   addr.idLocality,
        "idStreet":     addr.idStreet,
        "idHouse":      addr.idHouse,
        "flat":         addr.flat,
        "postCode":     addr.postCode,
        "fullAddress":  addr.fullAddress,
        "gln":          addr.gln,
        "foreignDistrict": addr.foreignDistrict,
        "foreignCity":     addr.foreignCity,
        "foreignLocality": addr.foreignLocality,
        "foreignStreet":   addr.foreignStreet,
        "foreignHouse":    addr.foreignHouse,
        "uniqueAddress":   addr.uniqueAddress,
        "otherGln":        addr.otherGln,
        "glonass":         addr.glonass,
        "idAddrType":      addr.idAddrType,
        "date_from":       DATE_MIN,
        "date_to":         DATE_MAX,
        "created_at":      datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_auth_contact_change(db: Session, auth_id: int, contact) -> int:
    sql = """
    DECLARE @new_id INT;
    EXEC dbo.certificate_certification_authority_contact__change
          @id         = @new_id OUTPUT,
          @id_auth    = :id_auth,
          @idContact  = :idContact,
          @idContactType = :idContactType,
          @value      = :value,
          @date_from  = :date_from,
          @date_to    = :date_to,
          @created_at = :created_at;
    SELECT @new_id AS id;
    """
    params = {
        "id_auth":      auth_id,
        "idContact":    contact.idContact,
        "idContactType":contact.idContactType,
        "value":        contact.value,
        "date_from":    DATE_MIN,
        "date_to":      DATE_MAX,
        "created_at":   datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def create_certificate_auth_block(db: Session, cert_id: int, auth_data, time_now: datetime):
    if not auth_data:
        return
    auth_id = call_certificate_auth_change(db, cert_id, auth_data)
    for addr in auth_data.addresses:
        call_certificate_auth_address_change(db, auth_id, addr)
    for c in auth_data.contacts:
        call_certificate_auth_contact_change(db, auth_id, c)


def save_certificate_to_db(data):
    with get_session() as session:
        create_certificate(session, data)
        

def create_certificate(db: Session, data: CertificateCreate) -> Certificate | None:
    time_now = datetime.now(ZoneInfo("Europe/Moscow"))
    try:
        cert = create_certificate_core(db, data)
        cert_id = cert.id
        create_certificate_annexes(db, cert_id, data.annexes)
        create_certificate_tech_reglaments(db, cert_id, data.idTechnicalReglaments)
        create_certificate_applicant_block(db, cert_id, data.applicant, time_now)
        create_certificate_manufacturer_block(db, cert_id, data.manufacturer, time_now)
        create_certificate_auth_block(db, cert_id, data.certificationAuthority, time_now)
        db.commit()
        db.refresh(cert)
        return cert
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[SQLAlchemyError] Ошибка при создании сертификата ID={data.idCertificate}: {e}")
    except Exception as e:
        db.rollback()
        logging.error(f"[Exception] Неизвестная ошибка при создании сертификата ID={data.idCertificate}: {e}")
    return None