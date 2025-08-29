from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class GatewayEvents(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Gateway Events Cog is ready!")
        await self.client.bot_panel_service.refresh_bot_panel(botAlive=True)
        await self.client.tree.sync()
        print("Synced application commands.")
        if not self.client.user:
            print("We are not logged in.")
            return

        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="Botnoi Employees"
            ),
        )

        print(f"We have logged in as {self.client.user.name}")


async def setup(client: "CustomBot"):
    await client.add_cog(GatewayEvents(client))
