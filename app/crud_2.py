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


# -------------------------
# Certificate Product
# -------------------------

def call_certificate_product_change(db: Session, cert_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_product__change
          @id              = @new_id OUTPUT,
          @id_certificate  = :id_certificate,
          @idProduct       = :idProduct,
          @idProductOrigin = :idProductOrigin,
          @fullName        = :fullName,
          @marking         = :marking,
          @usageScope      = :usageScope,
          @storageCondition = :storageCondition,
          @usageCondition  = :usageCondition,
          @batchSize       = :batchSize,
          @batchId         = :batchId,
          @identification  = :identification,
          @created_at      = :created_at;

    SELECT @new_id AS id;
    """
    params = {
        "id_certificate":   cert_id,
        "idProduct":        data.idProduct,
        "idProductOrigin":  data.idProductOrigin,
        "fullName":         data.fullName,
        "marking":          data.marking,
        "usageScope":       data.usageScope,
        "storageCondition": data.storageCondition,
        "usageCondition":   data.usageCondition,
        "batchSize":        data.batchSize,
        "batchId":          data.batchId,
        "identification":   data.identification,
        "created_at":       datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_product_identification_change(db: Session, prod_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_product_identification__change
          @id               = @new_id OUTPUT,
          @id_product       = :id_product,
          @idIdentification = :idIdentification,
          @annex            = :annex,
          @name             = :name,
          @type             = :type,
          @tradeMark        = :tradeMark,
          @model            = :model,
          @article          = :article,
          @sort             = :sort,
          @idOkpds          = :idOkpds,
          @idTnveds         = :idTnveds,
          @gtin             = :gtin,
          @lifeTime         = :lifeTime,
          @storageTime      = :storageTime,
          @description      = :description,
          @amount           = :amount,
          @idOkei           = :idOkei,
          @factoryNumber    = :factoryNumber,
          @productionDate   = :productionDate,
          @expiryDate       = :expiryDate,
          @created_at       = :created_at;

    SELECT @new_id AS id;
    """
    params = {
        "id_product":       prod_id,
        "idIdentification": data.idIdentification,
        "annex":            data.annex,
        "name":             data.name,
        "type":             data.type,
        "tradeMark":        data.tradeMark,
        "model":            data.model,
        "article":          data.article,
        "sort":             data.sort,
        "idOkpds":          data.idOkpds,
        "idTnveds":         data.idTnveds,
        "gtin":             data.gtin,
        "lifeTime":         data.lifeTime,
        "storageTime":      data.storageTime,
        "description":      data.description,
        "amount":           data.amount,
        "idOkei":           data.idOkei,
        "factoryNumber":    data.factoryNumber,
        "productionDate":   data.productionDate,
        "expiryDate":       data.expiryDate,
        "created_at":       datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_product_identification_document_change(db: Session, ident_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_product_identification_document__change
          @id              = @new_id OUTPUT,
          @id_identificate = :id_identificate,
          @id_doc          = :id_doc,
          @name            = :name,
          @number          = :number,
          @date            = :date,
          @created_at      = :created_at;

    SELECT @new_id AS id;
    """
    params = {
        "id_identificate": ident_id,
        "id_doc":          data.id_doc,
        "name":            data.name,
        "number":          data.number,
        "date":            data.date,
        "created_at":      datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_product_identification_standard_change(db: Session, ident_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_product_identification_standard__change
          @id              = @new_id OUTPUT,
          @id_identificate = :id_identificate,
          @idStandard      = :idStandard,
          @annex           = :annex,
          @idDictStandard  = :idDictStandard,
          @new_column      = :new_column,
          @designation     = :designation,
          @name            = :name,
          @section         = :section,
          @addlInfo        = :addlInfo,
          @idStatus        = :idStatus;

    SELECT @new_id AS id;
    """
    params = {
        "id_identificate": ident_id,
        "idStandard":      data.idStandard,
        "annex":           data.annex,
        "idDictStandard":  data.idDictStandard,
        "new_column":      data.new_column,
        "designation":     data.designation,
        "name":            data.name,
        "section":         data.section,
        "addlInfo":        data.addlInfo,
        "idStatus":        data.idStatus,
    }
    return execute_sp_return_scalar(db, sql, params)


def create_certificate_products(db: Session, cert_id: int, products_data):
    for prod_data in products_data or []:
        prod_id = call_certificate_product_change(db, cert_id, prod_data)

        for ident_data in prod_data.identifications or []:
            ident_id = call_certificate_product_identification_change(db, prod_id, ident_data)

            for doc_data in ident_data.documents or []:
                call_certificate_product_identification_document_change(db, ident_id, doc_data)

            for std_data in ident_data.standards or []:
                call_certificate_product_identification_standard_change(db, ident_id, std_data)


# -------------------------
# Certificate Testing Labs
# -------------------------

def call_certificate_testing_lab_change(db: Session, cert_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_testing_labs__change
          @id                       = @new_id OUTPUT,
          @certificate_id           = :certificate_id,
          @idTestingLab             = :idTestingLab,
          @annex                    = :annex,
          @idRal                    = :idRal,
          @regNumber                = :regNumber,
          @fullName                 = :fullName,
          @beginDate                = :beginDate,
          @endDate                  = :endDate,
          @basis                    = :basis,
          @accredEec                = :accredEec,
          @idAccredPlace            = :idAccredPlace,
          @importedForResearchTesting = :importedForResearchTesting,
          @actNumber                = :actNumber,
          @actDate                  = :actDate,
          @actIdentificationNumber  = :actIdentificationNumber,
          @actIdentificationDate    = :actIdentificationDate,
          @created_at               = :created_at;

    SELECT @new_id AS id;
    """
    params = {
        "certificate_id":             cert_id,
        "idTestingLab":               data.idTestingLab,
        "annex":                      data.annex,
        "idRal":                      data.idRal,
        "regNumber":                  data.regNumber,
        "fullName":                   data.fullName,
        "beginDate":                  data.beginDate,
        "endDate":                    data.endDate,
        "basis":                      data.basis,
        "accredEec":                  data.accredEec,
        "idAccredPlace":              data.idAccredPlace,
        "importedForResearchTesting": data.importedForResearchTesting,
        "actNumber":                  data.actNumber,
        "actDate":                    data.actDate,
        "actIdentificationNumber":    data.actIdentificationNumber,
        "actIdentificationDate":      data.actIdentificationDate,
        "created_at":                 datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_testing_lab_doc_confirm_custom_change(db: Session, lab_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_testing_labs_docconfirmcustom__change
          @id                                  = @new_id OUTPUT,
          @id_test_lab                         = :id_test_lab,
          @idDocConfirmCustom                  = :idDocConfirmCustom,
          @idDocConfirmCustomType              = :idDocConfirmCustomType,
          @otherDocs                           = :otherDocs,
          @reasonNonRegistrCustomsDeclaration  = :reasonNonRegistrCustomsDeclaration,
          @created_at                          = :created_at;

    SELECT @new_id AS id;
    """
    params = {
        "id_test_lab":                        lab_id,
        "idDocConfirmCustom":                 data.idDocConfirmCustom,
        "idDocConfirmCustomType":             data.idDocConfirmCustomType,
        "otherDocs":                          data.otherDocs,
        "reasonNonRegistrCustomsDeclaration": data.reasonNonRegistrCustomsDeclaration,
        "created_at":                         datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_testing_lab_doc_confirm_custom_info_change(db: Session, dcc_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_testing_labs_docconfirmcustom_custominfo__change
          @id                    = @new_id OUTPUT,
          @id_doc_confirm_custom = :id_doc_confirm_custom,
          @idCustomInfo          = :idCustomInfo,
          @customDeclNumber      = :customDeclNumber;

    SELECT @new_id AS id;
    """
    params = {
        "id_doc_confirm_custom": dcc_id,
        "idCustomInfo":          data.idCustomInfo,
        "customDeclNumber":      data.customDeclNumber,
    }
    return execute_sp_return_scalar(db, sql, params)


def call_certificate_testing_lab_protocol_change(db: Session, lab_id: int, data) -> int:
    sql = """
    DECLARE @new_id INT;

    EXEC dbo.certificate_testing_labs_protocols__change
          @id                = @new_id OUTPUT,
          @id_test_lab       = :id_test_lab,
          @idProtocol        = :idProtocol,
          @idProtocolRpi     = :idProtocolRpi,
          @number            = :number,
          @date              = :date,
          @standards         = :standards,
          @isProtocolInvalid = :isProtocolInvalid,
          @created_at        = :created_at;

    SELECT @new_id AS id;
    """
    params = {
        "id_test_lab":       lab_id,
        "idProtocol":        data.idProtocol,
        "idProtocolRpi":     data.idProtocolRpi,
        "number":            data.number,
        "date":              data.date,
        "standards":         data.standards,
        "isProtocolInvalid": data.isProtocolInvalid,
        "created_at":        datetime.now(ZoneInfo("Europe/Moscow")),
    }
    return execute_sp_return_scalar(db, sql, params)


def create_certificate_testing_labs(db: Session, cert_id: int, testing_labs_data):
    for lab_data in testing_labs_data or []:
        lab_id = call_certificate_testing_lab_change(db, cert_id, lab_data)

        for dcc_data in lab_data.doc_confirm_customs or []:
            dcc_id = call_certificate_testing_lab_doc_confirm_custom_change(db, lab_id, dcc_data)

            for ci_data in dcc_data.custom_infos or []:
                call_certificate_testing_lab_doc_confirm_custom_info_change(db, dcc_id, ci_data)

        for proto_data in lab_data.protocols or []:
            call_certificate_testing_lab_protocol_change(db, lab_id, proto_data)


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
        create_certificate_products(db, cert_id, data.products)
        create_certificate_testing_labs(db, cert_id, data.testing_labs)
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