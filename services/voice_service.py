from datetime import date, datetime
from typing import TYPE_CHECKING
from typing_extensions import Literal

if TYPE_CHECKING:
    from core.custom_bot import CustomBot
    from repositories.voice_repository import VoiceRepository


class VoiceService:

    def __init__(self, voiceRepository: "VoiceRepository", client: "CustomBot"):
        self.voiceRepository = voiceRepository
        self.client = client

    async def insert_voice_log(
        self, author_id: str, event_time: datetime, event_type: str, date: date
    ) -> None:
        if event_type not in ["join", "leave"]:
            raise ValueError("event_type must be either 'join' or 'leave'")

        await self.voiceRepository.insert_voice_log(
            author_id, event_time, event_type, date
        )

    async def get_lested_event_type_by_author_id(self, author_id: int) -> Literal["join", "leave"]:
        return await self.voiceRepository.get_lested_event_type_by_author_id(author_id)
