from discord import File, Forbidden, TextChannel
from discord.ext import commands

from core.custom_bot import CustomBot
from datacache import DataCache


class Anounce(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client = client

    @commands.command(name="anounce")
    async def anounce(self, ctx: commands.Context, *, message: str | None = None):
        attachments = ctx.message.attachments
        if not message and not attachments:
            await ctx.reply("You must provide a message or at least one attachment.")
            return

        for channel_id in DataCache.STANDUP_CHANNELS:
            channel = self.client.get_channel(channel_id)
            if channel and isinstance(channel, TextChannel):
                try:
                    # if message:
                    #     await channel.send(message)

                    # for attachment in attachments:
                    #     await channel.send(file=await attachment.to_file())
                    files = [await attachment.to_file() for attachment in attachments]
                    await channel.send(content=message, files=files)
                except Forbidden:
                    print(f"Cannot send message to channel {channel_id}: Forbidden")
                except Exception as e:
                    print(f"Error sending announcement to channel {channel_id}: {e}")


async def setup(client: CustomBot):
    await client.add_cog(Anounce(client))
