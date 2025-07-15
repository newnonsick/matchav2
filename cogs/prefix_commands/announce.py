import asyncio
import discord
from discord.ext import commands

from core.custom_bot import CustomBot
from datacache import DataCache
from io import BytesIO


class Announce(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client = client

    async def _send_to_channel(
        self,
        channel: discord.TextChannel,
        message: str | None,
        attachment_bytes: list[tuple[str, bytes]],
    ):
        try:
            files = [
                discord.File(BytesIO(data), filename=filename)
                for filename, data in attachment_bytes
            ]
            await channel.send(content=message, files=files)
        except discord.Forbidden:
            print(f"[Forbidden] Cannot send to channel {channel.id}")
        except discord.HTTPException as e:
            print(f"[HTTPException] Error sending to {channel.id}: {e}")
        except Exception as e:
            print(f"[Error] Unexpected error for {channel.id}: {e}")

    @commands.command(name="announce")
    async def anounce(self, ctx: commands.Context, *, message: str | None = None):
        attachments = ctx.message.attachments

        if not message and not attachments:
            await ctx.reply("You must provide a message or at least one attachment.")
            return

        attachment_bytes = (
            [(att.filename, await att.read()) for att in attachments]
            if attachments
            else []
        )

        channels: list[discord.TextChannel] = [
            ch
            for ch_id in DataCache.STANDUP_CHANNELS
            if (ch := self.client.get_channel(ch_id))
            and isinstance(ch, discord.TextChannel)
        ]

        BATCH_SIZE = 10
        DELAY_BETWEEN_BATCHES = 2

        for i in range(0, len(channels), BATCH_SIZE):
            batch = channels[i : i + BATCH_SIZE]
            await asyncio.gather(
                *(self._send_to_channel(ch, message, attachment_bytes) for ch in batch)
            )
            if i + BATCH_SIZE < len(channels):
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)

        await ctx.reply(f"Announcement sent to {len(channels)} channel{"s" if len(channels) != 1 else ""}.")


async def setup(client: CustomBot):
    await client.add_cog(Announce(client))
