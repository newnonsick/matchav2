from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class MembersEvents(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.client.member_service.remove_member_from_all_standup_channels(
            member.id
        )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.display_name != after.display_name:
            await self.client.member_service.update_member_display_name(
                after.id, after.display_name
            )


async def setup(client: "CustomBot"):
    await client.add_cog(MembersEvents(client))
