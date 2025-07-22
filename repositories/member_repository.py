from supabase import AsyncClient

from db.supabase import SupabaseClient
from models import MemberTeam, StandupMember


class MemberRepository:

    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client: SupabaseClient = supabase_client

    async def get_all_standup_members(self) -> list[MemberTeam]:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team").select("author_id, server_name").execute()
        )
        return [MemberTeam(**item) for item in response.data] if response.data else []

    async def get_standup_members_by_channelid(
        self, channel_id: str
    ) -> list[MemberTeam]:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("author_id, server_name")
            .eq("channel_id", channel_id)
            .execute()
        )
        return [MemberTeam(**item) for item in response.data] if response.data else []

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
