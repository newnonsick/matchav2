import discord

from config import MATCHA_HELP_IMG_URL


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HelpSelect())


class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Main Page",
                value="main_page",
                emoji="🏡",
                description="General information about Matcha Bot",
            ),
            discord.SelectOption(
                label="Stand-Up Commands",
                value="standup_commands",
                emoji="📝",
                description="Streamline your daily stand-ups",
            ),
            discord.SelectOption(
                label="Leave Management Commands",
                value="leave_commands",
                emoji="🌴",
                description="Effortlessly manage leave requests",
            ),
            discord.SelectOption(
                label="Admin Commands (Prefix !)",
                value="admin_commands",
                emoji="👑",
                description="Special commands for administrators",
            ),
        ]
        super().__init__(
            placeholder="📚 Choose a command category!",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        embed = discord.Embed(color=discord.Color.from_rgb(64, 224, 208)).set_image(
            url=MATCHA_HELP_IMG_URL
        )

        if selected_value == "standup_commands":
            embed.title = "📝 Stand-Up Commands"
            embed.description = (
                "**Manage your team's daily stand-ups with ease!**\n\n"
                "**`/register`**\n"
                "  • Set up a channel for stand-ups.\n\n"
                "**`/add_member <user>`**\n"
                "  • Include a user in stand-up tracking.\n\n"
                "**`/remove_user <user|user_id>`**\n"
                "  • Remove a user from stand-up tracking.\n\n"
                "**`/team [date]`**\n"
                "  • See who's submitted stand-ups and who's on leave.\n\n"
                "**`/track <message_id>`**\n"
                "  • Manually track a missed stand-up message.\n\n"
                "**`/standup_report <month> [to_email] [user] [team_channel]`**\n"
                "  • Generate Excel reports for stand-ups, customizable by user/team and delivery.\n\n"
                "**`/check_standup [month]`**\n"
                "  • Review your personal monthly stand-up history, including leave days.\n"
            )
        elif selected_value == "leave_commands":
            embed.title = "🌴 Leave Management Commands"
            embed.description = (
                "**Effortlessly handle leave requests with smart automation!**\n\n"
                "• **Automatic Tracking**: I automatically detect and record leave requests from messages in designated channels using AI. You'll get a private confirmation! *No command needed, just send your leave message!*\n\n"
                "• **Leave Deletion**: If you delete your original leave request, I'll automatically remove it from the system.\n\n"
                "**`/leave_summary [date]`**\n"
                "  • View a real-time summary of all leaves for a specific day.\n"
            )
        elif selected_value == "admin_commands":
            embed.title = "👑 Admin Commands (Prefix `!`)"
            embed.description = (
                "**Special commands for administrators to send announcements.**\n\n"
                "**`!announce [message] [attachments]`**\n"
                "  • Send announcements to all registered stand-up channels with optional files.\n"
            )
        elif selected_value == "main_page":
            embed.title = "🍵 Welcome to Matcha Bot!"
            embed.description = """Hey there! I'm Matcha Bot, your friendly assistant for managing daily stand-ups and leave requests. I'm here to streamline your team's communication and keep everyone in sync. 

Ready to explore what I can do? Use the dropdown menu below to navigate through my commands.

✨ **Select a category to get started!**
"""

        await interaction.response.edit_message(embed=embed, view=self.view)
