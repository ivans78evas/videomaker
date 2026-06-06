from sqlalchemy.orm import Session
from app.models.models import Partner
import uuid

class PartnerService:
    def get_or_create_default_partner(self, db: Session) -> Partner:
        partner = db.query(Partner).first()
        if not partner:
            partner = Partner(
                name="Default Partner",
                email="partner@example.com"
            )
            db.add(partner)
            db.flush()
        return partner

partner_service = PartnerService()
