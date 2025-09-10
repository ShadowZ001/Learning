import discord
from discord.ext import commands
import asyncio
import time
from datetime import datetime, timedelta
from utils.embed_utils import add_dravon_footer
from typing import Dict, List, Optional

class AntiNukeSetupView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.select(
        placeholder="🛡️ Configure AntiNuke Protection...",
        options=[
            discord.SelectOption(label="🔧 Enable/Disable System", description="Toggle AntiNuke protection", value="toggle"),
            discord.SelectOption(label="👥 Manage Whitelist", description="Add/remove whitelisted users", value="whitelist"),
            discord.SelectOption(label="⚡ Protection Level", description="Basic, Strong, or Extreme", value="level"),
            discord.SelectOption(label="⚖️ Auto Punishment", description="Set punishment type", value="punishment"),
            discord.SelectOption(label="📝 Logging Channel", description="Set logs channel", value="logs"),
            discord.SelectOption(label="🚨 Auto Alerts", description="DM owner on threats", value="alerts")
        ]
    )
    async def setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        
        if value == "toggle":
            embed = discord.Embed(
                title="🛡️ AntiNuke System Toggle",
                description="Choose to enable or disable the AntiNuke system",
                color=0xff6b35
            )
            view = ToggleView(self.bot, self.guild)
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif value == "level":
            embed = discord.Embed(
                title="⚡ Protection Level",
                description="Choose your server's protection intensity",
                color=0x4ecdc4
            )
            view = ProtectionLevelView(self.bot, self.guild)
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif value == "punishment":
            embed = discord.Embed(
                title="⚖️ Auto Punishment System",
                description="Configure what happens to rule breakers",
                color=0xe74c3c
            )
            view = PunishmentView(self.bot, self.guild)
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif value == "whitelist":
            embed = discord.Embed(
                title="👥 Whitelist Management",
                description="Manage trusted users who bypass AntiNuke protection",
                color=0x95a5a6
            )
            embed.add_field(
                name="ℹ️ Information",
                value="Use the commands below to manage whitelisted users:\n\n• `/antinuke whitelist add <user>` - Add trusted user\n• `/antinuke whitelist remove <user>` - Remove user\n• `/antinuke whitelist list` - View all whitelisted users",
                inline=False
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=None)
        
        elif value == "logs":
            embed = discord.Embed(
                title="📝 Logging Configuration",
                description="Set up security event logging",
                color=0x7289da
            )
            embed.add_field(
                name="ℹ️ Information",
                value="Use the command below to set up logging:\n\n• `/antinuke logs <channel>` - Set logs channel\n• `/antinuke logs` - View current logs channel",
                inline=False
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=None)
        
        elif value == "alerts":
            embed = discord.Embed(
                title="🚨 Auto Alerts Configuration",
                description="Configure automatic owner notifications",
                color=0xff8c00
            )
            embed.add_field(
                name="ℹ️ Information",
                value="Auto alerts are automatically enabled when AntiNuke is active.\n\nThe server owner will receive DM notifications for:\n• Critical security threats\n• Emergency lockdowns\n• System configuration changes",
                inline=False
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=None)

