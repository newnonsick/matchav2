from typing import TYPE_CHECKING

import discord

from config import BOT_PANEL_IMG_URL
from models import BotPanel
from views.bot_panel_view import BotPanelView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot
    from repositories.bot_panel_repository import BotPanelRepository


class BotPanelService:

    def __init__(self, botPanelRepository: "BotPanelRepository", client: "CustomBot"):
        self.botPanelRepository = botPanelRepository
        self.client = client

    async def get_bot_panel(self) -> BotPanel | None:
        bot_panel = await self.botPanelRepository.get_bot_panel()
        return bot_panel

    async def delete_bot_panel(self) -> None:
        bot_panel = await self.botPanelRepository.get_bot_panel()
        if bot_panel:
            channel = await self.client.fetch_channel(bot_panel.channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                try:
                    message = await channel.fetch_message(bot_panel.message_id)
                    await message.delete()
                except discord.NotFound:
                    print(
                        "Bot panel message not found, it may have been deleted already."
                    )
                except Exception as e:
                    print(f"Failed to delete bot panel message: {e}")

        await self.botPanelRepository.delete_bot_panel()

    async def insert_bot_panel(self, message_id: int, channel_id: int) -> None:
        await self.botPanelRepository.insert_bot_panel(message_id, channel_id)

    def get_bot_panel_embed(self, botAlive: bool = True) -> discord.Embed:
        embed = discord.Embed(
            title="MATCHA BOT - EXCLUSIVE HR MANAGEMENT SYSTEM",
            color=discord.Color.from_rgb(144, 213, 255),
        )

        status_lines = []
        if botAlive:
            status_lines.append("[Matcha Bot]: 🟢\n")
        else:
            status_lines.append("[Matcha Bot]: 🔴\n")

        embed.add_field(
            name="Status Meaning:",
            value=(
                "🟢 - Online\n"
                "🔴 - Offline\n"
                "❓  - Unknown (could not check status)\n"
            ),
            inline=False,
        )

        embed.add_field(
            name="Status:",
            value=f"```ini\n" + "".join(status_lines) + "```",
            inline=False,
        )

        embed.set_image(url=BOT_PANEL_IMG_URL)

        embed.set_footer(text="Made with ❤️ by Matcha Team")

        return embed

    async def setup_bot_panel(self, interaction: discord.Interaction) -> None:
        await interaction.edit_original_response(
            content="🎛️ Setting up the **Control Panel**... 🚀", view=None
        )

        embed = self.client.bot_panel_service.get_bot_panel_embed(botAlive=True)
        if isinstance(interaction.channel, discord.TextChannel):
            message = await interaction.channel.send(
                embed=embed, view=BotPanelView(self.client)
            )
            await self.client.bot_panel_service.insert_bot_panel(
                message_id=message.id, channel_id=interaction.channel.id
            )
            await interaction.edit_original_response(
                content="✅ The Control Panel has been set up successfully!",
                view=None,
            )
        else:
            await interaction.followup.send(
                "🚫 Use this in a text channel!", ephemeral=True
            )

    async def refresh_bot_panel(self, botAlive: bool) -> None:
        bot_panel = await self.get_bot_panel()
        if not bot_panel:
            print("Bot panel does not exist. Cannot refresh.")
            return

        channel = await self.client.fetch_channel(bot_panel.channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            await self.delete_bot_panel()
            return

        try:
            message = await channel.fetch_message(bot_panel.message_id)
        except discord.NotFound:
            await self.delete_bot_panel()
            return
        except Exception as e:
            print(f"Failed to fetch bot panel message: {e}")
            return

        embed = self.get_bot_panel_embed(botAlive=botAlive)
        try:
            await message.edit(embed=embed, view=BotPanelView(self.client))
        except Exception as e:
            print(f"Failed to edit bot panel message: {e}")
