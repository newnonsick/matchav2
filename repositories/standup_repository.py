from supabase import AsyncClient

from db.supabase import SupabaseClient


class StandupRepository:

    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client: SupabaseClient = supabase_client

    async def get_standup_channels(self) -> list:
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
            .execute()
        )
        return response.data if response.data else []

    async def get_standup_by_message_id(self, message_id: str) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("message")
            .select("content, author_id, timestamp")
            .eq("message_id", message_id)
            .execute()
        )
        return response.data if response.data else []

    async def track_standup(
        self,
        message_id: str,
        author_id: str,
        username: str,
        user_server_name: str,
        channel_id: str,
        content: str,
        timestamp: str,
    ) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("message").insert(
            {
                "message_id": message_id,
                "author_id": author_id,
                "username": username,
                "servername": user_server_name,
                "channel_id": channel_id,
                "content": content,
                "timestamp": timestamp,
            }
        ).execute()

    async def regis_new_standup_channel(
        self,
        channel_id: str,
        team_name: str,
        server_id: str,
        server_name: str,
        timestamp: str,
    ) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("team").insert(
            {
                "channel_id": channel_id,
                "team_name": team_name,
                "server_id": server_id,
                "server_name": server_name,
                "timestamp": timestamp,
            }
        ).execute()

    async def add_member_to_standup_channel(
        self, channel_id: int, user_id: int, user_name: str, created_at: str
    ) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("member_team").insert(
            {
                "channel_id": str(channel_id),
                "author_id": str(user_id),
                "server_name": user_name,
                "created_at": created_at,
            }
        ).execute()

    async def is_user_added_to_standup_channel(
        self, channel_id: int, user_id: int
    ) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("author_id")
            .eq("channel_id", str(channel_id))
            .eq("author_id", str(user_id))
            .execute()
        )
        return response.data if response.data else []
    
    async def remove_member_from_standup_channel(
        self, channel_id: int, user_id: int
    ) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("member_team").delete().eq(
            "channel_id", str(channel_id)
        ).eq("author_id", str(user_id)).execute()

    async def delete_standup_by_message_id(self, message_id: str) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("message").delete().eq("message_id", str(message_id)).execute()
