import os
import json
from sqlalchemy.orm import Session
from app.core.db import get_session
from app.certificate.schemas import CertificateCreate
from app.certificate.models import Certificate
from app.certificate_applicant.schemas import CertificateApplicantCreate
from app.certificate_applicant.models import Certificate_applicant, Certificate_Applicant_Address, Certificate_Applicant_Contact
from app.certificate_annex.schemas import CertificateAnnexCreate, CertificateAnnexBlankCreate
from app.certificate_annex.models import Certificate_Annex, Certificate_AnnexBlank
from app.certificate_manufacturer.schemas import CertificateManufacturerCreate
from app.certificate_manufacturer.models import Certificate_Manufacturer, Certificate_Manufacturer_Address, Certificate_Manufacturer_Contact
from app.certificate_certification_authority.schemas import CertificationAuthorityCreate
from app.certificate_certification_authority.models import Certificate_Certification_Authority, Certificate_Auth_Address, Certificate_Auth_Contact

def parse_and_save_certificate(json_path: str, session: Session):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Валидация и создание Certificate
    cert_schema = CertificateCreate(**{k: v for k, v in data.items() if k not in ("applicant", "annexes", "manufacturer", "certification_authority")})
    cert = Certificate(**cert_schema.dict())
    session.add(cert)
    session.flush()  # Получить cert.id
    # Applicant
    if "applicant" in data and data["applicant"]:
        applicant_schema = CertificateApplicantCreate(**{k: v for k, v in data["applicant"].items() if k not in ("addresses", "contacts")}, id_certificate=cert.id)
        applicant = Certificate_applicant(**applicant_schema.dict())
        session.add(applicant)
        session.flush()
        for addr in data["applicant"].get("addresses", []):
            address = Certificate_Applicant_Address(id_applicant=applicant.id, **{k: v for k, v in addr.items() if k != "id_applicant"})
            session.add(address)
        for contact in data["applicant"].get("contacts", []):
            contact_obj = Certificate_Applicant_Contact(id_applicant=applicant.id, **{k: v for k, v in contact.items() if k != "id_applicant"})
            session.add(contact_obj)
    # Manufacturer
    if "manufacturer" in data and data["manufacturer"]:
        manufacturer_schema = CertificateManufacturerCreate(**{k: v for k, v in data["manufacturer"].items() if k not in ("addresses", "contacts")}, id_certificate=cert.id)
        manufacturer = Certificate_Manufacturer(**manufacturer_schema.dict())
        session.add(manufacturer)
        session.flush()
        for addr in data["manufacturer"].get("addresses", []):
            address = Certificate_Manufacturer_Address(id_manufacturer=manufacturer.id, **{k: v for k, v in addr.items() if k != "id_manufacturer"})
            session.add(address)
        for contact in data["manufacturer"].get("contacts", []):
            contact_obj = Certificate_Manufacturer_Contact(id_manufacturer=manufacturer.id, **{k: v for k, v in contact.items() if k != "id_manufacturer"})
            session.add(contact_obj)
    # Certification Authority
    if "certification_authority" in data and data["certification_authority"]:
        authority_schema = CertificationAuthorityCreate(**{k: v for k, v in data["certification_authority"].items() if k not in ("addresses", "contacts")}, certificate_id=cert.id)
        authority = Certificate_Certification_Authority(**authority_schema.dict())
        session.add(authority)
        session.flush()
        for addr in data["certification_authority"].get("addresses", []):
            address = Certificate_Auth_Address(id_auth=authority.id, **{k: v for k, v in addr.items() if k != "id_auth"})
            session.add(address)
        for contact in data["certification_authority"].get("contacts", []):
            contact_obj = Certificate_Auth_Contact(id_auth=authority.id, **{k: v for k, v in contact.items() if k != "id_auth"})
            session.add(contact_obj)
    # Annexes
    for annex in data.get("annexes", []):
        annex_schema = CertificateAnnexCreate(**{k: v for k, v in annex.items() if k != "blanks"}, id_certificate=cert.id)
        annex_obj = Certificate_Annex(**annex_schema.dict())
        session.add(annex_obj)
        session.flush()
        for blank in annex.get("blanks", []):
            blank_schema = CertificateAnnexBlankCreate(**blank, id_annexes=annex_obj.id)
            blank_obj = Certificate_AnnexBlank(**blank_schema.dict())
            session.add(blank_obj)
    session.commit()
    print(f"Certificate {cert.idCertificate} and related data saved.")

if __name__ == "__main__":
    # Пример использования
    session = next(get_session())
    json_path = os.path.join(os.path.dirname(__file__), '..', 'certs', '10', '1003852', '2025-09-15T23-50-06.json')
    parse_and_save_certificate(json_path, session)
