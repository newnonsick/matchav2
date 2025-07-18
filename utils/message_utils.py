import discord


async def clear_bot_reactions(msg: discord.Message, client: discord.Client):
    for reaction in msg.reactions:
        try:
            async for user in reaction.users():
                if client.user is not None and user.id == client.user.id:
                    await msg.remove_reaction(reaction.emoji, user)
        except discord.HTTPException:
            pass
