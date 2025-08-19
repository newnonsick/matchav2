import asyncio
import os

import discord

from config import BOT_TOKEN
from core.custom_bot import CustomBot
from datacache import DataCache

intents = discord.Intents.default()
intents.messages = True
intents.voice_states = True
intents.message_content = True
intents.members = True

client = CustomBot(command_prefix="!", intents=intents, max_messages=0)

async def load_all_cogs(client: CustomBot):
    for folder in ["client_event", "slash_commands", "prefix_commands", "cronjob"]:
        folder_path = f"cogs/{folder}"
        for filename in os.listdir(folder_path):
            if filename.endswith(".py") and filename != "__init__.py":
                cog_path = f"cogs.{folder}.{filename[:-3]}"
                try:
                    await client.load_extension(cog_path)
                    print(f"✅ Loaded cog: {cog_path}")
                except Exception as e:
                    print(f"❌ Failed to load cog {cog_path}: {e}")


async def main():
    async with client:
        await client.db.connect()
        await load_all_cogs(client)
        print("Connected to PostgreSQL successfully.")
        await DataCache.initialize(client)
        await client.start(BOT_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except discord.HTTPException as e:
        if e.status == 429:
            print(
                "The Discord servers denied the connection for making too many requests."
            )
            print(
                "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
            )
            # os.system("python restart.py")
            os.system("kill 1")
        else:
            raise e
