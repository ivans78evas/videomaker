from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.models import RevenueReport, PartnershipAgreement

class FinanceService:
    def calculate_payout(self, db: Session, channel_id: str, gross_revenue: float, costs: float) -> Dict[str, Any]:
        """
        Calculates the 50/50 split (or other agreed percentage) after processing costs.
        """
        agreement = db.query(PartnershipAgreement).filter(
            PartnershipAgreement.channel_id == channel_id,
            PartnershipAgreement.status == "active"
        ).first()

        share_pct = agreement.share_percentage if agreement else 50.0

        net_profit = gross_revenue - costs
        partner_share = net_profit * (share_pct / 100.0)
        firm_share = net_profit - partner_share

        return {
            "gross": gross_revenue,
            "costs": costs,
            "net": net_profit,
            "partner_payout": partner_share,
            "firm_profit": firm_share
        }

    def generate_monthly_report(self, db: Session, channel_id: str, month: str, gross: float, costs: float):
        metrics = self.calculate_payout(db, channel_id, gross, costs)
        report = RevenueReport(
            channel_id=channel_id,
            month=month,
            gross_revenue=gross,
            processing_costs=costs,
            net_profit=metrics["net"],
            partner_payout=metrics["partner_payout"]
        )
        db.add(report)
        db.commit()
        return report

finance_service = FinanceService()
