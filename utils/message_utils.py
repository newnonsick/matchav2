import discord

from core.custom_bot import CustomBot


async def clear_bot_reactions(msg: discord.Message, client: CustomBot):
    for reaction in msg.reactions:
        if reaction.me:
            try:
                if client.user is not None:
                    await msg.remove_reaction(reaction.emoji, client.user)
            except discord.HTTPException:
                pass
