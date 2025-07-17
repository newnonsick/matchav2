from supabase import AsyncClient

from db.supabase import SupabaseClient


class MemberRepository:

    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client: SupabaseClient = supabase_client

    async def get_all_standup_members(self) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team").select("author_id, server_name").execute()
        )
        return response.data if response.data else []
    
    async def get_standup_members_by_channelid(self, channel_id: str) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("author_id, server_name")
            .eq("channel_id", channel_id)
            .execute()
        )
        return response.data if response.data else []
