import discord
from discord.ext import commands

from core.custom_bot import CustomBot


class MembersEvents(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client = client

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.client.member_service.remove_member_from_all_standup_channels(
            member.id
        )


async def setup(client: CustomBot):
    await client.add_cog(MembersEvents(client))
