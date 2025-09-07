import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN
from utils.database import Database
from utils.emoji import EmojiHandler
from datetime import datetime

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
        
        # Premium no-prefix system - Premium users OR premium guilds
        if message.guild and not message.content.startswith(('>', '/', '<@')):
            premium_cog = self.get_cog('Premium')
            if premium_cog:
                user_premium = await premium_cog.is_premium(message.author.id)
                guild_premium = await premium_cog.is_premium_guild(message.guild.id)
                
                if user_premium or guild_premium:
                    # Only premium users can use commands without prefix
                    content_lower = message.content.lower().strip()
                    first_word = content_lower.split()[0] if content_lower.split() else ''
                    
                    # Comprehensive command list including all cog commands
                    all_command_names = set()
                    
                    # Get all commands from bot
                    def add_commands_recursive(commands):
                        for command in commands:
                            all_command_names.add(command.name.lower())
                            if hasattr(command, 'aliases') and command.aliases:
                                all_command_names.update([alias.lower() for alias in command.aliases])
                            # Handle group commands
                            if hasattr(command, 'commands'):
                                add_commands_recursive(command.commands)
                    
                    # Add all bot commands
                    add_commands_recursive(self.commands)
                    
                    # Add hybrid commands and app commands
                    for cog in self.cogs.values():
                        add_commands_recursive(cog.get_commands())
                    
                    # Extended static command list for all features
                    static_commands = {
                        # Basic commands
                        'help', 'mhelp', 'h', 'serverinfo', 'si', 'userinfo', 'ui', 'botinfo', 'bi',
                        'ping', 'support', 'partnership', 'docs', 'invite',
                        
                        # Music commands
                        'play', 'p', 'skip', 'stop', 'pause', 'resume', 'queue', 'q', 'volume',
                        'shuffle', 'clear', 'nowplaying', 'np', 'loop', 'autoplay',
                        
                        # Moderation commands
                        'ban', 'unban', 'kick', 'mute', 'unmute', 'warn', 'warnings', 'purge',
                        'timeout', 'untimeout', 'slowmode', 'lock', 'unlock',
                        
                        # Setup commands
                        'welcome', 'leave', 'boost', 'autorole', 'automod', 'antinuke',
                        'ticket', 'embed', 'logs', 'prefix',
                        
                        # Premium commands
                        'premium', 'mode', 'activate',
                        
                        # Fun commands
                        'kiss', 'slap', 'kill', 'hug', 'pat', 'poke',
                        
                        # Utility commands
                        'afk', 'level', 'rank', 'leaderboard', 'avatar', 'banner',
                        'giveaway', 'poll', 'remind', 'weather', 'translate',
                        
                        # Admin commands
                        'whitelist', 'blacklist', 'reload', 'sync', 'eval', 'exec'
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
    
    async def process_commands(self, message):
        """Process commands with cooldown handling"""
        ctx = await self.get_context(message)
        if ctx.command is None:
            return
        
        # Apply cooldowns based on premium status
        premium_cog = self.get_cog('Premium')
        if premium_cog and message.guild:
            user_premium = await premium_cog.is_premium(message.author.id)
            guild_premium = await premium_cog.is_premium_guild(message.guild.id)
            
            # No cooldown for premium users/guilds, 2 second cooldown for normal users
            if not (user_premium or guild_premium):
                # Apply 2 second cooldown for non-premium
                if not hasattr(self, '_cooldowns'):
                    self._cooldowns = {}
                
                user_key = f"{message.author.id}_{ctx.command.name}"
                current_time = datetime.now().timestamp()
                
                if user_key in self._cooldowns:
                    time_diff = current_time - self._cooldowns[user_key]
                    if time_diff < 2.0:  # 2 second cooldown
                        remaining = 2.0 - time_diff
                        embed = discord.Embed(
                            title="⏰ Cooldown Active",
                            description=f"Please wait **{remaining:.1f}s** before using this command again.\n\n💎 **Premium users and guilds have no cooldowns!**",
                            color=0xff8c00
                        )
                        await ctx.send(embed=embed, delete_after=3)
                        return
                
                self._cooldowns[user_key] = current_time
        
        await self.invoke(ctx)

async def main():
    bot = DravonBot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())