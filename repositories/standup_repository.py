from datetime import datetime
from typing import TYPE_CHECKING, Optional

from models import StandupChannel, StandupMessage, UserStandupReport

if TYPE_CHECKING:
    from db.supabase import SupabaseClient


class StandupRepository:

    def __init__(self, supabase_client: "SupabaseClient"):
        self.supabase_client = supabase_client

    async def get_standup_channel_ids(self) -> list:
        client = await self.supabase_client.get_client()
        response = await client.from_("team").select("channel_id").execute()
        return response.data if response.data else []

    async def get_userid_wrote_standup(
        self, channel_id: int, from_datetime: datetime, to_datatime: datetime
    ) -> list:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("message")
            .select("author_id")
            .eq("channel_id", channel_id)
            .gte("timestamp", from_datetime.isoformat())
            .lte("timestamp", to_datatime.isoformat())
            .execute()
        )
        return response.data if response.data else []

    async def userid_in_standup_channel(self, channel_id: int) -> list:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("author_id")
            .eq("channel_id", channel_id)
            .order("server_name", desc=False)
            .execute()
        )
        return response.data if response.data else []

    async def get_standup_by_message_id(
        self, message_id: str
    ) -> Optional[StandupMessage]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("message")
            .select(
                "message_id, author_id, username, servername, channel_id, content, timestamp"
            )
            .eq("message_id", message_id)
            .execute()
        )
        return (
            StandupMessage(**response.data[0])
            if response.data and len(response.data) > 0
            else None
        )

    async def track_standup(self, standup_message: StandupMessage) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("message").insert(standup_message.model_dump()).execute()

    async def regis_new_standup_channel(self, standup_channel: StandupChannel) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("team").insert(standup_channel.model_dump()).execute()

    async def delete_standup_by_message_id(self, message_id: str) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("message").delete().eq(
            "message_id", str(message_id)
        ).execute()

    async def get_standups_by_user_and_datetime(
        self, user_id: str, from_datetime: datetime, to_datetime: datetime
    ) -> list[UserStandupReport]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("message")
            .select("content, timestamp")
            .eq("author_id", user_id)
            .gte("timestamp", from_datetime.isoformat())
            .lte("timestamp", to_datetime.isoformat())
            .order("timestamp", desc=False)
            .execute()
        )
        return (
            [UserStandupReport(**item) for item in response.data]
            if response.data
            else []
        )
