from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional
import zipfile

import discord
from discord import app_commands
from discord.ext import commands

from core.custom_bot import CustomBot
from utils.datetime_utils import is_valid_month_format
from utils.email_utils import is_valid_email_format
from utils.file_utils import compress_files_to_zip


class StandupReport(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client: CustomBot = client

    @app_commands.command(
        name="standup_report",
        description="Generate a user standup report for a specific month",
    )
    @app_commands.describe(
        month="The month for which to generate the report (format: YYYY-MM)",
        user="The user for whom to generate the report (defaults is everyone)",
        to_email="The email address to send the report to",
    )
    async def standup_report(
        self,
        interaction: discord.Interaction,
        month: str,
        to_email: str,
        user: Optional[discord.User] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            await interaction.edit_original_response(
                content="This command can only be used in a server."
            )
            return

        if not month:
            await interaction.edit_original_response(
                content="Please provide a month in the format YYYY-MM."
            )
            return

        if not is_valid_month_format(month):
            await interaction.edit_original_response(
                content="Invalid month format. Please use YYYY-MM."
            )
            return

        if not to_email:
            await interaction.edit_original_response(
                content="Please provide an email address to send the report to."
            )
            return

        if not is_valid_email_format(to_email):
            await interaction.edit_original_response(
                content="Invalid email format. Please provide a valid email address."
            )
            return

        try:
            await interaction.edit_original_response(
                content=f"Generating stand-up report for {month}..."
            )

            month_start = datetime.strptime(month, "%Y-%m")

            if month_start.month == 12:
                month_end = datetime(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(
                    month_start.year, month_start.month + 1, 1
                ) - timedelta(days=1)

            from_datetime = month_start.strftime("%Y-%m-%dT%H:%M:%S%z")
            to_datetime = month_end.strftime("%Y-%m-%dT%H:%M:%S%z")

            target_users: list[discord.User] = []
            if user:
                target_users.append(user)
            else:
                all_standup_channel_ids = (
                    await self.client.standup_service.get_standup_channels()
                )
                for channel_id in all_standup_channel_ids:
                    member_ids_in_channel = (
                        await self.client.standup_service.userid_in_standup_channel(
                            channel_id
                        )
                    )
                    for member_id in member_ids_in_channel:
                        discord_user = await self.client.fetch_user(member_id)
                        if discord_user and discord_user not in target_users:
                            target_users.append(discord_user)

            if not target_users:
                await interaction.edit_original_response(
                    content="No users found to generate reports for."
                )
                return

            all_attachments = []
            reports_generated = 0
            for target_user in target_users:
                user_id = str(target_user.id)
                user_name = (
                    target_user.display_name
                    if target_user.display_name
                    else target_user.name
                )

                user_standups = (
                    await self.client.standup_repository.get_standups_by_user_and_month(
                        user_id, from_datetime, to_datetime
                    )
                )

                if not user_standups:
                    continue

                report_buffer = self.client.standup_report_generator.generate_report(
                    user_name, month, user_standups
                )
                report_filename = f"standup_report_{user_name}_{month}.docx"
                all_attachments.append((report_filename, report_buffer))
                reports_generated += 1

            if not all_attachments:
                await interaction.edit_original_response(
                    content="No stand-up reports were generated for the specified criteria."
                )
                return
            
            compessed_file = compress_files_to_zip(all_attachments, f"standup_reports_{month}.zip")
            all_attachments = [(compessed_file.name, compessed_file)]

            if reports_generated > 0:
                if self.client.email_service.send_email(
                    to_email,
                    f"Stand-Up Reports {f"for {user.display_name if user.display_name else user.name}" if user else ""} - {month}",
                    f"Please find attached the stand-up reports for the month of {month}.\n\nRegards,\nMatcha Bot",
                    attachments=all_attachments,
                ):
                    await interaction.edit_original_response(
                        content=f"Successfully generated and sent {reports_generated} stand-up report(s) to {to_email}."
                    )
                else:
                    await interaction.edit_original_response(
                        content=f"Failed to send the combined stand-up report to {to_email}."
                    )
            else:
                await interaction.edit_original_response(
                    content="No stand-up reports were generated or sent for the specified criteria."
                )

        except Exception as e:
            print(f"Error generating stand-up report: {e}")
            await interaction.edit_original_response(
                content=f"An error occurred while generating the report: {str(e)}"
            )


async def setup(client: CustomBot):
    await client.add_cog(StandupReport(client))
