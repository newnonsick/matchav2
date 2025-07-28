from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from core.custom_bot import CustomBot
from utils.datetime_utils import (
    get_month_now,
    get_month_range,
    get_weekdays_in_month,
    is_valid_month_format,
)


class CheckStandup(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client: CustomBot = client

    @app_commands.command(name="check_standup", description="Check Stand-Up status")
    @app_commands.describe(month="Month to check (YYYY-MM). Default is current month")
    async def check_standup(
        self, interaction: discord.Interaction, month: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            await interaction.edit_original_response(
                content="This command can only be used in a server."
            )
            return

        if not month:
            month = get_month_now()

        if not is_valid_month_format(month):
            await interaction.edit_original_response(
                content="Invalid month format. Please use YYYY-MM."
            )
            return

        from_datetime, to_datetime = get_month_range(month)
        user_id = interaction.user.id

        try:
            user_standup_data = (
                await self.client.standup_service.get_standups_by_user_and_datetime(
                    user_id=user_id,
                    from_datetime=from_datetime,
                    to_datetime=to_datetime,
                )
            )

            user_leave_data = (
                await self.client.leave_service.get_leave_by_userid_and_date(
                    user_id=user_id,
                    from_date=from_datetime,
                    to_date=to_datetime,
                )
            )

            month_weekdeys = get_weekdays_in_month(month)

            embed = await self.client.standup_service.get_monthly_standup_embed(
                user_standup_data=user_standup_data,
                user_leave_data=user_leave_data,
                month_weekdays=month_weekdeys,
                month=month,
            )

            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            await interaction.edit_original_response(
                content=f"An error occurred while checking stand-up: {str(e)}"
            )


async def setup(client: CustomBot):
    await client.add_cog(CheckStandup(client))
