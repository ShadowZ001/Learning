#!/usr/bin/env python3
"""
Slash Command Sync Script for Dravon Bot
"""

import asyncio
import discord
from discord.ext import commands
import os
from config import TOKEN

async def sync_commands():
    """Sync slash commands"""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    bot = commands.Bot(
        command_prefix=">",
        intents=intents,
        help_command=None
    )
    
    @bot.event
    async def on_ready():
        print(f"🤖 Logged in as {bot.user}")
        print("🔄 Syncing slash commands...")
        
        try:
            # Sync globally
            synced = await bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands globally")
            
            # Optional: Sync to specific guild for testing (faster)
            # guild_id = 1369352923221590047  # Replace with your test guild ID
            # guild = discord.Object(id=guild_id)
            # synced_guild = await bot.tree.sync(guild=guild)
            # print(f"✅ Synced {len(synced_guild)} slash commands to test guild")
            
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
        
        await bot.close()
    
    await bot.start(TOKEN)

if __name__ == "__main__":
    print("🚀 Starting command sync...")
    asyncio.run(sync_commands())