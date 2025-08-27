from datetime import date, datetime
from typing import TYPE_CHECKING

from models import ClockinLog


if TYPE_CHECKING:
    from core.custom_bot import CustomBot
    from repositories.clockin_repository import ClockinRepository


class ClockinService:

    def __init__(self, clockinRepository: "ClockinRepository", client: "CustomBot"):
        self.clockinRepository = clockinRepository
        self.client = client

    async def create_clockin_log(self, author_id: str, clockin_time: datetime) -> None:
        await self.clockinRepository.create_clockin_log(
            author_id=author_id, clockin_time=clockin_time
        )

    async def get_clockin_by_author_and_date(self, author_id: str, target_date: date) -> ClockinLog | None:
        clockin_record = await self.clockinRepository.get_clockin_by_author_and_date(
            author_id=author_id, target_date=target_date
        )
        return clockin_record

    async def is_user_clocked_in(self, author_id: str, target_date: date) -> bool:
        clockin_record = await self.clockinRepository.get_clockin_by_author_and_date(
            author_id=author_id, target_date=target_date
        )
        return clockin_record is not None