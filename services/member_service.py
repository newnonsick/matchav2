import discord

from models import MemberTeam, StandupMember
from repositories.member_repository import MemberRepository


class MemberService:
    def __init__(self, member_repository: MemberRepository):
        self.member_repository = member_repository

    async def get_all_standup_members(self) -> list[MemberTeam]:
        return await self.member_repository.get_all_standup_members()

    async def get_standup_members_by_channelid(
        self, channel_id: int
    ) -> list[MemberTeam]:
        return await self.member_repository.get_standup_members_by_channelid(
            str(channel_id)
        )

    async def is_user_added_to_standup_channel(
        self, channel_id: int, user_id: int
    ) -> bool:
        response = await self.member_repository.is_user_added_to_standup_channel(
            channel_id=channel_id, user_id=user_id
        )
        return response

    async def add_member_to_standup_channel(
        self, channel_id: int, user_id: int, user_name: str, created_at: str
    ) -> None:
        if await self.is_user_added_to_standup_channel(channel_id, user_id):
            raise ValueError(
                f"User <@{user_id}> is already added to standup channel <#{channel_id}>"
            )

        standup_member = StandupMember(
            channel_id=str(channel_id),
            author_id=str(user_id),
            server_name=user_name,
            created_at=created_at,
        )

        await self.member_repository.add_member_to_standup_channel(standup_member)

    async def remove_member_from_standup_channel(
        self, channel_id: int, user_id: int
    ) -> None:
        if not await self.is_user_added_to_standup_channel(channel_id, user_id):
            raise ValueError(
                f"User <@{user_id}> is not in standup channel <#{channel_id}>"
            )

        await self.member_repository.remove_member_from_standup_channel(
            channel_id=channel_id, user_id=user_id
        )

    async def remove_member_from_all_standup_channels(self, user_id: int) -> None:
        await self.member_repository.remove_member_from_all_standup_channels(
            str(user_id)
        )

    async def send_standup_removal_notification(
        self, member: discord.User, reason: str
    ) -> None:
        channel = await member.create_dm()
        embed = discord.Embed(
            title="🚫 Removed from Standup",
            description=(
                f"{member.mention}, you've been removed from the standup channel.\n\n"
                f"**Reason:** {reason}\n\n"
                "If this seems like a mistake, please contact HR or the Matcha team."
            ),
            color=discord.Color.from_rgb(231, 76, 60),
        )
        embed.set_footer(text="Matcha Bot • Stay engaged!")
        await channel.send(embed=embed)
