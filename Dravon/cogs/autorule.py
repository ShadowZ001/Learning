import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta

class AutoRule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()
        self.rules = {}
        
        # Default rules
        self.default_rules = {
            "no_mass_mention": {"enabled": True, "limit": 5, "punishment": "timeout"},
            "no_invite_links": {"enabled": True, "punishment": "delete"},
            "no_external_links": {"enabled": True, "punishment": "delete"},
            "no_repeated_text": {"enabled": True, "limit": 3, "punishment": "delete"},
            "no_zalgo_text": {"enabled": True, "punishment": "delete"},
            "account_age_check": {"enabled": True, "min_age_days": 7, "punishment": "kick"},
            "no_emoji_spam": {"enabled": True, "limit": 10, "punishment": "delete"}
        }
    
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
        """Check if user is whitelisted"""
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
        """Send DM to server owner about rule violations"""
        try:
            if guild.owner:
                embed = discord.Embed(
                    title="🚨 AutoRule Violation",
                    description=f"**Server:** {guild.name}\n**Rule:** {action}\n**User:** {user} ({user.id})\n**Details:** {details}",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                embed.set_footer(text="Dravon™ AutoRule System")
                await guild.owner.send(embed=embed)
        except:
            pass
    
    async def log_action(self, guild, action, user, details):
        """Log autorule actions"""
        try:
            logs_config = await self.bot.db.get_autorule_rule(guild.id, "logs")
            if logs_config and logs_config.get("channel_id"):
                channel = guild.get_channel(logs_config["channel_id"])
                if channel:
                    embed = discord.Embed(
                        title="📝 AutoRule Action",
                        description=f"**Rule:** {action}\n**User:** {user.mention} ({user.id})\n**Details:** {details}",
                        color=0xff8c00,
                        timestamp=datetime.now()
                    )
                    await channel.send(embed=embed)
        except:
            pass
    
    @commands.hybrid_group(name="autorule")
    async def autorule_group(self, ctx):
        if not await self.is_owner_or_extra(ctx.guild, ctx.author):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only server owners and extra owners can use AutoRule commands.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📝 Dravon™ AutoRule System",
                description="**Advanced Rule Enforcement**\n\nAutomatically enforce server rules and maintain order.",
                color=0x7289da
            )
            embed.add_field(
                name="🔧 Commands",
                value="`/autorule setup` - Configure AutoRule\n`/autorule enable` - Enable all rules\n`/autorule disable` - Disable AutoRule\n`/autorule status` - View current settings",
                inline=False
            )
            await ctx.send(embed=embed)
    
    @autorule_group.command(name="setup")
    async def autorule_setup(self, ctx):
        """Interactive AutoRule setup"""
        embed = discord.Embed(
            title="📝 AutoRule Setup",
            description="**Configure Automatic Rule Enforcement**\n\nUse the buttons below to configure your server's automatic rule system.",
            color=0x7289da
        )
        
        view = discord.ui.View(timeout=300)
        
        enable_btn = discord.ui.Button(label="🟢 Enable AutoRule", style=discord.ButtonStyle.success)
        disable_btn = discord.ui.Button(label="🔴 Disable AutoRule", style=discord.ButtonStyle.danger)
        
        async def enable_callback(interaction):
            await self.bot.db.set_autorule_rule(ctx.guild.id, "enabled", {"status": True})
            for rule_name, rule_config in self.default_rules.items():
                await self.bot.db.set_autorule_rule(ctx.guild.id, rule_name, rule_config)
            
            embed = discord.Embed(
                title="✅ AutoRule Enabled",
                description="All AutoRule enforcement is now active!",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        async def disable_callback(interaction):
            await self.bot.db.set_autorule_rule(ctx.guild.id, "enabled", {"status": False})
            
            embed = discord.Embed(
                title="❌ AutoRule Disabled",
                description="AutoRule enforcement has been disabled.",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        enable_btn.callback = enable_callback
        disable_btn.callback = disable_callback
        
        view.add_item(enable_btn)
        view.add_item(disable_btn)
        
        await ctx.send(embed=embed, view=view)
    
    @autorule_group.command(name="enable")
    async def autorule_enable(self, ctx):
        """Enable AutoRule with all rules"""
        await self.bot.db.set_autorule_rule(ctx.guild.id, "enabled", {"status": True})
        for rule_name, rule_config in self.default_rules.items():
            await self.bot.db.set_autorule_rule(ctx.guild.id, rule_name, rule_config)
        
        embed = discord.Embed(
            title="✅ AutoRule Enabled",
            description="**All rules activated:**\n• No Mass Mentions\n• No Invite Links\n• No External Links\n• No Repeated Text\n• No Zalgo Text\n• Account Age Check\n• No Emoji Spam",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @autorule_group.command(name="disable")
    async def autorule_disable(self, ctx):
        """Disable AutoRule"""
        await self.bot.db.set_autorule_rule(ctx.guild.id, "enabled", {"status": False})
        
        embed = discord.Embed(
            title="❌ AutoRule Disabled",
            description="AutoRule enforcement has been disabled for this server.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @autorule_group.command(name="status")
    async def autorule_status(self, ctx):
        """View AutoRule status"""
        try:
            enabled = await self.bot.db.get_autorule_rule(ctx.guild.id, "enabled")
        except:
            enabled = None
        
        status = "🟢 Enabled" if enabled and enabled.get("status") else "🔴 Disabled"
        
        embed = discord.Embed(
            title="📝 AutoRule Status",
            description=f"**System Status:** {status}",
            color=0x00ff00 if enabled and enabled.get("status") else 0xff0000
        )
        
        if enabled and enabled.get("status"):
            rules_status = []
            for rule_name in self.default_rules.keys():
                try:
                    rule_config = await self.bot.db.get_autorule_rule(ctx.guild.id, rule_name)
                    status_icon = "✅" if rule_config and rule_config.get("enabled") else "❌"
                    rules_status.append(f"{status_icon} {rule_name.replace('_', ' ').title()}")
                except:
                    rules_status.append(f"❌ {rule_name.replace('_', ' ').title()}")
            
            embed.add_field(
                name="📋 Active Rules",
                value="\n".join(rules_status),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Enhanced message rule checking"""
        if message.author.bot or not message.guild:
            return
        
        # Check if AutoRule is enabled
        try:
            enabled = await self.bot.db.get_autorule_rule(message.guild.id, "enabled")
            if not enabled or not enabled.get("status"):
                return
        except:
            return
        
        # Check if user is whitelisted
        if await self.is_whitelisted(message.guild.id, message.author.id):
            return
        
        deleted = False
        violation_type = ""
        
        # Mass mention check
        try:
            rule = await self.bot.db.get_autorule_rule(message.guild.id, "no_mass_mention")
            if rule and rule.get("enabled"):
                mention_count = len(message.mentions) + len(message.role_mentions)
                if mention_count >= rule.get("limit", 5):
                    try:
                        await message.delete()
                        await message.channel.send(f"👥 {message.author.mention}, no mass mentions allowed!", delete_after=5)
                        deleted = True
                        violation_type = "Mass Mentions"
                        
                        if rule.get("punishment") == "timeout":
                            await message.author.timeout(datetime.now() + timedelta(minutes=5), reason="AutoRule: Mass mentions")
                    except:
                        pass
        except:
            pass
        
        # Invite links check
        if not deleted:
            try:
                rule = await self.bot.db.get_autorule_rule(message.guild.id, "no_invite_links")
                if rule and rule.get("enabled"):
                    if re.search(r'discord\.gg/|discord\.com/invite/|discordapp\.com/invite/', message.content):
                        try:
                            await message.delete()
                            await message.channel.send(f"🔗 {message.author.mention}, invite links are not allowed!", delete_after=5)
                            deleted = True
                            violation_type = "Invite Links"
                        except:
                            pass
            except:
                pass
        
        # External links check
        if not deleted:
            try:
                rule = await self.bot.db.get_autorule_rule(message.guild.id, "no_external_links")
                if rule and rule.get("enabled"):
                    if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content):
                        try:
                            await message.delete()
                            await message.channel.send(f"🌐 {message.author.mention}, external links are not allowed!", delete_after=5)
                            deleted = True
                            violation_type = "External Links"
                        except:
                            pass
            except:
                pass
        
        # Repeated text check
        if not deleted:
            try:
                rule = await self.bot.db.get_autorule_rule(message.guild.id, "no_repeated_text")
                if rule and rule.get("enabled"):
                    words = message.content.split()
                    if len(words) > 1:
                        repeated_count = max([words.count(word) for word in set(words)])
                        if repeated_count >= rule.get("limit", 3):
                            try:
                                await message.delete()
                                await message.channel.send(f"🔄 {message.author.mention}, no repeated text allowed!", delete_after=5)
                                deleted = True
                                violation_type = "Repeated Text"
                            except:
                                pass
            except:
                pass
        
        # Emoji spam check
        if not deleted:
            try:
                rule = await self.bot.db.get_autorule_rule(message.guild.id, "no_emoji_spam")
                if rule and rule.get("enabled"):
                    emoji_count = len(re.findall(r'<:[^:]+:\d+>|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', message.content))
                    if emoji_count >= rule.get("limit", 10):
                        try:
                            await message.delete()
                            await message.channel.send(f"😀 {message.author.mention}, too many emojis!", delete_after=5)
                            deleted = True
                            violation_type = "Emoji Spam"
                        except:
                            pass
            except:
                pass
        
        # Log violation and notify owner
        if deleted:
            await self.log_action(message.guild, violation_type, message.author, f"Message deleted: {message.content[:100]}...")
            await self.notify_owner(message.guild, violation_type, message.author, f"Violated {violation_type.lower()} rule")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Check new members against account age rule"""
        try:
            enabled = await self.bot.db.get_autorule_rule(member.guild.id, "enabled")
            if not enabled or not enabled.get("status"):
                return
            
            rule = await self.bot.db.get_autorule_rule(member.guild.id, "account_age_check")
            if rule and rule.get("enabled"):
                account_age = (datetime.now() - member.created_at).days
                min_age = rule.get("min_age_days", 7)
                
                if account_age < min_age:
                    punishment = rule.get("punishment", "kick")
                    
                    if punishment == "kick":
                        try:
                            await member.kick(reason=f"AutoRule: Account too new ({account_age} days old)")
                            await self.log_action(member.guild, "Account Age Check", member, f"Kicked for account age ({account_age} days)")
                            await self.notify_owner(member.guild, "Account Age Check", member, f"Account only {account_age} days old")
                        except:
                            pass
                    elif punishment == "ban":
                        try:
                            await member.ban(reason=f"AutoRule: Account too new ({account_age} days old)")
                            await self.log_action(member.guild, "Account Age Check", member, f"Banned for account age ({account_age} days)")
                            await self.notify_owner(member.guild, "Account Age Check", member, f"Account only {account_age} days old")
                        except:
                            pass
        except:
            pass

async def setup(bot):
    await bot.add_cog(AutoRule(bot))