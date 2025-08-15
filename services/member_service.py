from datetime import datetime
from typing import TYPE_CHECKING

import discord

from config import RECEIVED_STANDUP_REMOVAL_NOTIFICATION_USERIDS
from models import MemberTeam, StandupMember

if TYPE_CHECKING:
    from repositories.member_repository import MemberRepository
    from core.custom_bot import CustomBot


class MemberService:
    def __init__(self, member_repository: "MemberRepository", client: "CustomBot"):
        self.member_repository = member_repository
        self.client = client

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

    async def is_user_in_any_standup_channel(self, user_id: int) -> bool:
        response = await self.member_repository.get_standup_channels_by_user_id(
            str(user_id)
        )
        return bool(response)

    async def add_member_to_standup_channel(
        self, channel_id: int, user_id: int, user_name: str, created_at: datetime
    ) -> None:
        if await self.is_user_added_to_standup_channel(channel_id, user_id):
            raise ValueError(
                f"User <@{user_id}> is already added to standup channel <#{channel_id}>"
            )

        standup_member = StandupMember(
            channel_id=str(channel_id),
            author_id=str(user_id),
            server_name=user_name,
            created_at=created_at.isoformat(),
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

    async def send_standup_removal_to_related_person(
        self, members: list[MemberTeam], reason: str):
        send_to_userids = RECEIVED_STANDUP_REMOVAL_NOTIFICATION_USERIDS
        if not send_to_userids:
            return
        embed = discord.Embed(
            title="Standup Member Removal Notification",
            description=f"The following members have been removed from standup channels:\n"
                        f"**Reason:** {reason}\n",
            color=discord.Color.from_rgb(231, 76, 60),
        )
        embed.set_footer(text="Matcha Bot • Standup Management")

        inactive_members = [
            f"- <@{member.author_id}> ({member.server_name})" for member in members
        ]

        if not inactive_members:
            embed.add_field(
                name="Inactive Members",
                value="No inactive members found.",
                inline=False,
            )
        else:
            inactive_members_split = [
                inactive_members[i : i + 25] for i in range(0, len(inactive_members), 25)
            ]

            for batch in inactive_members_split:
                embed.add_field(
                    name="Inactive Members",
                    value="\n".join(batch) if batch else "No inactive members found.",
                    inline=False,
                )

        embed.set_footer(text="Made with ❤️ by TN Backend Min")

        try:
            for user_id in send_to_userids:
                user = self.client.get_user(user_id)
                if user:
                    channel = await user.create_dm()
                    await channel.send(embed=embed)
        except discord.Forbidden:
            print(f"Cannot send message to admin channel {channel.id}: Forbidden")
        except Exception as e:
            print(f"Error sending standup removal notification: {e}")

    async def is_admin(self, user_id: int) -> bool:
        role = await self.member_repository.get_user_role(str(user_id))
        return role == "admin"

    async def promote_user_to_admin(self, user_id: int) -> None:
        if not await self.is_user_in_any_standup_channel(user_id):
            raise ValueError(
                "User must be in at least one standup channel to be promoted."
            )

        if await self.is_admin(user_id):
            raise ValueError("User is already an admin.")

        await self.member_repository.update_user_role(str(user_id), "admin")

    async def demote_admin_to_user(self, user_id: int) -> None:
        if not await self.is_user_in_any_standup_channel(user_id):
            raise ValueError(
                "User must be in at least one standup channel to be demoted."
            )

        if not await self.is_admin(user_id):
            raise ValueError("User is not an admin.")

        await self.member_repository.update_user_role(str(user_id), "user")

    async def update_member_display_name(self, user_id: int, new_display_name: str) -> None:
        if not await self.member_repository.is_user_exists(str(user_id)):
            raise ValueError(f"User with ID {user_id} does not exist.")

        await self.member_repository.update_member_display_name(
            str(user_id), new_display_name
        )
