from core.custom_bot import CustomBot
from typing import List
import copy

from config import ATTENDANCE_EMPLOYEE_CHANNEL_ID, ATTENDANCE_TRAINEE_CHANNEL_ID


class DataCache:
    ATTENDANCE_CHANNELS: List[int] = [
        ATTENDANCE_TRAINEE_CHANNEL_ID,
        ATTENDANCE_EMPLOYEE_CHANNEL_ID,
    ]
    STANDUP_CHANNELS: List[int] = []

    @classmethod
    async def initialize(cls, client: CustomBot):
        await cls._load_standup_channels(client)

    @classmethod
    async def _load_standup_channels(cls, client: CustomBot):
        try:
            standup_channels: List[int] = await client.standup_service.get_standup_channels()
            cls.STANDUP_CHANNELS = copy.deepcopy(standup_channels)
        except Exception as e:
            print(f"Error loading standup channels: {e}")
            return
