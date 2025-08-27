import datetime
from typing import TYPE_CHECKING

import discord

from config import CLOCKIN_END_TIME, CLOCKIN_START_TIME
from utils.captcha_utils import generate_captcha
from utils.datetime_utils import convert_to_bangkok, get_datetime_now
from utils.string_utils import random_text
from views.clockin_captcha_view import ClockinCaptchaView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class BotPanelView(discord.ui.View):

    def __init__(
        self,
        client: "CustomBot",
    ):
        super().__init__(timeout=None)
        self.client = client

    @discord.ui.button(
        label="Clock In",
        style=discord.ButtonStyle.green,
        custom_id="bot_panel:clock_in",
        emoji="🕒",
    )
    async def clock_in_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        clockin_time = get_datetime_now()

        if clockin_time.time() < datetime.time(*CLOCKIN_START_TIME):
            # ) or clockin_time.time() > datetime.time(*CLOCKIN_END_TIME):
            await interaction.response.send_message(
                "Clock-in is only allowed between 08:00 and 10:00 AM. Please try again during this time window.",
                ephemeral=True,
            )
            return

        clockedin_log = (
            await self.client.clockin_service.get_clockin_by_author_and_date(
                author_id=str(interaction.user.id), target_date=clockin_time.date()
            )
        )
        if clockedin_log is not None:
            await interaction.response.send_message(
                f"You have already clocked in today at {convert_to_bangkok(clockedin_log.clock_in_time).strftime('%d/%m/%Y %H:%M:%S')}.",
                ephemeral=True,
            )
        else:
            captcha_text = random_text(6)
            captcha_image = await generate_captcha(captcha_text)
            file = discord.File(captcha_image, filename="captcha.png")
            await interaction.response.send_message(
                "Please solve the captcha below to confirm your clock-in:",
                file=file,
                ephemeral=True,
                view=ClockinCaptchaView(
                    self.client, interaction.user.id, captcha_text, clockin_time
                ),
            )
