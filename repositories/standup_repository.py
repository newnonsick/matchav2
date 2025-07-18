from typing import Optional

from supabase import AsyncClient

from db.supabase import SupabaseClient
from models import StandupChannel, StandupMember, StandupMessage


class StandupRepository:

    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client: SupabaseClient = supabase_client

    async def get_standup_channel_ids(self) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = await client.from_("team").select("channel_id").execute()
        return response.data if response.data else []

    async def get_userid_wrote_standup(
        self, channel_id: int, from_datetime: str, to_datatime: str
    ) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("message")
            .select("author_id")
            .eq("channel_id", channel_id)
            .gte("timestamp", from_datetime)
            .lte("timestamp", to_datatime)
            .execute()
        )
        return response.data if response.data else []

    async def userid_in_standup_channel(self, channel_id: int) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
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
        client: AsyncClient = await self.supabase_client.get_client()
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
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("message").insert(standup_message.model_dump()).execute()

    async def regis_new_standup_channel(self, standup_channel: StandupChannel) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("team").insert(standup_channel.model_dump()).execute()

    async def add_member_to_standup_channel(
        self, standup_member: StandupMember
    ) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("member_team").insert(standup_member.model_dump()).execute()

    async def is_user_added_to_standup_channel(
        self, channel_id: int, user_id: int
    ) -> bool:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("author_id")
            .eq("channel_id", str(channel_id))
            .eq("author_id", str(user_id))
            .execute()
        )
        return bool(response.data)

    async def remove_member_from_standup_channel(
        self, channel_id: int, user_id: int
    ) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("member_team").delete().eq("channel_id", str(channel_id)).eq(
            "author_id", str(user_id)
        ).execute()

    async def delete_standup_by_message_id(self, message_id: str) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("message").delete().eq(
            "message_id", str(message_id)
        ).execute()

    async def get_standups_by_user_and_month(
        self, user_id: str, from_datetime: str, to_datetime: str
    ) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("message")
            .select("content, timestamp")
            .eq("author_id", user_id)
            .gte("timestamp", from_datetime)
            .lte("timestamp", to_datetime)
            .order("timestamp", desc=False)
            .execute()
        )
        return response.data if response.data else []
