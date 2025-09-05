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
        
        # Check for premium no-prefix commands
        if message.guild:
            premium_cog = self.get_cog('Premium')
            if premium_cog and await premium_cog.is_premium(message.author.id):
                # Always check for no-prefix commands for premium users
                ctx = await self.get_context(message)
                if not ctx.valid and not message.content.startswith(await self.get_prefix(message)):
                    content_lower = message.content.lower().strip()
                    first_word = content_lower.split()[0] if content_lower.split() else ''
                    
                    # Get all available commands dynamically
                    all_command_names = set()
                    
                    # Get all command names from bot's command registry
                    for command in self.all_commands.values():
                        all_command_names.add(command.name.lower())
                        # Also add original case for exact matching
                        all_command_names.add(command.name)
                        if hasattr(command, 'aliases') and command.aliases:
                            all_command_names.update([alias.lower() for alias in command.aliases])
                            all_command_names.update(command.aliases)
                    
                    # Get commands from all loaded cogs (including hybrid commands)
                    for cog_name, cog in self.cogs.items():
                        for command in cog.get_commands():
                            all_command_names.add(command.name.lower())
                            all_command_names.add(command.name)
                            if hasattr(command, 'aliases') and command.aliases:
                                all_command_names.update([alias.lower() for alias in command.aliases])
                                all_command_names.update(command.aliases)
                    
                    # Add comprehensive static command list for safety
                    static_commands = {
                        # Help & Info
                        'help', 'mhelp', 'h', 'serverinfo', 'si', 'userinfo', 'ui', 'botinfo', 'bi',
                        'ping', 'support', 'partnership', 'docs', 'documentation',
                        # Music (all variations)
                        'play', 'p', 'skip', 'stop', 'pause', 'resume', 'queue', 'q', 'volume', 'vol',
                        'shuffle', 'repeat', 'nowplaying', 'np', 'join', 'leave', 'disconnect', 'clear',
                        # Moderation
                        'ban', 'unban', 'kick', 'mute', 'unmute', 'warn', 'warnings', 'purge',
                        'timeout', 'untimeout', 'slowmode', 'lock', 'unlock',
                        # Setup & Config
                        'ticket', 'embed', 'boost', 'welcome', 'automod', 'antinuke', 'giveaway',
                        'logs', 'autorole', 'prefix', 'autoresponder', 'autorule',
                        # Premium & Features
                        'premium', 'teams', 'team', 'levelup', 'level', 'levels', 'rank', 'leaderboard',
                        'afk', 'whitelist', 'stats', 'nodestatus',
                        # Fun Commands (all case variations)
                        'kiss', 'slap', 'kill', 'Kiss', 'Slap', 'Kill', 'KISS', 'SLAP', 'KILL'
                    }
                    all_command_names.update(static_commands)
                    
                    # Check if first word matches any command (case insensitive and exact)
                    original_first_word = message.content.split()[0] if message.content.split() else ''
                    if first_word in all_command_names or original_first_word in all_command_names:
                        # Preserve original case but add prefix
                        prefix = await self.get_prefix(message)
                        message.content = f"{prefix}{message.content}"
                    
                    # Handle common misspellings
                    misspelling_map = {
                        'partership': 'partnership',
                        'parnership': 'partnership',
                        'partneship': 'partnership',
                        'plya': 'play',
                        'palsy': 'play',
                        'skipt': 'skip',
                        'hlep': 'help',
                        'mhlep': 'mhelp',
                        'kil': 'kill',
                        'kis': 'kiss',
                        'kiss': 'kiss',
                        'slaap': 'slap',
                        'kyll': 'kill'
                    }
                    
                    if first_word in misspelling_map:
                        parts = message.content.split()
                        # Replace first word with correct spelling, preserve case style
                        original_case = parts[0]
                        corrected = misspelling_map[first_word]
                        if original_case.isupper():
                            corrected = corrected.upper()
                        elif original_case.istitle():
                            corrected = corrected.title()
                        parts[0] = corrected
                        prefix = await self.get_prefix(message)
                        message.content = f"{prefix}{' '.join(parts)}"
        
        # Process emoji placeholders in message content
        if message.content:
            message.content = self.emoji_handler.replace_emojis(message.content)
        
        await self.process_commands(message)

async def main():
    bot = DravonBot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())