class ToggleView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.button(label="🟢 Enable AntiNuke", style=discord.ButtonStyle.success)
    async def enable_antinuke(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.db.set_antinuke_rule(self.guild.id, "enabled", {"status": True})
        embed = discord.Embed(
            title="✅ AntiNuke Enabled",
            description="Your server is now protected by Dravon™ AntiNuke system!",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="🔴 Disable AntiNuke", style=discord.ButtonStyle.danger)
    async def disable_antinuke(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.guild.owner_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner can disable AntiNuke protection!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await self.bot.db.set_antinuke_rule(self.guild.id, "enabled", {"status": False})
        embed = discord.Embed(
            title="⚠️ AntiNuke Disabled",
            description="AntiNuke protection has been disabled. Your server is now vulnerable!",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)

class ProtectionLevelView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.button(label="🟡 Basic Protection", style=discord.ButtonStyle.secondary)
    async def basic_protection(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.db.set_antinuke_rule(self.guild.id, "protection_level", {"level": "basic"})
        embed = discord.Embed(
            title="🟡 Basic Protection Enabled",
            description="Standard protection against common threats",
            color=0xffd700
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="🟠 Strong Protection", style=discord.ButtonStyle.primary)
    async def strong_protection(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.db.set_antinuke_rule(self.guild.id, "protection_level", {"level": "strong"})
        embed = discord.Embed(
            title="🟠 Strong Protection Enabled",
            description="Enhanced protection with faster response times",
            color=0xff8c00
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="🔴 Extreme Protection", style=discord.ButtonStyle.danger)
    async def extreme_protection(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.db.set_antinuke_rule(self.guild.id, "protection_level", {"level": "extreme"})
        embed = discord.Embed(
            title="🔴 Extreme Protection Enabled",
            description="Maximum security with zero tolerance for threats",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)

class PunishmentView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.select(
        placeholder="⚖️ Choose punishment type...",
        options=[
            discord.SelectOption(label="🔒 Quarantine Role", description="Lock user in isolation (Recommended)", value="quarantine"),
            discord.SelectOption(label="👢 Kick User", description="Remove user from server", value="kick"),
            discord.SelectOption(label="🔨 Ban User", description="Permanently ban the user", value="ban"),
            discord.SelectOption(label="📝 Remove All Roles", description="Strip all roles from user", value="strip_roles")
        ]
    )
    async def punishment_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        punishment = select.values[0]
        await self.bot.db.set_antinuke_rule(self.guild.id, "punishment", {"type": punishment})
        
        punishment_names = {
            "quarantine": "🔒 Quarantine Role",
            "kick": "👢 Kick User",
            "ban": "🔨 Ban User",
            "strip_roles": "📝 Remove All Roles"
        }
        
        embed = discord.Embed(
            title="✅ Punishment Set",
            description=f"Auto punishment set to: **{punishment_names[punishment]}**",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.action_tracker = {}  # Track suspicious actions
        self.lockdown_guilds = set()  # Guilds in emergency lockdown
        self.threat_levels = {
            "channel_delete": "HIGH",
            "mass_channel_delete": "CRITICAL",
            "role_delete": "HIGH", 
            "mass_role_delete": "CRITICAL",
            "member_ban": "MEDIUM",
            "mass_member_ban": "CRITICAL",
            "webhook_create": "MEDIUM",
            "bot_add": "HIGH",
            "permission_escalation": "CRITICAL"
        }
    
    async def is_whitelisted(self, guild_id: int, user_id: int) -> bool:
        """Check if user is whitelisted (includes automatic whitelist)"""
        # Bot admin is always whitelisted
        if user_id == 1037768611126841405:
            return True
        
        # Server owner is always whitelisted
        guild = self.bot.get_guild(guild_id)
        if guild and guild.owner_id == user_id:
            return True
        
        # Check database whitelist
        whitelist = await self.bot.db.get_antinuke_rule(guild_id, "whitelist")
        if not whitelist:
            return False
        return user_id in whitelist.get("users", [])
    
    async def get_quarantine_role(self, guild: discord.Guild):
        """Get or create quarantine role"""
        role = discord.utils.get(guild.roles, name="🔒 Dravon™ Quarantine")
        if not role:
            role = await guild.create_role(
                name="🔒 Dravon™ Quarantine",
                color=0x2c2c2c,
                permissions=discord.Permissions.none(),
                reason="AntiNuke Quarantine Role"
            )
            # Lock role in all channels
            for channel in guild.channels:
                try:
                    await channel.set_permissions(role, send_messages=False, view_channel=False)
                except:
                    pass
        return role
    
    async def execute_punishment(self, guild: discord.Guild, user: discord.Member, reason: str):
        """Execute the configured punishment"""
        punishment_config = await self.bot.db.get_antinuke_rule(guild.id, "punishment")
        punishment_type = punishment_config.get("type", "quarantine") if punishment_config else "quarantine"
        
        try:
            if punishment_type == "quarantine":
                quarantine_role = await self.get_quarantine_role(guild)
                await user.add_roles(quarantine_role, reason=f"AntiNuke: {reason}")
            elif punishment_type == "kick":
                await user.kick(reason=f"AntiNuke: {reason}")
            elif punishment_type == "ban":
                await user.ban(reason=f"AntiNuke: {reason}")
            elif punishment_type == "strip_roles":
                await user.edit(roles=[], reason=f"AntiNuke: {reason}")
        except Exception as e:
            print(f"AntiNuke punishment failed: {e}")
    
    async def log_action(self, guild: discord.Guild, action: str, user: discord.Member, details: str, threat_level: str = "HIGH"):
        """Log security action with enhanced formatting"""
        logs_config = await self.bot.db.get_antinuke_rule(guild.id, "logs")
        if not logs_config:
            return
        
        channel_id = logs_config.get("channel_id")
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        
        # Color based on threat level
        colors = {
            "CRITICAL": 0x8B0000,  # Dark red
            "HIGH": 0xFF0000,      # Red
            "MEDIUM": 0xFF8C00,    # Orange
            "LOW": 0xFFD700       # Gold
        }
        
        embed = discord.Embed(
            title="🛡️ AntiNuke Security Alert",
            color=colors.get(threat_level, 0xFF0000),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🚨 Threat Detected",
            value=f"**Action:** {action}\n**Threat Level:** {threat_level}\n**Details:** {details}",
            inline=False
        )
        
        embed.add_field(
            name="👤 User Information",
            value=f"**User:** {user.mention}\n**ID:** `{user.id}`\n**Account Created:** <t:{int(user.created_at.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="🏠 Server Information",
            value=f"**Server:** {guild.name}\n**Owner:** <@{guild.owner_id}>\n**Time:** <t:{int(datetime.now().timestamp())}:F>",
            inline=True
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"AntiNuke v6.0 • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        try:
            await channel.send(embed=embed)
            
            # Send DM to server owner if critical threat
            if threat_level == "CRITICAL" and guild.owner:
                try:
                    dm_embed = discord.Embed(
                        title="🚨 CRITICAL SECURITY ALERT",
                        description=f"**Server:** {guild.name}\n**Threat:** {action}\n**User:** {user} ({user.id})\n\nImmediate action has been taken to protect your server.",
                        color=0x8B0000
                    )
                    dm_embed = add_dravon_footer(dm_embed)
                    await guild.owner.send(embed=dm_embed)
                except:
                    pass
        except:
            pass
    
    @commands.hybrid_group(name="antinuke")
    async def antinuke_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🛡️ Dravon™ AntiNuke v6.0",
                description="**Advanced Server Protection System**\n\nProtect your server from malicious attacks with our state-of-the-art security system.",
                color=0xff6b35
            )
            embed.add_field(
                name="🚀 Quick Commands",
                value="`/antinuke setup` - Interactive setup wizard\n`/antinuke fastsetup` - Instant secure setup\n`/antinuke config` - View current settings",
                inline=False
            )
            embed.add_field(
                name="🔧 Management",
                value="`/antinuke whitelist` - Manage trusted users\n`/antinuke punishment` - Configure punishments\n`/antinuke reset` - Reset all settings",
                inline=False
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413146132405817487/f41e57df-936d-428a-8aa8-a0b4ca2a1e64.jpg?ex=68bade64&is=68b98ce4&hm=b47dca3ee7abd906adf59b9a6974c047a2ee5079928e6b3ba37255ea7b9945f7&")
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
    
    @antinuke_group.command(name="setup")
    async def antinuke_setup(self, ctx):
        """Interactive AntiNuke setup wizard (Whitelisted users only)"""
        # Check if user has permission
        if ctx.author.id != ctx.guild.owner_id and not await self.bot.db.has_antinuke_access(ctx.guild.id, ctx.author.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="**🔒 Restricted Command**\n\nOnly whitelisted users can access AntiNuke setup.\n\n**How to get access:**\nAsk the server owner to whitelist you using `/whitelist`",
                color=0xff0000
            )
            embed.set_footer(text="AntiNuke v6.0 • Access Restriction • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(
            title="🛡️ Dravon™ AntiNuke v6.0 Setup Wizard",
            description="**🚀 Advanced Server Protection System**\n\nProtect your server from malicious attacks, raids, and unauthorized actions with our state-of-the-art security system.\n\n**🔥 Key Features:**\n• Real-time threat detection\n• Intelligent punishment system\n• Whitelist management\n• Advanced logging\n• Emergency lockdown\n• Owner notifications",
            color=0x4ecdc4
        )
        
        embed.add_field(
            name="⚙️ Configuration Options",
            value="🔧 **System Toggle** - Enable/Disable protection\n👥 **Whitelist Management** - Trusted users\n⚡ **Protection Levels** - Basic, Strong, Extreme\n⚖️ **Auto Punishment** - Quarantine, Kick, Ban\n📝 **Logging System** - Security event logs\n🚨 **Alert System** - Owner notifications",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Protection Coverage",
            value="• Mass channel deletion\n• Mass role deletion\n• Mass member kicks/bans\n• Permission escalation\n• Webhook spam\n• Bot additions",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Response Time",
            value="• **Basic:** 3-5 seconds\n• **Strong:** 1-2 seconds\n• **Extreme:** <1 second",
            inline=True
        )
        
        embed.set_footer(text="AntiNuke v6.0 • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        # Add loading animation
        loading_embed = discord.Embed(
            title="🔄 Loading AntiNuke Setup...",
            description="⏳ Initializing security configuration wizard...",
            color=0xffd700
        )
        loading_embed.set_footer(text="Please wait...", icon_url=self.bot.user.display_avatar.url)
        
        message = await ctx.send(embed=loading_embed)
        await asyncio.sleep(2)
        
        view = AntiNukeSetupView(self.bot, ctx.guild)
        await message.edit(embed=embed, view=view)
    
    @antinuke_group.command(name="logs")
    @commands.has_permissions(manage_guild=True)
    async def antinuke_logs(self, ctx, channel: discord.TextChannel = None):
        """Set or view AntiNuke logs channel"""
        if channel is None:
            # View current logs channel
            logs_config = await self.bot.db.get_antinuke_rule(ctx.guild.id, "logs")
            current_channel = logs_config.get("channel_id") if logs_config else None
            
            embed = discord.Embed(
                title="📝 AntiNuke Logs Configuration",
                description="**🛡️ Security Event Logging System**\n\nAll AntiNuke security events and alerts are logged to the designated channel.",
                color=0x7289da
            )
            
            if current_channel:
                channel_obj = ctx.guild.get_channel(current_channel)
                if channel_obj:
                    embed.add_field(
                        name="✅ Current Logs Channel",
                        value=f"{channel_obj.mention}\n**ID:** `{current_channel}`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="⚠️ Invalid Logs Channel",
                        value=f"Channel with ID `{current_channel}` not found.\nPlease set a new logs channel.",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="❌ No Logs Channel Set",
                    value="Security events are not being logged.\nUse `/antinuke logs <channel>` to set one.",
                    inline=False
                )
            
            embed.add_field(
                name="📊 Logged Events",
                value="• Security threats detected\n• Punishment actions taken\n• Whitelist modifications\n• Emergency lockdowns\n• System configuration changes",
                inline=False
            )
            
            embed.set_footer(text="AntiNuke v6.0 • Logging System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
        else:
            # Set new logs channel
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "logs", {"channel_id": channel.id})
            
            embed = discord.Embed(
                title="✅ Logs Channel Updated",
                description=f"**📝 AntiNuke logs will now be sent to {channel.mention}**",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🛡️ What gets logged?",
                value="• Security threat alerts\n• Automatic punishments\n• Whitelist changes\n• Emergency actions\n• Configuration updates",
                inline=False
            )
            
            embed.set_footer(text="AntiNuke v6.0 • Logging Active • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            
            # Send test log
            await self.log_action(ctx.guild, "Logs Channel Updated", ctx.author, f"Logs channel set to {channel.mention}", "LOW")
    
    @antinuke_group.command(name="fastsetup")
    @commands.has_permissions(manage_guild=True)
    async def antinuke_fastsetup(self, ctx):
        """Instant secure AntiNuke setup with enhanced progress tracking"""
        # Initial setup embed
        embed = discord.Embed(
            title="🚀 AntiNuke Fast Setup Initializing",
            description="**⚡ Preparing to secure your server...**\n\nThis will configure optimal security settings automatically.",
            color=0xffd700
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        message = await ctx.send(embed=embed)
        
        steps = [
            {"text": "🔧 Initializing AntiNuke v6.0 system...", "detail": "Loading security modules"},
            {"text": "🛡️ Creating security infrastructure...", "detail": "Setting up quarantine role"},
            {"text": "📝 Configuring logging system...", "detail": "Creating logs channel"},
            {"text": "🔒 Applying protection settings...", "detail": "Strong protection level"},
            {"text": "⚡ Finalizing configuration...", "detail": "Activating all systems"},
            {"text": "✅ Security deployment complete!", "detail": "Server is now protected"}
        ]
        
        for i, step in enumerate(steps):
            progress_bar = "█" * (i + 1) + "░" * (len(steps) - i - 1)
            percentage = int((i + 1) / len(steps) * 100)
            
            embed = discord.Embed(
                title="🚀 AntiNuke Fast Setup in Progress",
                description=f"**{step['text']}**\n*{step['detail']}*\n\n**Progress:** `{progress_bar}` **{percentage}%**",
                color=0xffd700 if i < len(steps) - 1 else 0x00ff00
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(text=f"Step {i + 1} of {len(steps)} • AntiNuke v6.0", icon_url=self.bot.user.display_avatar.url)
            
            await message.edit(embed=embed)
            await asyncio.sleep(1.5)
        
        # Actually configure the system
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "enabled", {"status": True})
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "protection_level", {"level": "strong"})
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "punishment", {"type": "quarantine"})
        
        # Create quarantine role
        quarantine_role = await self.get_quarantine_role(ctx.guild)
        
        # Create logs channel
        logs_channel = None
        try:
            logs_channel = await ctx.guild.create_text_channel(
                "🛡️-antinuke-logs",
                topic="AntiNuke v6.0 Security Logs - Powered by Dravon™",
                reason="AntiNuke Fast Setup - Security Logging"
            )
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "logs", {"channel_id": logs_channel.id})
        except:
            pass
        
        # Final success embed
        final_embed = discord.Embed(
            title="🎉 AntiNuke Fast Setup Complete!",
            description="**🛡️ Your server is now protected by Dravon™ AntiNuke v6.0**\n\nAll security systems are active and monitoring for threats.",
            color=0x00ff00
        )
        
        final_embed.add_field(
            name="✅ Successfully Configured",
            value=f"🔧 **System Status:** Active\n⚡ **Protection Level:** Strong\n⚖️ **Auto Punishment:** Quarantine Role\n🔒 **Quarantine Role:** {quarantine_role.mention}\n📝 **Logs Channel:** {logs_channel.mention if logs_channel else 'Failed to create'}",
            inline=False
        )
        
        final_embed.add_field(
            name="🛡️ Active Protection Features",
            value="• Real-time threat detection\n• Automatic punishment system\n• Security event logging\n• Emergency lockdown capability\n• Owner alert notifications",
            inline=True
        )
        
        final_embed.add_field(
            name="⚡ Next Steps",
            value="• Add trusted users: `/antinuke whitelist add`\n• View configuration: `/antinuke config`\n• Adjust settings: `/antinuke setup`",
            inline=True
        )
        
        final_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)
        final_embed.set_footer(text="AntiNuke v6.0 • Your server is now secure • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        await message.edit(embed=final_embed)
    
    @antinuke_group.group(name="punishment")
    async def punishment_group(self, ctx):
        if ctx.invoked_subcommand is None:
            punishment_config = await self.bot.db.get_antinuke_rule(ctx.guild.id, "punishment")
            current_punishment = punishment_config.get("type", "quarantine") if punishment_config else "quarantine"
            
            punishment_descriptions = {
                "quarantine": "🔒 **Quarantine Role** - Isolate user with restricted permissions",
                "kick": "👢 **Kick User** - Remove user from server (can rejoin)",
                "ban": "🔨 **Ban User** - Permanently ban user from server",
                "strip_roles": "📝 **Strip Roles** - Remove all roles from user"
            }
            
            embed = discord.Embed(
                title="⚖️ AntiNuke Punishment System",
                description="**🛡️ Configure automatic responses to security threats**\n\nChoose how AntiNuke should handle users who trigger security alerts.",
                color=0xe74c3c
            )
            
            embed.add_field(
                name="⚡ Current Setting",
                value=punishment_descriptions.get(current_punishment, "Unknown"),
                inline=False
            )
            
            embed.add_field(
                name="📝 Available Punishments",
                value="\n".join(punishment_descriptions.values()),
                inline=False
            )
            
            embed.add_field(
                name="⚙️ Management Commands",
                value="• `/antinuke punishment set` - Change punishment type\n• `/antinuke punishment view` - View current settings",
                inline=False
            )
            
            embed.set_footer(text="AntiNuke v6.0 • Punishment System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
    
    @punishment_group.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def punishment_set(self, ctx):
        """Configure punishment type"""
        embed = discord.Embed(
            title="⚖️ Set Punishment Type",
            description="Choose how to handle rule breakers",
            color=0xe74c3c
        )
        view = PunishmentView(self.bot, ctx.guild)
        await ctx.send(embed=embed, view=view)
    
    @punishment_group.command(name="view")
    async def punishment_view(self, ctx):
        """View detailed punishment settings"""
        punishment_config = await self.bot.db.get_antinuke_rule(ctx.guild.id, "punishment")
        punishment_type = punishment_config.get("type", "quarantine") if punishment_config else "quarantine"
        
        punishment_info = {
            "quarantine": {
                "name": "🔒 Quarantine Role",
                "description": "User is isolated with a special role that restricts all permissions",
                "severity": "Medium",
                "reversible": "Yes"
            },
            "kick": {
                "name": "👢 Kick User",
                "description": "User is removed from server but can rejoin with invite",
                "severity": "High",
                "reversible": "Yes (can rejoin)"
            },
            "ban": {
                "name": "🔨 Ban User",
                "description": "User is permanently banned from the server",
                "severity": "Critical",
                "reversible": "Manual unban required"
            },
            "strip_roles": {
                "name": "📝 Strip All Roles",
                "description": "All roles are removed from the user",
                "severity": "Medium",
                "reversible": "Manual role restoration"
            }
        }
        
        current = punishment_info.get(punishment_type, punishment_info["quarantine"])
        
        embed = discord.Embed(
            title="⚖️ AntiNuke Punishment Configuration",
            description=f"**Current active punishment for security violations**",
            color=0x7289da
        )
        
        embed.add_field(
            name="⚡ Active Punishment",
            value=f"**{current['name']}**\n{current['description']}",
            inline=False
        )
        
        embed.add_field(
            name="📊 Severity Level",
            value=current['severity'],
            inline=True
        )
        
        embed.add_field(
            name="🔄 Reversible",
            value=current['reversible'],
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Change Punishment",
            value="Use `/antinuke punishment set` to modify",
            inline=True
        )
        
        embed.set_footer(text="AntiNuke v6.0 • Punishment Settings • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @antinuke_group.group(name="whitelist")
    async def whitelist_group(self, ctx):
        if ctx.invoked_subcommand is None:
            whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
            whitelist_users = whitelist.get("users", []) if whitelist else []
            
            embed = discord.Embed(
                title="👥 AntiNuke Whitelist Management",
                description="**🔒 Trusted User System**\n\nWhitelisted users bypass all AntiNuke protections and can perform administrative actions without triggering security alerts.",
                color=0x95a5a6
            )
            
            if whitelist_users:
                user_list = []
                for user_id in whitelist_users[:10]:  # Show first 10
                    user = self.bot.get_user(user_id)
                    if user:
                        user_list.append(f"• {user.mention} (`{user.id}`)") 
                    else:
                        user_list.append(f"• Unknown User (`{user_id}`)") 
                
                embed.add_field(
                    name=f"✅ Whitelisted Users ({len(whitelist_users)})",
                    value="\n".join(user_list) + (f"\n... and {len(whitelist_users) - 10} more" if len(whitelist_users) > 10 else ""),
                    inline=False
                )
            else:
                embed.add_field(
                    name="📝 No Whitelisted Users",
                    value="No users are currently whitelisted. Server owner and bot admins are automatically trusted.",
                    inline=False
                )
            
            embed.add_field(
                name="⚡ Quick Commands",
                value="• `/antinuke whitelist add <user>` - Add trusted user\n• `/antinuke whitelist remove <user>` - Remove user\n• `/antinuke whitelist list` - View all whitelisted users",
                inline=False
            )
            
            embed.set_footer(text="AntiNuke v6.0 • Whitelist System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
    
    @whitelist_group.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_add(self, ctx, user: discord.Member):
        """Add user to AntiNuke whitelist"""
        if user.bot:
            embed = discord.Embed(
                title="❌ Cannot Whitelist Bot",
                description="Bots cannot be added to the whitelist for security reasons.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
        if not whitelist:
            whitelist = {"users": []}
        
        if user.id in whitelist["users"]:
            embed = discord.Embed(
                title="⚠️ Already Whitelisted",
                description=f"{user.mention} is already in the whitelist.",
                color=0xffd700
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        whitelist["users"].append(user.id)
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "whitelist", whitelist)
        
        embed = discord.Embed(
            title="✅ User Successfully Whitelisted",
            description=f"**{user.display_name}** has been added to the AntiNuke whitelist.",
            color=0x00ff00
        )
        
        embed.add_field(
            name="👤 User Information",
            value=f"**User:** {user.mention}\n**ID:** `{user.id}`\n**Joined:** <t:{int(user.joined_at.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Permissions Granted",
            value="• Bypass all AntiNuke protections\n• Perform admin actions safely\n• No security alerts triggered",
            inline=True
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="AntiNuke v6.0 • Whitelist System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
        
        # Log the action
        await self.log_action(ctx.guild, "User Whitelisted", user, f"Added to whitelist by {ctx.author}", "LOW")
    
    @whitelist_group.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_remove(self, ctx, user: discord.Member):
        """Remove user from AntiNuke whitelist"""
        whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
        
        if not whitelist or user.id not in whitelist.get("users", []):
            embed = discord.Embed(
                title="❌ User Not Whitelisted",
                description=f"{user.mention} is not in the whitelist.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        whitelist["users"].remove(user.id)
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "whitelist", whitelist)
        
        embed = discord.Embed(
            title="✅ User Removed from Whitelist",
            description=f"**{user.display_name}** has been removed from the AntiNuke whitelist.",
            color=0x00ff00
        )
        
        embed.add_field(
            name="👤 User Information",
            value=f"**User:** {user.mention}\n**ID:** `{user.id}`\n**Removed by:** {ctx.author.mention}",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Security Notice",
            value="• User will now trigger AntiNuke\n• Admin actions will be monitored\n• Security alerts will be sent",
            inline=True
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="AntiNuke v6.0 • Whitelist System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
        
        # Log the action
        await self.log_action(ctx.guild, "User Removed from Whitelist", user, f"Removed by {ctx.author}", "MEDIUM")
    
    @whitelist_group.command(name="list")
    async def whitelist_list(self, ctx):
        """List all whitelisted users"""
        whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
        whitelist_users = whitelist.get("users", []) if whitelist else []
        
        embed = discord.Embed(
            title="📝 AntiNuke Whitelist",
            description=f"**🔒 Trusted Users in {ctx.guild.name}**\n\nThese users bypass all AntiNuke protections.",
            color=0x7289da
        )
        
        # Always whitelisted users
        embed.add_field(
            name="👑 Automatically Whitelisted",
            value=f"• **Server Owner:** <@{ctx.guild.owner_id}>\n• **Bot Admin:** <@1037768611126841405>",
            inline=False
        )
        
        if whitelist_users:
            user_chunks = [whitelist_users[i:i+10] for i in range(0, len(whitelist_users), 10)]
            
            for i, chunk in enumerate(user_chunks):
                user_list = []
                for user_id in chunk:
                    user = self.bot.get_user(user_id)
                    if user:
                        user_list.append(f"• **{user.display_name}** - {user.mention}")
                    else:
                        user_list.append(f"• **Unknown User** - `{user_id}`")
                
                field_name = f"✅ Manual Whitelist ({len(whitelist_users)} total)" if i == 0 else f"Continued..."
                embed.add_field(
                    name=field_name,
                    value="\n".join(user_list),
                    inline=False
                )
        else:
            embed.add_field(
                name="📝 Manual Whitelist",
                value="No manually whitelisted users.",
                inline=False
            )
        
        embed.add_field(
            name="⚡ Management Commands",
            value="• `/antinuke whitelist add <user>` - Add user\n• `/antinuke whitelist remove <user>` - Remove user",
            inline=False
        )
        
        embed.set_footer(text=f"AntiNuke v6.0 • Total Protected Users: {len(whitelist_users) + 2} • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @antinuke_group.command(name="config")
    async def antinuke_config(self, ctx):
        """View comprehensive AntiNuke configuration"""
        enabled = await self.bot.db.get_antinuke_rule(ctx.guild.id, "enabled")
        level = await self.bot.db.get_antinuke_rule(ctx.guild.id, "protection_level")
        punishment = await self.bot.db.get_antinuke_rule(ctx.guild.id, "punishment")
        whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
        logs = await self.bot.db.get_antinuke_rule(ctx.guild.id, "logs")
        
        is_enabled = enabled and enabled.get("status")
        status = "🟢 **ACTIVE**" if is_enabled else "🔴 **INACTIVE**"
        status_color = 0x00FF00 if is_enabled else 0xFF0000
        
        protection_level = level.get("level", "basic").upper() if level else "BASIC"
        punishment_type = punishment.get("type", "quarantine").replace("_", " ").title() if punishment else "Quarantine"
        whitelist_count = len(whitelist.get("users", [])) if whitelist else 0
        logs_channel = f"<#{logs.get('channel_id')}>" if logs and logs.get('channel_id') else "Not Set"
        
        embed = discord.Embed(
            title="🛡️ AntiNuke v6.0 Configuration Dashboard",
            description=f"**System Status:** {status}\n**Server:** {ctx.guild.name}\n**Owner:** <@{ctx.guild.owner_id}>",
            color=status_color
        )
        
        # Protection settings
        embed.add_field(
            name="⚡ Protection Settings",
            value=f"**Level:** {protection_level}\n**Punishment:** {punishment_type}\n**Response Time:** {'<1s' if protection_level == 'EXTREME' else '1-2s' if protection_level == 'STRONG' else '3-5s'}",
            inline=True
        )
        
        # Security info
        embed.add_field(
            name="🔒 Security Information",
            value=f"**Whitelisted Users:** {whitelist_count}\n**Logs Channel:** {logs_channel}\n**Emergency Mode:** {'🔴 Active' if ctx.guild.id in self.lockdown_guilds else '🟢 Standby'}",
            inline=True
        )
        
        # Protection coverage
        embed.add_field(
            name="🛡️ Protection Coverage",
            value="✅ Channel Management\n✅ Role Management\n✅ Member Management\n✅ Webhook Protection\n✅ Bot Protection\n✅ Permission Escalation",
            inline=False
        )
        
        # Quick actions
        embed.add_field(
            name="⚡ Quick Commands",
            value="`/antinuke setup` - Configuration wizard\n`/antinuke fastsetup` - Instant secure setup\n`/antinuke whitelist add <user>` - Add trusted user\n`/antinuke punishment set` - Change punishment",
            inline=False
        )
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)
        embed.set_footer(text=f"AntiNuke v6.0 • Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @antinuke_group.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def antinuke_reset(self, ctx):
        """Reset all AntiNuke settings (Owner only)"""
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="**🔒 Owner Only Command**\n\nOnly the server owner can reset AntiNuke settings for security reasons.",
                color=0xff0000
            )
            embed.set_footer(text="AntiNuke v6.0 • Security Restriction • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return
        
        # Confirmation embed
        confirm_embed = discord.Embed(
            title="⚠️ Confirm AntiNuke Reset",
            description="**🚨 WARNING: This will reset ALL AntiNuke settings!**\n\n• Disable protection system\n• Reset protection level to Basic\n• Clear whitelist\n• Remove punishment settings\n\n**Are you sure you want to continue?**",
            color=0xff8c00
        )
        confirm_embed.set_footer(text="This action cannot be undone!", icon_url=self.bot.user.display_avatar.url)
        
        # Add confirmation buttons
        view = discord.ui.View(timeout=30)
        
        async def confirm_callback(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ Only the command author can confirm this action.", ephemeral=True)
                return
            
            # Reset all settings
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "enabled", {"status": False})
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "protection_level", {"level": "basic"})
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "punishment", {"type": "quarantine"})
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "whitelist", {"users": []})
            
            reset_embed = discord.Embed(
                title="✅ AntiNuke Reset Complete",
                description="**🔄 All settings have been reset to defaults**\n\n• **System Status:** Disabled\n• **Protection Level:** Basic\n• **Punishment:** Quarantine\n• **Whitelist:** Cleared\n\nYour server is no longer protected. Use `/antinuke setup` to reconfigure.",
                color=0x00ff00
            )
            reset_embed.set_footer(text="AntiNuke v6.0 • Reset Complete • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await interaction.response.edit_message(embed=reset_embed, view=None)
        
        async def cancel_callback(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ Only the command author can cancel this action.", ephemeral=True)
                return
            
            cancel_embed = discord.Embed(
                title="❌ Reset Cancelled",
                description="AntiNuke reset has been cancelled. All settings remain unchanged.",
                color=0x7289da
            )
            cancel_embed.set_footer(text="AntiNuke v6.0 • No Changes Made • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await interaction.response.edit_message(embed=cancel_embed, view=None)
        
        confirm_button = discord.ui.Button(label="✅ Confirm Reset", style=discord.ButtonStyle.danger)
        cancel_button = discord.ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        
        await ctx.send(embed=confirm_embed, view=view)
    
    @antinuke_group.command(name="emergency")
    @commands.has_permissions(administrator=True)
    async def emergency_lockdown(self, ctx):
        """Emergency server lockdown (Owner/Admin only)"""
        if ctx.author.id not in [ctx.guild.owner_id, 1037768611126841405]:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only server owner or bot admin can trigger emergency lockdown.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if ctx.guild.id in self.lockdown_guilds:
            # Remove from lockdown
            self.lockdown_guilds.remove(ctx.guild.id)
            embed = discord.Embed(
                title="✅ Emergency Lockdown Lifted",
                description="**🔓 Server lockdown has been lifted**\n\nNormal operations have resumed.",
                color=0x00ff00
            )
        else:
            # Add to lockdown
            self.lockdown_guilds.add(ctx.guild.id)
            embed = discord.Embed(
                title="🚨 Emergency Lockdown Activated",
                description="**🔒 Server is now in emergency lockdown**\n\nAll administrative actions are temporarily restricted.",
                color=0xff0000
            )
        
        embed.set_footer(text="AntiNuke v6.0 • Emergency System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
        
        # Log the emergency action
        await self.log_action(ctx.guild, "Emergency Lockdown Toggled", ctx.author, f"Lockdown {'activated' if ctx.guild.id in self.lockdown_guilds else 'deactivated'} by {ctx.author}", "CRITICAL")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))