from collections import Counter
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from core.custom_bot import CustomBot
from datacache import DataCache
from utils.datetime_utils import is_valid_month_format
from utils.email_utils import is_valid_email_format
from utils.file_utils import compress_files_to_zip
from utils.string_utils import make_name_safe


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
        team_channel="Optional team channel to generate the report for (defaults to all teams)",
    )
    async def standup_report(
        self,
        interaction: discord.Interaction,
        month: str,
        to_email: Optional[str] = None,
        user: Optional[discord.User] = None,
        team_channel: Optional[discord.TextChannel] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            await interaction.edit_original_response(
                content="This command can only be used in a server."
            )
            return

        if team_channel and user:
            await interaction.edit_original_response(
                content="You cannot specify both a user and a team channel. Please choose one."
            )
            return

        if team_channel:
            if team_channel.id not in DataCache.STANDUP_CHANNELS:
                await interaction.edit_original_response(
                    content="Please select a valid stand-up team channel."
                )
                return

        if not is_valid_month_format(month):
            await interaction.edit_original_response(
                content="Invalid month format. Please use YYYY-MM."
            )
            return

        if to_email and not is_valid_email_format(to_email):
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

            target_users: list[dict] = []
            if user:
                target_users.append(
                    {
                        "author_id": user.id,
                        "server_name": (
                            user.display_name if user.display_name else user.name
                        ),
                    }
                )
            else:
                if team_channel:
                    all_standup_members = await self.client.member_service.get_standup_members_by_channelid(
                        team_channel.id
                    )
                else:
                    all_standup_members = (
                        await self.client.member_service.get_all_standup_members()
                    )
                target_users.extend(all_standup_members)

            if not target_users:
                await interaction.edit_original_response(
                    content="No users found to generate reports for."
                )
                return

            all_attachments = []
            reports_generated = 0
            for target_user in target_users:
                target_user_id = target_user["author_id"]
                target_user_name = target_user["server_name"]

                user_standups = (
                    await self.client.standup_service.get_standups_by_user_and_month(
                        target_user_id, from_datetime, to_datetime
                    )
                )

                if not user_standups:
                    continue

                report_buffer = self.client.standup_report_generator.generate_report(
                    make_name_safe(target_user_name), month, user_standups
                )
                report_filename = f"standup_{make_name_safe(target_user_name)}_{target_user_id}_{month}.xlsx"
                all_attachments.append((report_filename, report_buffer))
                reports_generated += 1

            if not all_attachments:
                await interaction.edit_original_response(
                    content="No stand-up reports were generated for the specified criteria."
                )
                return

            if to_email:
                file_user_name = (
                    f"{make_name_safe(user.display_name) if user.display_name else make_name_safe(user.name)}_"
                    if user
                    else ""
                )
                file_team_name = (
                    f"{make_name_safe(team_channel.name)}_" if team_channel else ""
                )
                compessed_file = compress_files_to_zip(
                    all_attachments,
                    f"{file_user_name}{file_team_name}standup_{month}.zip",
                )
                all_attachments: list[tuple[str, BytesIO]] = [
                    (compessed_file.name, compessed_file)
                ]
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

                user_dm = interaction.user
                if not user_dm:
                    await interaction.edit_original_response(
                        content="Could not send report to your DM. Please ensure your DMs are open."
                    )
                    return

                current_zip_files = []
                current_size = 0
                file_part = 1
                MAX_DM_ATTACHMENT_SIZE = 8 * 1024 * 1024
                file_user_name = (
                    f"{make_name_safe(user.display_name) if user.display_name else make_name_safe(user.name)}_"
                    if user
                    else ""
                )
                file_team_name = (
                    f"{make_name_safe(team_channel.name)}_" if team_channel else ""
                )

                all_zip_files: list[discord.File] = []

                await interaction.edit_original_response(
                    content=f"Successfully generated {reports_generated} stand-up report(s). Sending to your DMs..."
                )

                for filename, file_buffer in all_attachments:
                    file_buffer.seek(0)
                    file_size = len(file_buffer.getvalue())

                    if (
                        current_size + file_size > MAX_DM_ATTACHMENT_SIZE
                        and current_zip_files
                    ):
                        zip_name = f"{file_user_name}{file_team_name}standup_{month}_{file_part}.zip"
                        zip_bytes_io = compress_files_to_zip(
                            current_zip_files, zip_name
                        )

                        all_zip_files.append(
                            discord.File(zip_bytes_io, filename=zip_name)
                        )

                        current_zip_files = []
                        current_size = 0
                        file_part += 1

                    current_zip_files.append((filename, file_buffer))
                    current_size += file_size

                if current_zip_files:
                    zip_name = f"{file_user_name}{file_team_name}standup_{month}_{file_part}.zip"
                    zip_bytes_io = compress_files_to_zip(current_zip_files, zip_name)

                    all_zip_files.append(discord.File(zip_bytes_io, filename=zip_name))

                try:
                    await user_dm.send(
                        content=f"Here are your stand-up reports for the month of {month}.",
                        files=all_zip_files,
                    )
                    await interaction.edit_original_response(
                        content=f"Successfully sent {reports_generated} stand-up report(s) to your DMs."
                    )
                except discord.Forbidden:
                    await interaction.edit_original_response(
                        content="Could not send the report to your DMs. Please ensure your DMs are open."
                    )
                    return

        except Exception as e:
            print(f"Error generating stand-up report: {e}")
            await interaction.edit_original_response(
                content=f"An error occurred while generating the report: {str(e)}"
            )


async def setup(client: CustomBot):
    await client.add_cog(StandupReport(client))
