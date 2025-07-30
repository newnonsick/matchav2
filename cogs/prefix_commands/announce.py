from io import BytesIO
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from datacache import DataCache
from utils.decorators import is_admin
from views.announce_confirmation_view import AnnounceConfirmationView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class Announce(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client

    @commands.command(name="announce")
    @is_admin()
    async def announce(self, ctx: commands.Context, *, message: str | None = None):
        attachments = ctx.message.attachments

        if not message and not attachments:
            await ctx.reply("You must provide a message or at least one attachment.")
            return

        attachment_bytes: list[tuple[str, bytes]] = (
            [(att.filename, await att.read()) for att in attachments]
            if attachments
            else []
        )
        preview_message = await ctx.reply(
            f"Previewing announcement:\n\n{message or ''}",
            files=[
                discord.File(BytesIO(data), filename=filename)
                for filename, data in attachment_bytes
            ],
        )

        channels: list[discord.TextChannel] = [
            ch
            for ch_id in DataCache.STANDUP_CHANNELS
            if (ch := self.client.get_channel(ch_id))
            and isinstance(ch, discord.TextChannel)
        ]

        await preview_message.edit(
            view=AnnounceConfirmationView(
                preview_message, attachment_bytes, channels, message
            )
        )


async def setup(client: "CustomBot"):
    await client.add_cog(Announce(client))
