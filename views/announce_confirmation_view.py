import asyncio
from io import BytesIO

import discord


class AnnounceConfirmationView(discord.ui.View):

    def __init__(
        self,
        parent_message: discord.Message,
        attachment_bytes: list[tuple[str, bytes]],
        channels: list[discord.TextChannel],
        message: str | None = None,
    ):
        super().__init__(timeout=60)
        self.parent_message = parent_message
        self.attachment_bytes = attachment_bytes
        self.channels = channels
        self.message = message

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

    @discord.ui.button(label="Comfrim", style=discord.ButtonStyle.green)
    async def confirm_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.parent_message.edit(
            content="Sending announcement...",
            view=None,
            attachments=[],
        )

        BATCH_SIZE = 10
        DELAY_BETWEEN_BATCHES = 2

        for i in range(0, len(self.channels), BATCH_SIZE):
            batch = self.channels[i : i + BATCH_SIZE]
            await asyncio.gather(
                *(
                    self._send_to_channel(ch, self.message, self.attachment_bytes)
                    for ch in batch
                )
            )
            if i + BATCH_SIZE < len(self.channels):
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)

        await self.parent_message.edit(
            content=f"Announcement sent to {len(self.channels)} channel{"s" if len(self.channels) != 1 else ""}.",
            view=None,
            attachments=[],
        )
        self.stop()

    @discord.ui.button(label="Cancle", style=discord.ButtonStyle.red)
    async def cancel_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.parent_message.edit(
            content=f"Announcement cancelled.",
            view=None,
            attachments=[],
        )
        self.stop()

    async def on_timeout(self):
        try:
            await self.parent_message.edit(
                content=f"Announcement timed out.",
                view=None,
                attachments=[],
            )
            self.stop()
        except discord.HTTPException:
            pass
