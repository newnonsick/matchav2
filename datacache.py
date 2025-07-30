import copy
from typing import TYPE_CHECKING

from config import ATTENDANCE_EMPLOYEE_CHANNEL_ID, ATTENDANCE_TRAINEE_CHANNEL_ID

if TYPE_CHECKING:
    from discord import Message

    from core.custom_bot import CustomBot


class DataCache:
    ATTENDANCE_CHANNELS: list[int] = [
        ATTENDANCE_TRAINEE_CHANNEL_ID,
        ATTENDANCE_EMPLOYEE_CHANNEL_ID,
    ]
    STANDUP_CHANNELS: list[int] = []
    daily_leave_summary: dict[str, "Message"] = {}

    @classmethod
    async def initialize(cls, client: "CustomBot"):
        await cls._load_standup_channels(client)

    @classmethod
    async def _load_standup_channels(cls, client: "CustomBot"):
        try:
            standup_channels: list[int] = (
                await client.standup_service.get_standup_channel_ids()
            )
            cls.STANDUP_CHANNELS = copy.deepcopy(standup_channels)
        except Exception as e:
            print(f"Error loading standup channels: {e}")
            return
