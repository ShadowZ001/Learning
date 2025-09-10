import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN
from utils.database import Database
from utils.emoji import EmojiHandler
from datetime import datetime
import time

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
        self.cooldowns = {}  # User cooldown tracking
        self.bot_admin_id = 1037768611126841405  # Main bot admin
        self.bot_admins = {1037768611126841405}  # Set of bot admins
    
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
        await self.load_extension('cogs.interactions')
        await self.load_extension('cogs.admin')
        await self.load_extension('cogs.whitelist_system')
        # await self.load_extension('cogs.premiumhelp')  # Comment out if doesn't exist

        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands globally")
        except Exception as e:
            print(f"❌ Failed to sync slash commands: {e}")
    
    async def on_guild_join(self, guild):
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"currently {len(self.guilds)} servers")
        await self.change_presence(activity=activity)
        
        # Send thank you message with buttons
        await self.send_guild_join_message(guild)
    
    async def on_guild_remove(self, guild):
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"currently {len(self.guilds)} servers")
        await self.change_presence(activity=activity)
    
    async def on_ready(self):
        print("=" * 50)
        print(f"🤖 {self.user} has connected to Discord!")
        print(f"📊 Bot is in {len(self.guilds)} guilds")
        print(f"👥 Serving {sum(guild.member_count for guild in self.guilds)} users")
        print(f"📅 Ready at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load bot admins from database
        try:
            db_admins = await self.db.get_bot_admins()
            self.bot_admins.update(db_admins)
            print(f"👑 Loaded {len(self.bot_admins)} bot administrators")
        except Exception as e:
            print(f"⚠️ Failed to load bot admins: {e}")
        
        print("=" * 50)
        
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
        
        # Enhanced no-prefix system for premium users and guilds (case-insensitive)
        if message.guild and not message.content.startswith(('>', '/', '<@', '!', '?', '.', '-', '+', '=')):
            premium_cog = self.get_cog('Premium')
            if premium_cog:
                user_premium = await premium_cog.is_premium(message.author.id)
                guild_premium = await premium_cog.is_premium_guild(message.guild.id)
                
                if user_premium or guild_premium:
                    content_stripped = message.content.strip()
                    words = content_stripped.split()
                    
                    if words and len(words[0]) >= 1:  # Allow single characters for short commands
                        first_word = words[0].lower()
                        
                        # Check if starts with letter and is reasonable length
                        if first_word and first_word[0].isalpha() and 1 <= len(first_word) <= 20:
                            # Comprehensive command list (case-insensitive)
                            all_commands = set()
                            
                            # Get all registered commands dynamically
                            for command in self.commands:
                                all_commands.add(command.name.lower())
                                if hasattr(command, 'aliases') and command.aliases:
                                    for alias in command.aliases:
                                        all_commands.add(alias.lower())
                            
                            # Get commands from all cogs
                            for cog in self.cogs.values():
                                for command in cog.get_commands():
                                    all_commands.add(command.name.lower())
                                    if hasattr(command, 'aliases') and command.aliases:
                                        for alias in command.aliases:
                                            all_commands.add(alias.lower())
                                    
                                    # Handle group commands
                                    if hasattr(command, 'commands'):
                                        for subcommand in command.commands:
                                            all_commands.add(f"{command.name.lower()} {subcommand.name.lower()}")
                            
                            # Static command list for reliability (case-insensitive)
                            static_commands = {
                                'help', 'mhelp', 'h', 'serverinfo', 'si', 'userinfo', 'ui', 'botinfo', 'bi',
                                'ping', 'support', 'partnership', 'docs', 'invite', 'stats',
                                'play', 'p', 'skip', 'stop', 'pause', 'resume', 'queue', 'q', 'volume',
                                'shuffle', 'clear', 'nowplaying', 'np', 'loop', 'autoplay', 'music',
                                'ban', 'unban', 'kick', 'mute', 'unmute', 'warn', 'warnings', 'purge',
                                'timeout', 'untimeout', 'slowmode', 'lock', 'unlock', 'role', 'nick',
                                'avatar', 'banner', 'color', 'members', 'moderation',
                                'welcome', 'leave', 'boost', 'autorole', 'automod', 'antinuke',
                                'ticket', 'embed', 'logs', 'prefix', 'giveaway', 'setup',
                                'premium', 'mode', 'activate', 'vip', 'exclusive',
                                'kiss', 'slap', 'kill', 'hug', 'pat', 'poke', 'fun',
                                'afk', 'level', 'rank', 'leaderboard', 'levelup',
                                'whitelist', 'blacklist', 'config', 'reset', 'enable', 'disable',
                                'admin', 'announce', 'add', 'remove', 'list', 'show', 'view'
                            }
                            
                            all_commands.update(static_commands)
                            
                            # Enhanced case-insensitive command matching
                            command_found = False
                            matched_command = None
                            
                            # Strategy 1: Direct exact match (case-insensitive)
                            if first_word in all_commands:
                                command_found = True
                                matched_command = first_word
                            
                            # Strategy 2: Group commands (case-insensitive)
                            elif len(words) >= 2:
                                two_word_cmd = f"{first_word} {words[1].lower()}"
                                if any(two_word_cmd == cmd for cmd in all_commands):
                                    command_found = True
                                    matched_command = two_word_cmd
                                elif first_word in ['antinuke', 'automod', 'premium', 'ticket', 'welcome'] and words[1].lower() in ['setup', 'config', 'show', 'add', 'remove']:
                                    command_found = True
                                    matched_command = two_word_cmd
                            
                            # Strategy 3: Case-insensitive pattern matching
                            if not command_found:
                                # Check all commands with case-insensitive matching
                                for cmd in all_commands:
                                    if cmd.lower() == first_word:
                                        command_found = True
                                        matched_command = cmd
                                        break
                                
                                # Special handling for common command variations
                                if not command_found:
                                    command_variations = {
                                        'help': first_word in ['help', 'h', 'Help', 'HELP', 'Help'],
                                        'botinfo': first_word in ['botinfo', 'bi', 'Botinfo', 'BOTINFO', 'BotInfo'],
                                        'serverinfo': first_word in ['serverinfo', 'si', 'Serverinfo', 'SERVERINFO', 'ServerInfo'],
                                        'userinfo': first_word in ['userinfo', 'ui', 'Userinfo', 'USERINFO', 'UserInfo'],
                                        'antinuke': first_word in ['antinuke', 'anti', 'Antinuke', 'ANTINUKE', 'AntiNuke'],
                                        'automod': first_word in ['automod', 'auto', 'Automod', 'AUTOMOD', 'AutoMod'],
                                        'premium': first_word in ['premium', 'prem', 'Premium', 'PREMIUM']
                                    }
                                    
                                    for base_cmd, matches in command_variations.items():
                                        if matches:
                                            command_found = True
                                            matched_command = base_cmd
                                            break
                            
                            if command_found:
                                prefix = await self.get_prefix(message)
                                # Use the matched command to ensure proper case
                                if matched_command and ' ' in matched_command:
                                    # For group commands
                                    remaining_words = ' '.join(words[2:]) if len(words) > 2 else ''
                                    message.content = f"{prefix}{matched_command} {remaining_words}".strip()
                                else:
                                    # For single commands
                                    remaining_words = ' '.join(words[1:]) if len(words) > 1 else ''
                                    message.content = f"{prefix}{matched_command or first_word} {remaining_words}".strip()
        
        # Process emoji placeholders in message content
        if message.content and hasattr(self, 'emoji_handler'):
            message.content = self.emoji_handler.replace_emojis(message.content)
        
        await self.process_commands(message)
    
    async def send_guild_join_message(self, guild):
        """Send thank you message when bot joins a guild and DM the inviter"""
        try:
            # Send DM to guild owner (inviter)
            await self.send_inviter_dm(guild.owner)
            
            # Find a suitable channel to send the message
            channel = None
            
            # Try to find general, welcome, or first available text channel
            for ch in guild.text_channels:
                if ch.name.lower() in ['general', 'welcome', 'chat', 'main', 'bot-commands']:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            if not channel:
                # Find first channel where bot can send messages
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            if not channel:
                return  # No suitable channel found
            
            # Create thank you embed
            embed = discord.Embed(
                title="🎉 Thank You for Inviting Dravon!",
                description="**Welcome to the Dravon family!**\n\nThank you for choosing Dravon as your server management solution. We're excited to help you build an amazing community!\n\n🚀 **Get Started:**\n• Use `>help` or `/help` to see all available commands\n• Configure your server with `>antinuke setup`\n• Join our support server for assistance",
                color=0x00ff00
            )
            
            embed.add_field(
                name="✨ What's Next?",
                value="• **Setup Welcome Messages** - `>welcome setup`\n• **Configure Security** - `>antinuke setup`\n• **Enable AutoMod** - `>automod setup`\n• **Create Tickets** - `>ticket setup`",
                inline=True
            )
            
            embed.add_field(
                name="💎 Premium Features",
                value="• **No Prefix Commands** - Natural usage\n• **Spotify Music** - High quality streaming\n• **Priority Support** - Faster responses\n• **Advanced Features** - Exclusive tools",
                inline=True
            )
            
            embed.set_thumbnail(url=self.user.display_avatar.url)
            embed.set_footer(text="Powered by Dravon™ • Strong Team. Strong Community.", icon_url=self.user.display_avatar.url)
            
            # Create buttons
            view = discord.ui.View(timeout=None)
            
            support_button = discord.ui.Button(
                label="Support Server",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/UKR78VcEtg",
                emoji="🛠️"
            )
            
            partnership_button = discord.ui.Button(
                label="Partnership",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/NCDpChD6US",
                emoji="🤝"
            )
            
            view.add_item(support_button)
            view.add_item(partnership_button)
            
            await channel.send(embed=embed, view=view)
            
            # Send additional greeting message with help button
            await asyncio.sleep(2)
            
            greet_embed = discord.Embed(
                title="🤖 Dravon is Ready!",
                description="**Your server management bot is now active!**\n\nI'm here to help you manage your server with advanced features like moderation, security, music, tickets, and much more!\n\n**Quick Start:** Click the buttons below to get started!",
                color=0x7289da
            )
            
            greet_embed.set_thumbnail(url=guild.icon.url if guild.icon else self.user.display_avatar.url)
            greet_embed.set_footer(text="Ready to serve your community! • Powered by Dravon™", icon_url=self.user.display_avatar.url)
            
            # Create greeting buttons
            greet_view = discord.ui.View(timeout=None)
            
            support_btn = discord.ui.Button(
                label="Support",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/UKR78VcEtg",
                emoji="🛠️"
            )
            
            help_btn = discord.ui.Button(
                label="Help Commands",
                style=discord.ButtonStyle.primary,
                custom_id="help_command",
                emoji="❓"
            )
            
            greet_view.add_item(support_btn)
            greet_view.add_item(help_btn)
            
            await channel.send(embed=greet_embed, view=greet_view)
            
        except Exception as e:
            print(f"Error sending guild join message: {e}")
    
    async def send_inviter_dm(self, user):
        """Send DM to the user who invited the bot"""
        try:
            if not user:
                return
            
            dm_embed = discord.Embed(
                title="🎉 Thank You for Inviting Dravon!",
                description="**Hey there! Thanks for adding me to your server!**\n\nI'm Dravon, your all-in-one Discord server management bot. I'm here to help you create an amazing community with advanced features!\n\n🚀 **What I can do:**\n• **Advanced Moderation** - Ban, kick, mute, warn\n• **Security System** - AntiNuke protection\n• **Music Player** - Multi-platform streaming\n• **Ticket System** - Professional support\n• **AutoMod** - Automatic content filtering\n• **And much more!**",
                color=0x00ff00
            )
            
            dm_embed.add_field(
                name="🎯 Quick Start",
                value="• Use `>help` to see all commands\n• Run `>antinuke setup` for security\n• Try `>play music` for entertainment\n• Join our support server for help!",
                inline=False
            )
            
            dm_embed.set_thumbnail(url=self.user.display_avatar.url)
            dm_embed.set_footer(text="Welcome to the Dravon family! • Powered by Dravon™", icon_url=self.user.display_avatar.url)
            
            # Create DM buttons
            dm_view = discord.ui.View(timeout=None)
            
            support_button = discord.ui.Button(
                label="Support Server",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/UKR78VcEtg",
                emoji="🛠️"
            )
            
            partnership_button = discord.ui.Button(
                label="Partnership",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/NCDpChD6US",
                emoji="🤝"
            )
            
            dm_view.add_item(support_button)
            dm_view.add_item(partnership_button)
            
            await user.send(embed=dm_embed, view=dm_view)
            
        except discord.Forbidden:
            print(f"Could not send DM to {user} - DMs disabled")
        except Exception as e:
            print(f"Error sending DM to inviter: {e}")
    
    async def process_commands(self, message):
        """Process commands with enhanced cooldown handling and duplicate prevention"""
        ctx = await self.get_context(message)
        if ctx.command is None:
            return
        
        # Prevent duplicate command execution
        command_key = f"{message.author.id}_{message.id}_{ctx.command.name}"
        if hasattr(self, '_processed_commands'):
            if command_key in self._processed_commands:
                return  # Command already processed
        else:
            self._processed_commands = set()
        
        self._processed_commands.add(command_key)
        
        # Clean up old processed commands (keep only last 100)
        if len(self._processed_commands) > 100:
            self._processed_commands = set(list(self._processed_commands)[-50:])
        
        # Apply cooldowns based on premium status
        premium_cog = self.get_cog('Premium')
        if premium_cog and message.guild:
            user_premium = await premium_cog.is_premium(message.author.id)
            guild_premium = await premium_cog.is_premium_guild(message.guild.id)
            
            # No cooldown for premium users/guilds, 2 second cooldown for normal users
            if not (user_premium or guild_premium):
                user_key = f"{message.author.id}_{ctx.command.name}"
                current_time = time.time()
                
                if user_key in self.cooldowns:
                    time_diff = current_time - self.cooldowns[user_key]
                    if time_diff < 2.0:  # 2 second cooldown
                        remaining = 2.0 - time_diff
                        embed = discord.Embed(
                            title="⏰ Command Cooldown",
                            description=f"Please wait **{remaining:.1f}s** before using this command again.\n\n💎 **Upgrade to Premium for no cooldowns!**\n🌟 **Premium guilds also have no cooldowns!**",
                            color=0xff8c00
                        )
                        embed.set_footer(text="Premium users enjoy instant command access!", icon_url=self.user.display_avatar.url)
                        await ctx.send(embed=embed, delete_after=4)
                        return
                
                self.cooldowns[user_key] = current_time
        
        await self.invoke(ctx)

async def main():
    bot = DravonBot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())