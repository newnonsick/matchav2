from datetime import datetime
from typing import TYPE_CHECKING

import discord

from utils.datetime_utils import convert_to_bangkok, get_date_now

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class ClockinCaptchaModal(discord.ui.Modal):
    def __init__(
        self,
        client: "CustomBot",
        author_id: int,
        captcha_text: str,
        clockin_time: datetime,
        parent_view: discord.ui.View,
    ):
        super().__init__(title="Clock-in Captcha", timeout=300)
        self.client = client
        self.author_id = author_id
        self.captcha_text = captcha_text
        self.clockin_time = clockin_time
        self.parent_view = parent_view

        self.captcha_input = discord.ui.TextInput(
            label="Enter the text shown in the image",
            style=discord.TextStyle.short,
            placeholder="Type the captcha text here...",
            required=True,
            max_length=10,
            min_length=0,
        )
        self.add_item(self.captcha_input)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This captcha is not for you.", ephemeral=True
            )
            return

        if self.captcha_input.value.lower() != self.captcha_text.lower():
            await interaction.response.send_message(
                "Incorrect captcha. Please try again.", ephemeral=True
            )
            return

        existing_clockin = (
            await self.client.clockin_service.get_clockin_by_author_and_date(
                author_id=str(self.author_id), target_date=get_date_now()
            )
        )

        if existing_clockin:
            await interaction.response.send_message(
                f"You have already clocked in today at {convert_to_bangkok(existing_clockin.clock_in_time).strftime('%d/%m/%Y %H:%M:%S')}.",
                ephemeral=True,
            )

            self.parent_view.stop()
            self.stop()
            return

        await self.client.clockin_service.create_clockin_log(
            author_id=str(self.author_id), clockin_time=self.clockin_time
        )

        await interaction.response.send_message(
            f"✅ Clock-in successful at {self.clockin_time.strftime('%d/%m/%Y %H:%M:%S')}. Wishing you a productive day!",
            ephemeral=True,
        )

        self.parent_view.stop()
        self.stop()
