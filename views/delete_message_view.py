import discord


class DeleteMessageView(discord.ui.View):

    def __init__(self, parent_interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.parent_interaction = parent_interaction

    @discord.ui.button(label="ลบข้อความ", style=discord.ButtonStyle.red)
    async def delete_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.parent_interaction.delete_original_response()
        self.stop()
