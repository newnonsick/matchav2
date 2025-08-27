from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from core.custom_bot import CustomBot
from collections import defaultdict


class CompanyHoliday(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(
        name="company_holiday", description="Get information about company holidays"
    )
    @app_commands.describe(
        year="The year to get holidays for (optional, defaults to current year)",
    )
    async def company_holiday(self, interaction: discord.Interaction, year: Optional[int] = None):
        if year is None:
            year = interaction.created_at.year

        if year <= 0:
            await interaction.response.send_message(
                "Please provide a valid year greater than 0.", ephemeral=True
            )
            return

        holidays = await self.client.company_service.get_holiday_days_by_year(year)
        if not holidays:
            await interaction.response.send_message(
                f"No company holidays found for the year {year}.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🌟 Company Holidays for {year}",
            color=discord.Color.from_rgb(52, 152, 219),
            description="Here's a list of company holidays for the year:"
        )

        holidays_by_month = defaultdict(list)
        for holiday in holidays:
            month_name = holiday.holiday_date.strftime('%B')
            date_str = holiday.holiday_date.strftime('%a, %d %b %Y')
            holidays_by_month[month_name].append(f"- `{date_str}` — {holiday.description}")

        for month, holiday_lines in holidays_by_month.items():
            embed.add_field(
                name=f"📅 {month}", value="\n".join(holiday_lines), inline=False
            )

        embed.set_footer(text="Enjoy your holidays! 🎉")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(client: "CustomBot"):
    await client.add_cog(CompanyHoliday(client))
