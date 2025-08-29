import datetime
from typing import TYPE_CHECKING
import uuid

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
        emoji="🕒",
    )
    async def clock_in_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        clockin_time = get_datetime_now()

        if clockin_time.time() < datetime.time(
            *CLOCKIN_START_TIME
        ) or clockin_time.time() > datetime.time(*CLOCKIN_END_TIME):
            await interaction.response.send_message(
                "Clock-in is only allowed between 08:00 and 18:00 AM. Please try again during this time window.",
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
            captcha_text = random_text(3, include_chars=["1", "4"])
            captcha_image = await generate_captcha(captcha_text)

            if not captcha_image:
                await interaction.response.send_message(
                    "⚠️ Failed to generate captcha. Please try again later.",
                    ephemeral=True,
                )
                return

            filename = f"captcha_{uuid.uuid4().hex}.png"
            file = discord.File(captcha_image, filename=filename)

            now_unix = int(clockin_time.timestamp())
            now_unix_plus_300 = now_unix + 300

            embed = discord.Embed(
                title="🔐 Clock-In Verification",
                description=(
                    "To complete your clock-in, please solve the captcha below.\n\n"
                    f"⏳ You have **5 minutes** to respond (until <t:{now_unix_plus_300}:T>).\n\n"
                    "✅ Enter the correct text shown in the image to confirm."
                ),
                color=discord.Color.blurple()
            )

            embed.set_image(url=f"attachment://{filename}")
            embed.set_footer(text="Clock-In Security Check")

            await interaction.response.send_message(
                embed=embed,
                file=file,
                ephemeral=True,
                view=ClockinCaptchaView(
                    self.client, interaction.user.id, captcha_text, clockin_time
                ),
            )
