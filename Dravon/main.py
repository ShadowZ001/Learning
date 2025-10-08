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
        intents.reactions = True
        
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
        self.start_time = time.time()  # Bot start time
    
    async def get_prefix(self, message):
        if not message.guild:
            return ">"
        
        custom_prefix = await self.db.get_prefix(message.guild.id)
        return custom_prefix or ">"
    
    async def setup_hook(self):
        # Load all existing cogs
        cogs = [
            'cogs.welcome', 'cogs.prefix', 'cogs.autoresponder', 'cogs.serverinfo',
            'cogs.stats', 'cogs.autorole', 'cogs.purge',
            'cogs.automod_advanced', 'cogs.antinuke',
            'cogs.logs', 'cogs.giveaway', 'cogs.boost', 'cogs.leave',
            'cogs.ticket', 'cogs.embed', 'cogs.botinfo', 'cogs.help_new',
            'cogs.music', 'cogs.premium', 'cogs.userinfo', 'cogs.teams',
            'cogs.levelup', 'cogs.afk', 'cogs.whitelist', 'cogs.docs',
            'cogs.botadmin', 'cogs.mention', 'cogs.emoji', 'cogs.fun', 'cogs.badge', 'cogs.youtube', 'cogs.admin_panel',
            'cogs.interactions', 'cogs.whitelist_system',
            'cogs.uptime', 'cogs.users', 'cogs.invites',
            'cogs.ping', 'cogs.media', 'cogs.voice_panel',
            'cogs.music_panel', 'cogs.extraowner', 'cogs.meme', 'cogs.verify',
            'cogs.reactionrole', 'cogs.userprofile', 'cogs.moderation_new',
            'cogs.maintenance', 'cogs.ai_chat', 'cogs.messages', 'cogs.vote', 'cogs.rps', 'cogs.autorule', 'cogs.apply'
        ]
        
        loaded = 0
        for cog in cogs:
            try:
                await self.load_extension(cog)
                loaded += 1
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        
        print(f"✅ Loaded {loaded} cogs total")

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
            f"currently {len(self.guilds)} servers",
            "Try >help",
            ">help | >support"
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
        
        # Skip blacklist check for now
        # botadmin_cog = self.get_cog('BotAdmin')
        # if botadmin_cog and botadmin_cog.is_blacklisted(message.author.id):
        #     return
        
        # Enhanced command suggestions
        if message.guild and message.content.startswith('>'):
            ctx = await self.get_context(message)
            if ctx.command is None and len(message.content) > 1:
                # Extract the attempted command
                attempted_command = message.content[1:].split()[0].lower()
                
                # Expanded command suggestions
                suggestions = {
                    'help': ['help', 'h', 'commands', 'cmd', 'command', 'cmds'],
                    'serverinfo': ['serverinfo', 'si', 'server', 'guild', 'sinfo', 'guildinfo', 'serverstats'],
                    'userinfo': ['userinfo', 'ui', 'user', 'profile', 'uinfo', 'whois', 'info'],
                    'botinfo': ['botinfo', 'bi', 'bot', 'info', 'binfo', 'about', 'stats'],
                    'play': ['play', 'p', 'music', 'song', 'mp3', 'youtube', 'yt', 'spotify'],
                    'premium': ['premium', 'prem', 'vip', 'pro', 'upgrade'],
                    'antinuke': ['antinuke', 'anti', 'security', 'protection', 'nuke', 'secure', 'safety'],
                    'automod': ['automod', 'auto', 'mod', 'moderation', 'amod', 'filter', 'automoderation'],
                    'invites': ['invites', 'invite', 'inv', 'i', 'invs', 'invitations'],
                    'ping': ['ping', 'latency', 'pong', 'lag', 'ms', 'speed'],
                    'kick': ['kick', 'remove', 'boot', 'eject'],
                    'ban': ['ban', 'banish', 'block', 'hammer'],
                    'mute': ['mute', 'timeout', 'silence', 'quiet', 'shush'],
                    'warn': ['warn', 'warning', 'caution', 'alert'],
                    'purge': ['purge', 'clear', 'delete', 'clean', 'prune'],
                    'voicepanel': ['voicepanel', 'vp', 'voice', 'vc', 'vpanel'],
                    'musicpanel': ['musicpanel', 'mp', 'music', 'mpanel'],

                    'ticket': ['ticket', 'support', 'tickets', 'tkt'],
                    'giveaway': ['giveaway', 'gw', 'give', 'contest', 'raffle'],
                    'embed': ['embed', 'announcement', 'message', 'rich'],
                    'welcome': ['welcome', 'greet', 'greeting', 'join'],
                    'roleadd': ['roleadd', 'addrole', 'giverole', 'role'],
                    'avatar': ['avatar', 'av', 'pfp', 'picture', 'pic'],
                    'banner': ['banner', 'bn', 'cover'],
                    'profile': ['profile', 'pr', 'bio', 'about']
                }
                
                # Find best match with fuzzy matching
                best_match = None
                best_score = 0
                
                for cmd, aliases in suggestions.items():
                    for alias in aliases:
                        # Exact match
                        if attempted_command == alias:
                            best_match = cmd
                            best_score = 100
                            break
                        # Starts with match
                        elif attempted_command.startswith(alias) or alias.startswith(attempted_command):
                            score = len(attempted_command) / len(alias) * 80
                            if score > best_score:
                                best_match = cmd
                                best_score = score
                        # Contains match
                        elif attempted_command in alias or alias in attempted_command:
                            score = 60
                            if score > best_score:
                                best_match = cmd
                                best_score = score
                    if best_score == 100:
                        break
                
                if best_match and best_score > 50:
                    embed = discord.Embed(
                        title="💡 Command Suggestion",
                        description=f"Did you mean `>{best_match}`?\n\n*Tip: Use `>help` to see all available commands!*",
                        color=0x7289da
                    )
                    embed.set_thumbnail(url=self.user.display_avatar.url)
                    embed.set_footer(text="Dravon™ Smart Suggestions", icon_url=self.user.display_avatar.url)
                    await message.channel.send(embed=embed, delete_after=8)
                elif len(attempted_command) > 2:
                    # Show helpful message for unknown commands
                    embed = discord.Embed(
                        title="❓ Command Not Found",
                        description=f"Command `{attempted_command}` not found.\n\n**Quick Help:**\n• Use `>help` to see all commands\n• Try `>botinfo` for bot information\n• Need support? Use `>support`",
                        color=0xff8c00
                    )
                    embed.set_thumbnail(url=self.user.display_avatar.url)
                    embed.set_footer(text="Need help? Join our support server!", icon_url=self.user.display_avatar.url)
                    await message.channel.send(embed=embed, delete_after=10)
        
        # No-prefix system for PREMIUM users only
        if message.guild and not message.content.startswith(('>', '/', '<@', '!', '?', '.', '-', '+', '=')):
            premium_cog = self.get_cog('Premium')
            if not premium_cog:
                return
            
            user_premium = await premium_cog.is_premium(message.author.id)
            guild_premium = await premium_cog.is_premium_guild(message.guild.id)
            
            if not (user_premium or guild_premium):
                return
            
            content_stripped = message.content.strip()
            words = content_stripped.split()
            
            if words and len(words[0]) >= 1:
                first_word = words[0].lower()
                
                if first_word and first_word[0].isalpha() and 1 <= len(first_word) <= 20:
                    # Get all commands
                    all_commands = set()
                    
                    for command in self.commands:
                        all_commands.add(command.name.lower())
                        if hasattr(command, 'aliases') and command.aliases:
                            for alias in command.aliases:
                                all_commands.add(alias.lower())
                    
                    for cog in self.cogs.values():
                        for command in cog.get_commands():
                            all_commands.add(command.name.lower())
                            if hasattr(command, 'aliases') and command.aliases:
                                for alias in command.aliases:
                                    all_commands.add(alias.lower())
                    
                    # Static commands
                    static_commands = {
                        'help', 'serverinfo', 'si', 'userinfo', 'ui', 'botinfo', 'bi',
                        'ping', 'play', 'p', 'skip', 'stop', 'pause', 'resume', 'queue',
                        'ban', 'kick', 'mute', 'unmute', 'purge', 'antinuke', 'automod',
                        'ticket', 'premium', 'voicepanel', 'vp', 'musicpanel', 'mp'
                    }
                    
                    all_commands.update(static_commands)
                    
                    if first_word in all_commands:
                        prefix = await self.get_prefix(message)
                        remaining_words = ' '.join(words[1:]) if len(words) > 1 else ''
                        message.content = f"{prefix}{first_word} {remaining_words}".strip()
        
        # Process emoji placeholders in message content
        if message.content and hasattr(self, 'emoji_handler'):
            message.content = self.emoji_handler.replace_emojis(message.content)
        
        # Process commands
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
        
        # Track command usage
        try:
            await self.db.increment_user_commands(ctx.author.id)
        except:
            pass
        
        await self.invoke(ctx)

async def main():
    bot = DravonBot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())