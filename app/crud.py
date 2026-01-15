# crud.py
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from app.certificate.models import Certificate
from app.certificate_annex.models import Certificate_Annex, Certificate_AnnexBlank
from app.certificate_applicant.models import Certificate_applicant, Certificate_Applicant_Address, Certificate_Applicant_Contact
from app.certificate.models import Certificate_has_tech_reglaments
from app.core.db import get_session


DATE_MIN = datetime.strptime("01.01.2001", "%d.%m.%Y").replace(tzinfo=timezone.utc)
DATE_MAX = datetime.strptime("31.12.2399", "%d.%m.%Y").replace(tzinfo=timezone.utc)


def get_last_certificate_version(session, idCertificate):
    return (
        session.query(Certificate)
        .filter(Certificate.idCertificate == idCertificate)
        .order_by(Certificate.date_from.desc())
        .first()
    )

####тут по id делать
def get_last_applicant_version(session, cert_id):
    return (
        session.query(Certificate_applicant)
        .filter(Certificate_applicant.id_certificate == cert_id)
        .order_by(Certificate_applicant.date_from.desc())
        .first()
    )


def update_old_certificate(cert: Certificate, time_now, session: Session) -> Certificate:
    cert.date_to = time_now
    session.add(cert)
    session.flush()


def update_old_applicant(applicant, time_now, session):
    applicant.date_to = time_now
    session.add(applicant)
    session.flush()


def create_applicant(cert_obj, app_data, time_now, is_first_version, session):
    # 1) Нужно достать последнюю версию applicant
    existing = get_last_applicant_version(session, cert_obj.id)

    # 2) Если applicant уже есть → закрываем старую запись
    if existing:
        update_old_applicant(existing, time_now, session)

    # 3) Создаём новую версию applicant
    appl_data = app_data.model_dump(exclude={
        "addresses",
        "contacts",
        "date_from",
        "date_to",
        "created_at",
    })

    applicant = Certificate_applicant(
        **appl_data,
        created_at=time_now,
        date_from=DATE_MIN if is_first_version else time_now,
        date_to=DATE_MAX,
        id_certificate=cert_obj.id
    )

    session.add(applicant)
    session.flush()  # получаем applicant.id

    # --- адреса ---
    for addr in app_data.addresses or []:
        addr_data = addr.model_dump(
            exclude={
            "date_from",
            "date_to",
            "created_at",
        }
        )
        session.add(Certificate_Applicant_Address(
            **addr_data,
            created_at=time_now,
            date_from=DATE_MIN if is_first_version else time_now,
            date_to=DATE_MAX,
            id_applicant = applicant.id
        ))

    
    for contact in app_data.contacts or []:
        con_data = contact.model_dump(
            exclude={
            "date_from",
            "date_to",
            "created_at",
        }
        )
        session.add(Certificate_Applicant_Contact(
            **con_data,
            created_at=time_now,
            date_from=DATE_MIN if is_first_version else time_now,
            date_to=DATE_MAX,
            id_applicant = applicant.id
        ))
    

def create_version_certificate(data, time_now, is_first_version: bool, session):
    cert_data = data.model_dump(exclude={
        "annexes",
        "applicant",
        "manufacturer",
        "certificationAuthority",
        "idTechnicalReglaments",
        "date_to",
        "date_from",
        "created_at",
        "idProductSingleLists"
    })

    cert = Certificate(
        **cert_data,
        created_at=time_now,
        date_from=DATE_MIN if is_first_version else time_now,
        date_to=DATE_MAX,
        idProductSingleLists_str=data.idProductSingleLists,
    )

    session.add(cert)
    session.flush()

    # техрегламенты
    for tech in data.idTechnicalReglaments or []:
        reg = Certificate_has_tech_reglaments(
            id_certificate=cert.id,
            idTechnicalReglaments=tech.tech_reglaments,
        )
        session.add(reg)
    
    # --- приложения/бланки ---
    for annex in data.annexes or []:
        annex_obj = Certificate_Annex(
            idAnnex=annex.idAnnex,
            idType=annex.idType,
            ord=annex.ord,
            pageCount=annex.pageCount,
            id_certificate=cert.id
        )
        session.add(annex_obj)
        session.flush()

        for b in annex.blanks or []:
            session.add(Certificate_AnnexBlank(
                idBlank=b.idBlank,
                blankNumber=b.blankNumber,
                id_annexes=annex_obj.id
            ))
            
    create_applicant(
        cert_obj=cert,
        app_data=data.applicant,
        time_now=time_now,
        is_first_version=is_first_version,
        session=session
    )

    return cert


def save_certificate_to_db(data):
    created_ids = []
    for cert_data in data:
        try:
            time_now = datetime.now(timezone.utc)

            # отдельная транзакция для каждого сертификата
            with get_session() as session:

                existing = get_last_certificate_version(
                    session, cert_data.idCertificate
                )

                if existing:
                    update_old_certificate(existing, time_now, session)
                    cert = create_version_certificate(
                        cert_data, time_now, is_first_version=False, session=session
                    )
                else:
                    cert = create_version_certificate(
                        cert_data, time_now, is_first_version=True, session=session
                    )

                session.commit()
                session.refresh(cert)

                created_ids.append(cert.id)

        except Exception as e:
            # ЛОГИРОВАНИЕ ОШИБКИ
            logging.exception(
                f"Ошибка при обработке сертификата "
                f"idCertificate={cert_data.idCertificate}, number={cert_data.number}: {e}"
            )

            # продолжаем цикл
            continue

    return created_ids