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
from app.certificate_product.schemas import (
    CertificateProductCreate,
    CertProductIdentificationCreate,
    CertProductIdentDocumentCreate,
    CertProductIdentStandardCreate,
)
from app.certificate_testing_labs.schemas import (
    CertificateTestingLabCreate,
    CertTestingLabDocConfirmCustomCreate,
    CertTestingLabDocConfirmCustomInfoCreate,
    CertTestingLabProtocolCreate,
)

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

    # ==== 7) Products ====
    products = []
    for prod_block in json_data.get("products", []):
        prod = CertificateProductCreate(
            **{k: v for k, v in prod_block.items() if k != "identifications"}
        )
        identifications = []
        for ident_block in prod_block.get("identifications", []):
            ident = CertProductIdentificationCreate(
                **{k: v for k, v in ident_block.items()
                   if k not in ("documents", "standards")}
            )
            ident.documents = [
                CertProductIdentDocumentCreate(**doc)
                for doc in ident_block.get("documents", [])
            ]
            ident.standards = [
                CertProductIdentStandardCreate(**std)
                for std in ident_block.get("standards", [])
            ]
            identifications.append(ident)
        prod.identifications = identifications
        products.append(prod)

    cert.products = products

    # ==== 8) Testing Labs ====
    testing_labs = []
    for lab_block in json_data.get("testing_labs", []):
        lab = CertificateTestingLabCreate(
            **{k: v for k, v in lab_block.items()
               if k not in ("doc_confirm_customs", "protocols")}
        )
        doc_confirm_customs = []
        for dcc_block in lab_block.get("doc_confirm_customs", []):
            dcc = CertTestingLabDocConfirmCustomCreate(
                **{k: v for k, v in dcc_block.items() if k != "custom_infos"}
            )
            dcc.custom_infos = [
                CertTestingLabDocConfirmCustomInfoCreate(**ci)
                for ci in dcc_block.get("custom_infos", [])
            ]
            doc_confirm_customs.append(dcc)
        lab.doc_confirm_customs = doc_confirm_customs
        lab.protocols = [
            CertTestingLabProtocolCreate(**p)
            for p in lab_block.get("protocols", [])
        ]
        testing_labs.append(lab)

    cert.testing_labs = testing_labs

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
