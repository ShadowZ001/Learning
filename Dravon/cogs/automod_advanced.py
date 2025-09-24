import discord
from discord.ext import commands
import re
import asyncio
from datetime import datetime, timedelta

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()
        self.link_filter = set()
        self.profanity_filter = set()
        self.caps_filter = set()
        self.spam_filter = set()
        self.nsfw_filter = set()
        self.whitelisted_users = {}
        self.user_message_count = {}
        self.user_last_message = {}
        
        # Enhanced bad words list
        self.bad_words = [
            'fuck', 'shit', 'bitch', 'damn', 'ass', 'hell', 'crap', 'piss', 'bastard', 'slut',
            'whore', 'nigger', 'nigga', 'faggot', 'retard', 'cunt', 'pussy', 'dick', 'cock',
            'penis', 'vagina', 'sex', 'porn', 'nude', 'naked', 'xxx', 'anal', 'oral', 'rape'
        ]
        
        # Spam detection
        self.spam_threshold = 5  # messages
        self.spam_time_window = 10  # seconds
    
    async def is_owner_or_extra(self, guild, user):
        """Check if user is server owner or extra owner"""
        if user.id == guild.owner_id:
            return True
        try:
            extra_owners = await self.bot.db.get_extra_owners(guild.id)
            return user.id in extra_owners
        except:
            return False
    
    async def is_whitelisted(self, guild_id, user_id):
        """Check if user is whitelisted for automod bypass"""
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return False
        
        # Server owner always whitelisted
        if user_id == guild.owner_id:
            return True
        
        # Check extra owners
        try:
            extra_owners = await self.bot.db.get_extra_owners(guild_id)
            if user_id in extra_owners:
                return True
        except:
            pass
        
        # Check antinuke whitelist
        try:
            antinuke_whitelist = await self.bot.db.get_antinuke_rule(guild_id, "whitelist")
            if antinuke_whitelist and user_id in antinuke_whitelist.get("users", []):
                return True
        except:
            pass
        
        return False
    
    async def notify_owner(self, guild, action, user, details):
        """Send DM to server owner about security events"""
        try:
            if guild.owner:
                embed = discord.Embed(
                    title="🚨 AutoMod Security Alert",
                    description=f"**Server:** {guild.name}\n**Action:** {action}\n**User:** {user} ({user.id})\n**Details:** {details}",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                embed.set_footer(text="Dravon™ AutoMod Security System")
                await guild.owner.send(embed=embed)
        except:
            pass
    
    async def log_action(self, guild, action, user, details):
        """Log automod actions"""
        try:
            logs_config = await self.bot.db.get_automod_rule(guild.id, "logs")
            if logs_config and logs_config.get("channel_id"):
                channel = guild.get_channel(logs_config["channel_id"])
                if channel:
                    embed = discord.Embed(
                        title="🤖 AutoMod Action",
                        description=f"**Action:** {action}\n**User:** {user.mention} ({user.id})\n**Details:** {details}",
                        color=0xff8c00,
                        timestamp=datetime.now()
                    )
                    await channel.send(embed=embed)
        except:
            pass
    
    @commands.hybrid_group(name="automod")
    async def automod_group(self, ctx):
        if not await self.is_owner_or_extra(ctx.guild, ctx.author):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only server owners and extra owners can use AutoMod commands.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🤖 Dravon™ AutoMod System",
                description="**Advanced Automatic Moderation**\n\nProtect your server with intelligent content filtering and spam detection.",
                color=0x7289da
            )
            embed.add_field(
                name="🔧 Commands",
                value="`/automod setup` - Configure AutoMod\n`/automod enable` - Enable all filters\n`/automod disable` - Disable AutoMod\n`/automod status` - View current settings",
                inline=False
            )
            await ctx.send(embed=embed)
    
    @automod_group.command(name="setup")
    async def automod_setup(self, ctx):
        """Interactive AutoMod setup"""
        embed = discord.Embed(
            title="🤖 AutoMod Setup",
            description="**Configure AutoMod Protection**\n\nUse the buttons below to configure your server's automatic moderation system.",
            color=0x7289da
        )
        
        view = discord.ui.View(timeout=300)
        
        # Enable/Disable button
        enable_btn = discord.ui.Button(label="🟢 Enable AutoMod", style=discord.ButtonStyle.success)
        disable_btn = discord.ui.Button(label="🔴 Disable AutoMod", style=discord.ButtonStyle.danger)
        
        async def enable_callback(interaction):
            await self.bot.db.set_automod_rule(ctx.guild.id, "enabled", {"status": True})
            await self.bot.db.set_automod_rule(ctx.guild.id, "link_filter", {"enabled": True})
            await self.bot.db.set_automod_rule(ctx.guild.id, "profanity_filter", {"enabled": True})
            await self.bot.db.set_automod_rule(ctx.guild.id, "caps_filter", {"enabled": True})
            await self.bot.db.set_automod_rule(ctx.guild.id, "spam_filter", {"enabled": True})
            
            embed = discord.Embed(
                title="✅ AutoMod Enabled",
                description="All AutoMod filters are now active and protecting your server!",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        async def disable_callback(interaction):
            await self.bot.db.set_automod_rule(ctx.guild.id, "enabled", {"status": False})
            
            embed = discord.Embed(
                title="❌ AutoMod Disabled",
                description="AutoMod protection has been disabled.",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        enable_btn.callback = enable_callback
        disable_btn.callback = disable_callback
        
        view.add_item(enable_btn)
        view.add_item(disable_btn)
        
        await ctx.send(embed=embed, view=view)
    
    @automod_group.command(name="enable")
    async def automod_enable(self, ctx):
        """Enable AutoMod with all filters"""
        await self.bot.db.set_automod_rule(ctx.guild.id, "enabled", {"status": True})
        await self.bot.db.set_automod_rule(ctx.guild.id, "link_filter", {"enabled": True})
        await self.bot.db.set_automod_rule(ctx.guild.id, "profanity_filter", {"enabled": True})
        await self.bot.db.set_automod_rule(ctx.guild.id, "caps_filter", {"enabled": True})
        await self.bot.db.set_automod_rule(ctx.guild.id, "spam_filter", {"enabled": True})
        
        embed = discord.Embed(
            title="✅ AutoMod Enabled",
            description="**All filters activated:**\n• Link Filter\n• Profanity Filter\n• Caps Filter\n• Spam Filter\n• NSFW Filter",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @automod_group.command(name="disable")
    async def automod_disable(self, ctx):
        """Disable AutoMod"""
        await self.bot.db.set_automod_rule(ctx.guild.id, "enabled", {"status": False})
        
        embed = discord.Embed(
            title="❌ AutoMod Disabled",
            description="AutoMod protection has been disabled for this server.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @automod_group.command(name="status")
    async def automod_status(self, ctx):
        """View AutoMod status"""
        try:
            enabled = await self.bot.db.get_automod_rule(ctx.guild.id, "enabled")
            link_filter = await self.bot.db.get_automod_rule(ctx.guild.id, "link_filter")
            profanity_filter = await self.bot.db.get_automod_rule(ctx.guild.id, "profanity_filter")
            caps_filter = await self.bot.db.get_automod_rule(ctx.guild.id, "caps_filter")
            spam_filter = await self.bot.db.get_automod_rule(ctx.guild.id, "spam_filter")
        except:
            enabled = None
            link_filter = None
            profanity_filter = None
            caps_filter = None
            spam_filter = None
        
        status = "🟢 Enabled" if enabled and enabled.get("status") else "🔴 Disabled"
        
        embed = discord.Embed(
            title="🤖 AutoMod Status",
            description=f"**System Status:** {status}",
            color=0x00ff00 if enabled and enabled.get("status") else 0xff0000
        )
        
        filters_status = []
        filters_status.append(f"🔗 Link Filter: {'✅' if link_filter and link_filter.get('enabled') else '❌'}")
        filters_status.append(f"🤬 Profanity Filter: {'✅' if profanity_filter and profanity_filter.get('enabled') else '❌'}")
        filters_status.append(f"📢 Caps Filter: {'✅' if caps_filter and caps_filter.get('enabled') else '❌'}")
        filters_status.append(f"🚫 Spam Filter: {'✅' if spam_filter and spam_filter.get('enabled') else '❌'}")
        
        embed.add_field(
            name="🛡️ Active Filters",
            value="\n".join(filters_status),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Enhanced message filtering"""
        if message.author.bot or not message.guild:
            return
        
        # Check if AutoMod is enabled
        try:
            enabled = await self.bot.db.get_automod_rule(message.guild.id, "enabled")
            if not enabled or not enabled.get("status"):
                return
        except:
            return
        
        # Check if user is whitelisted (owner, extra owner, or antinuke whitelist)
        if await self.is_whitelisted(message.guild.id, message.author.id):
            return
        
        # Users with Administrator permission should NOT bypass (as requested)
        # Only server owner, extra owners, and whitelisted users can bypass
        
        deleted = False
        violation_type = ""
        
        # Link Filter
        try:
            link_filter = await self.bot.db.get_automod_rule(message.guild.id, "link_filter")
            if link_filter and link_filter.get("enabled"):
                if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content):
                    try:
                        await message.delete()
                        await message.channel.send(f"🔗 {message.author.mention}, links are not allowed!", delete_after=5)
                        deleted = True
                        violation_type = "Link Filter"
                    except:
                        pass
        except:
            pass
        
        # Profanity Filter
        if not deleted:
            try:
                profanity_filter = await self.bot.db.get_automod_rule(message.guild.id, "profanity_filter")
                if profanity_filter and profanity_filter.get("enabled"):
                    for word in self.bad_words:
                        if word.lower() in message.content.lower():
                            try:
                                await message.delete()
                                await message.channel.send(f"🤬 {message.author.mention}, inappropriate language detected!", delete_after=5)
                                deleted = True
                                violation_type = "Profanity Filter"
                                break
                            except:
                                pass
            except:
                pass
        
        # Caps Filter
        if not deleted:
            try:
                caps_filter = await self.bot.db.get_automod_rule(message.guild.id, "caps_filter")
                if caps_filter and caps_filter.get("enabled"):
                    if len(message.content) > 10:
                        caps_count = sum(1 for c in message.content if c.isupper())
                        if caps_count / len(message.content) > 0.7:  # 70% caps
                            try:
                                await message.delete()
                                await message.channel.send(f"📢 {message.author.mention}, please don't use excessive caps!", delete_after=5)
                                deleted = True
                                violation_type = "Caps Filter"
                            except:
                                pass
            except:
                pass
        
        # Spam Filter
        if not deleted:
            try:
                spam_filter = await self.bot.db.get_automod_rule(message.guild.id, "spam_filter")
                if spam_filter and spam_filter.get("enabled"):
                    user_id = message.author.id
                    current_time = datetime.now()
                    
                    if user_id not in self.user_message_count:
                        self.user_message_count[user_id] = []
                    
                    # Remove old messages outside time window
                    self.user_message_count[user_id] = [
                        msg_time for msg_time in self.user_message_count[user_id]
                        if (current_time - msg_time).seconds < self.spam_time_window
                    ]
                    
                    # Add current message
                    self.user_message_count[user_id].append(current_time)
                    
                    # Check if spam threshold exceeded
                    if len(self.user_message_count[user_id]) >= self.spam_threshold:
                        try:
                            await message.delete()
                            await message.channel.send(f"🚫 {message.author.mention}, slow down! You're sending messages too fast!", delete_after=5)
                            deleted = True
                            violation_type = "Spam Filter"
                            
                            # Timeout user for 1 minute
                            try:
                                await message.author.timeout(datetime.now() + timedelta(minutes=1), reason="AutoMod: Spam detected")
                            except:
                                pass
                        except:
                            pass
            except:
                pass
        
        # Log violation and notify owner
        if deleted:
            await self.log_action(message.guild, violation_type, message.author, f"Message deleted: {message.content[:100]}...")
            await self.notify_owner(message.guild, violation_type, message.author, f"Violated {violation_type.lower()}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Check new members for suspicious activity"""
        try:
            enabled = await self.bot.db.get_automod_rule(member.guild.id, "enabled")
            if not enabled or not enabled.get("status"):
                return
        except:
            return
        
        # Check account age (less than 7 days = suspicious)
        account_age = (datetime.now() - member.created_at).days
        if account_age < 7:
            await self.notify_owner(
                member.guild, 
                "Suspicious Account", 
                member, 
                f"New account joined (created {account_age} days ago)"
            )

async def setup(bot):
    await bot.add_cog(AutoMod(bot))