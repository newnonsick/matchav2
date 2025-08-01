from typing import TYPE_CHECKING, Optional

from models import MemberTeam, StandupMember, Team

if TYPE_CHECKING:
    from db.supabase import SupabaseClient


class MemberRepository:

    def __init__(self, supabase_client: "SupabaseClient"):
        self.supabase_client = supabase_client

    async def get_all_standup_members(self) -> list[MemberTeam]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team").select("author_id, server_name").execute()
        )
        return [MemberTeam(**item) for item in response.data] if response.data else []

    async def get_standup_members_by_channelid(
        self, channel_id: str
    ) -> list[MemberTeam]:
        client = await self.supabase_client.get_client()
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
        client = await self.supabase_client.get_client()
        await client.from_("member_team").insert(standup_member.model_dump()).execute()

    async def is_user_added_to_standup_channel(
        self, channel_id: int, user_id: int
    ) -> bool:
        client = await self.supabase_client.get_client()
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
        client = await self.supabase_client.get_client()
        await client.from_("member_team").delete().eq("channel_id", str(channel_id)).eq(
            "author_id", str(user_id)
        ).execute()

    async def remove_member_from_all_standup_channels(self, user_id: str) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("member_team").delete().eq("author_id", user_id).execute()

    async def get_user_role(self, user_id: str) -> Optional[str]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("role")
            .eq("author_id", user_id)
            .execute()
        )
        if response.data:
            return response.data[0].get("role")
        return None

    async def update_user_role(self, user_id: str, role: str) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("member_team").update({"role": role}).eq(
            "author_id", user_id
        ).execute()

    async def get_standup_channels_by_user_id(self, user_id: str) -> list[Team]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("team(channel_id, server_id, server_name, team_name)")
            .eq("author_id", user_id)
            .execute()
        )
        return [Team(**item["team"]) for item in response.data] if response.data else []

    async def is_user_exists(self, user_id: str) -> bool:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("member_team")
            .select("author_id")
            .eq("author_id", user_id)
            .execute()
        )
        return bool(response.data)

    async def update_member_display_name(
        self, user_id: str, new_display_name: str
    ) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("member_team").update({"server_name": new_display_name}).eq(
            "author_id", user_id
        ).execute()
