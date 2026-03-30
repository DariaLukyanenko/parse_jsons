import os
import json

from app.certificate.schemas import CertificateCreate
from app.certificate_annex.schemas import CertificateAnnexCreate, CertificateAnnexBlankCreate
from app.certificate_authority.schemas import (CertificationAuthorityCreate, 
                                               CertAuthAddressBase, 
                                               CertAuthContactBase)
from app.certificate_applicant.schemas import (CertificateApplicantCreate,
                                               CertificateApplicantAddressBase, 
                                               CertificateApplicantContactBase)
from app.certificate_manufacturer.schemas import (CertificateManufacturerCreate, 
                                                  CertificateManufacturerAddressBase, 
                                                  CertificateManufacturerContactBase)
from app.tech_reg.schemas import CertificateTechReglamentCreate

from app.core.db import get_session
from app.crud_2 import save_certificate_to_db


def load_json(path: str) -> dict:
    """Загрузка JSON-файла."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_certificate(json_data: dict) -> CertificateCreate:
    """
    Преобразует сырой JSON в объект CertificateCreate (Pydantic),
    включая applicant, manufacturer, certificationAuthority, annexes и TR.
    """

    # ==== 1) Корневой Certificate ====
    cert_fields = {
        k: v for k, v in json_data.items()
        if k not in ("applicant", "manufacturer", "certification_authority", "annexes", "tech_reglaments")
    }
    cert = CertificateCreate(**cert_fields)

    # ==== 2) Applicant ====
    applicant_block = json_data.get("applicant")
    if applicant_block:
        applicant = CertificateApplicantCreate(
            **{k: v for k, v in applicant_block.items()
               if k not in ("addresses", "contacts")}
        )

        # Адреса
        applicant.addresses = [
            CertificateApplicantAddressBase(**addr)
            for addr in applicant_block.get("addresses", [])
        ]

        # Контакты
        applicant.contacts = [
            CertificateApplicantContactBase(**c)
            for c in applicant_block.get("contacts", [])
        ]

        cert.applicant = applicant

    # ==== 3) Manufacturer ====
    manufacturer_block = json_data.get("manufacturer")
    if manufacturer_block:
        manufacturer = CertificateManufacturerCreate(
            **{k: v for k, v in manufacturer_block.items()
               if k not in ("addresses", "contacts")}
        )

        manufacturer.addresses = [
            CertificateManufacturerAddressBase(**addr)
            for addr in manufacturer_block.get("addresses", [])
        ]
        manufacturer.contacts = [
            CertificateManufacturerContactBase(**c)
            for c in manufacturer_block.get("contacts", [])
        ]

        cert.manufacturer = manufacturer

    # ==== 4) Certification Authority ====
    authority_block = json_data.get("certification_authority")
    if authority_block:
        authority = CertificationAuthorityCreate(
            **{k: v for k, v in authority_block.items()
               if k not in ("addresses", "contacts")}
        )

        authority.addresses = [
            CertAuthAddressBase(**addr)
            for addr in authority_block.get("addresses", [])
        ]
        authority.contacts = [
            CertAuthContactBase(**c)
            for c in authority_block.get("contacts", [])
        ]

        cert.certificationAuthority = authority

    # ==== 5) Annexes ====
    annexes = []
    for annex in json_data.get("annexes", []):
        a = CertificateAnnexCreate(
            **{k: v for k, v in annex.items() if k != "blanks"}
        )
        a.blanks = [
            CertificateAnnexBlankCreate(**b)
            for b in annex.get("blanks", [])
        ]
        annexes.append(a)

    cert.annexes = annexes

    # ==== 6) Technical Reglaments ====
    techs = []
    for tr in json_data.get("tech_reglaments", []):
        techs.append(CertificateTechReglamentCreate(tech_reglaments=tr))

    cert.tech_reglaments = techs

    return cert


def process_certificate(json_path: str):
    """Полный цикл обработки JSON → Pydantic → DB через CRUD."""
    data = load_json(json_path)
    cert_pydantic = parse_certificate(data)

    with get_session() as session:
        save_certificate_to_db(cert_pydantic)


if __name__ == "__main__":
    json_path = os.path.join(
        os.path.dirname(__file__),
        "..", "certs", "10", "1003852", "2025-09-15T23-50-06.json"
    )

    process_certificate(json_path)
