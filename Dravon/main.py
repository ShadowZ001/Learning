import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN
from utils.database import Database
from utils.emoji import EmojiHandler

class DravonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None
        )
        
        self.db = Database()
        self.emoji_handler = EmojiHandler()
    
    async def get_prefix(self, message):
        if not message.guild:
            return ">"
        
        custom_prefix = await self.db.get_prefix(message.guild.id)
        return custom_prefix or ">"
    
    async def setup_hook(self):
        await self.load_extension('cogs.welcome')
        await self.load_extension('cogs.prefix')
        await self.load_extension('cogs.autoresponder')
        await self.load_extension('cogs.serverinfo')
        await self.load_extension('cogs.autorule')
        await self.load_extension('cogs.stats')
        await self.load_extension('cogs.autorole')
        await self.load_extension('cogs.purge')
        await self.load_extension('cogs.moderation')
        await self.load_extension('cogs.automod')
        await self.load_extension('cogs.antinuke')
        await self.load_extension('cogs.logs')
        await self.load_extension('cogs.giveaway')
        await self.load_extension('cogs.boost')
        await self.load_extension('cogs.leave')
        await self.load_extension('cogs.ticket')
        await self.load_extension('cogs.embed')
        await self.load_extension('cogs.botinfo')
        await self.load_extension('cogs.help')
        await self.load_extension('cogs.music')
        await self.load_extension('cogs.premium')
        await self.load_extension('cogs.userinfo')
        await self.load_extension('cogs.teams')
        await self.load_extension('cogs.levelup')
        await self.load_extension('cogs.afk')
        await self.load_extension('cogs.whitelist')
        await self.load_extension('cogs.docs')
        await self.load_extension('cogs.botadmin')
        await self.load_extension('cogs.mention')
        await self.load_extension('cogs.emoji')
        await self.load_extension('cogs.fun')

        await self.tree.sync()
        print(f"Synced slash commands")
    
    async def on_guild_join(self, guild):
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"currently {len(self.guilds)} servers")
        await self.change_presence(activity=activity)
    
    async def on_guild_remove(self, guild):
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"currently {len(self.guilds)} servers")
        await self.change_presence(activity=activity)
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Start rotating status
        self.status_task = asyncio.create_task(self.rotate_status())
    
    async def rotate_status(self):
        statuses = [
            "shadow >3",
            f"currently {len(self.guilds)} servers"
        ]
        
        while not self.is_closed():
            for status in statuses:
                if status.startswith("currently"):
                    status = f"currently {len(self.guilds)} servers"
                
                activity = discord.Activity(type=discord.ActivityType.watching, name=status)
                await self.change_presence(activity=activity)
                await asyncio.sleep(10)  # Change every 10 seconds
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Check if user is blacklisted
        botadmin_cog = self.get_cog('BotAdmin')
        if botadmin_cog and botadmin_cog.is_blacklisted(message.author.id):
            return
        
        # Premium no-prefix system - ONLY for premium users
        if message.guild and not message.content.startswith(('>', '/', '<@')):
            premium_cog = self.get_cog('Premium')
            if premium_cog and await premium_cog.is_premium(message.author.id):
                # Only premium users can use commands without prefix
                ctx = await self.get_context(message)
                if not ctx.valid:
                    content_lower = message.content.lower().strip()
                    first_word = content_lower.split()[0] if content_lower.split() else ''
                    
                    # Get all command names (case-insensitive)
                    all_command_names = set()
                    
                    # Get commands from bot registry
                    for command in self.all_commands.values():
                        all_command_names.add(command.name.lower())
                        if hasattr(command, 'aliases') and command.aliases:
                            all_command_names.update([alias.lower() for alias in command.aliases])
                    
                    # Get commands from all cogs
                    for cog in self.cogs.values():
                        for command in cog.get_commands():
                            all_command_names.add(command.name.lower())
                            if hasattr(command, 'aliases') and command.aliases:
                                all_command_names.update([alias.lower() for alias in command.aliases])
                    
                    # Static command list for reliability
                    static_commands = {
                        'help', 'mhelp', 'h', 'serverinfo', 'si', 'userinfo', 'ui', 'botinfo', 'bi',
                        'ping', 'support', 'partnership', 'docs', 'play', 'p', 'skip', 'stop', 
                        'pause', 'resume', 'queue', 'q', 'volume', 'ban', 'kick', 'mute', 'warn',
                        'ticket', 'embed', 'premium', 'kiss', 'slap', 'kill', 'afk', 'level'
                    }
                    all_command_names.update(static_commands)
                    
                    # Check if first word is a command (case-insensitive)
                    if first_word in all_command_names:
                        prefix = await self.get_prefix(message)
                        message.content = f"{prefix}{message.content}"
        
        # Process emoji placeholders in message content
        if message.content:
            message.content = self.emoji_handler.replace_emojis(message.content)
        
        await self.process_commands(message)

async def main():
    bot = DravonBot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())