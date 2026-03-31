from app.core.db import Base  # noqa
from app.certificate.models import Certificate, Certificate_has_tech_reglaments
from app.certificate_product.models import (  # noqa
    Certificate_Product,
    Certificate_Product_Identification,
    Certificate_Product_Identification_Document,
    Certificate_Product_Identification_Standard,
)
from app.certificate_testing_labs.models import (  # noqa
    Certificate_Testing_Lab,
    Certificate_Testing_Lab_DocConfirmCustom,
    Certificate_Testing_Lab_DocCentreCustom_CustomInfo,
    Certificate_Testing_Lab_Protocol,
)
