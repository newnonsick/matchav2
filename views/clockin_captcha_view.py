from datetime import datetime
import discord
from typing import TYPE_CHECKING

from modals.clockin_captcha_modal import ClockinCaptchaModal

if TYPE_CHECKING:
    from core.custom_bot import CustomBot

class ClockinCaptchaView(discord.ui.View):

    def __init__(
        self,
        client: "CustomBot",
        author_id: int,
        captcha_text: str,
        clockin_time: datetime,
    ):
        super().__init__(timeout=300)
        self.client = client
        self.author_id = author_id
        self.captcha_text = captcha_text
        self.clockin_time = clockin_time

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.blurple, custom_id="clockin_captcha:submit", emoji="✅")
    async def submit_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This captcha is not for you.", ephemeral=True)
            return

        modal = ClockinCaptchaModal(self.client, self.author_id, self.captcha_text, self.clockin_time)
        callback = await interaction.response.send_modal(modal)


    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        self.stop()