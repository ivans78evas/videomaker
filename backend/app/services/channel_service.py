from sqlalchemy.orm import Session
from app.models.models import YouTubeChannel, Partner
from app.services.partner_service import partner_service

class ChannelService:
    def get_or_create_default_channel(self, db: Session) -> YouTubeChannel:
        channel = db.query(YouTubeChannel).filter(YouTubeChannel.id == "default_channel").first()
        if not channel:
            partner = partner_service.get_or_create_default_partner(db)
            channel = YouTubeChannel(
                id="default_channel",
                partner_id=partner.id,
                title="Default Channel",
                credentials={}
            )
            db.add(channel)
            db.flush()
        return channel

channel_service = ChannelService()
