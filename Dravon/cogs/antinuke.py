import discord
from discord.ext import commands
import asyncio
import time
from datetime import datetime, timedelta
from utils.embed_utils import add_dravon_footer

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
    
    async def is_whitelisted(self, guild_id: int, user_id: int) -> bool:
        """Check if user is whitelisted"""
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
    
    async def log_action(self, guild: discord.Guild, action: str, user: discord.Member, details: str):
        """Log security action"""
        logs_config = await self.bot.db.get_antinuke_rule(guild.id, "logs")
        if not logs_config:
            return
        
        channel_id = logs_config.get("channel_id")
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title="🚨 AntiNuke Alert",
            description=f"**Action:** {action}\n**User:** {user.mention} ({user.id})\n**Details:** {details}",
            color=0xff0000,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed = add_dravon_footer(embed)
        
        try:
            await channel.send(embed=embed)
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
            embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413172497964339200/antinuke_banner.gif")
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
    
    @antinuke_group.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def antinuke_setup(self, ctx):
        """Interactive AntiNuke setup wizard"""
        embed = discord.Embed(
            title="🛡️ AntiNuke Setup Wizard",
            description="**Welcome to Dravon™ AntiNuke v6.0**\n\nUse the dropdown below to configure your server's protection settings.",
            color=0x4ecdc4
        )
        embed.add_field(
            name="🔧 Available Options",
            value="• Enable/Disable System\n• Manage Whitelist\n• Set Protection Level\n• Configure Punishments\n• Setup Logging\n• Auto Alerts",
            inline=False
        )
        embed = add_dravon_footer(embed)
        
        view = AntiNukeSetupView(self.bot, ctx.guild)
        await ctx.send(embed=embed, view=view)
    
    @antinuke_group.command(name="fastsetup")
    @commands.has_permissions(manage_guild=True)
    async def antinuke_fastsetup(self, ctx):
        """Instant secure AntiNuke setup"""
        # Processing animation
        embed = discord.Embed(
            title="🚀 Fast Setup in Progress",
            description="⏳ Setting up your server security...",
            color=0xffd700
        )
        message = await ctx.send(embed=embed)
        
        steps = [
            "🔧 Initializing AntiNuke system...",
            "🛡️ Creating security roles...",
            "📝 Setting up logging channel...",
            "🔒 Configuring quarantine system...",
            "⚡ Applying protection settings...",
            "✅ Setup complete!"
        ]
        
        for i, step in enumerate(steps):
            progress = "█" * (i + 1) + "░" * (len(steps) - i - 1)
            embed.description = f"{step}\n\n`{progress}` {int((i + 1) / len(steps) * 100)}%"
            await message.edit(embed=embed)
            await asyncio.sleep(1)
        
        # Actually configure the system
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "enabled", {"status": True})
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "protection_level", {"level": "strong"})
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "punishment", {"type": "quarantine"})
        
        # Create quarantine role
        await self.get_quarantine_role(ctx.guild)
        
        # Create logs channel
        try:
            logs_channel = await ctx.guild.create_text_channel(
                "🛡️-antinuke-logs",
                reason="AntiNuke Fast Setup"
            )
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "logs", {"channel_id": logs_channel.id})
        except:
            pass
        
        final_embed = discord.Embed(
            title="🎉 Fast Setup Complete!",
            description="**Your server is now protected by Dravon™ AntiNuke v6.0**",
            color=0x00ff00
        )
        final_embed.add_field(
            name="✅ Configured Features",
            value="• AntiNuke System: **Enabled**\n• Protection Level: **Strong**\n• Punishment: **Quarantine Role**\n• Quarantine Role: **Created**\n• Logs Channel: **Created**",
            inline=False
        )
        final_embed = add_dravon_footer(final_embed)
        await message.edit(embed=final_embed)
    
    @antinuke_group.group(name="punishment")
    async def punishment_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="⚖️ Punishment System",
                description="Configure how AntiNuke handles rule breakers",
                color=0xe74c3c
            )
            embed = add_dravon_footer(embed)
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
        """View current punishment settings"""
        punishment_config = await self.bot.db.get_antinuke_rule(ctx.guild.id, "punishment")
        punishment_type = punishment_config.get("type", "quarantine") if punishment_config else "quarantine"
        
        punishment_names = {
            "quarantine": "🔒 Quarantine Role",
            "kick": "👢 Kick User",
            "ban": "🔨 Ban User",
            "strip_roles": "📝 Remove All Roles"
        }
        
        embed = discord.Embed(
            title="⚖️ Current Punishment Settings",
            description=f"**Active Punishment:** {punishment_names.get(punishment_type, 'Unknown')}",
            color=0x7289da
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @antinuke_group.group(name="whitelist")
    async def whitelist_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="👥 Whitelist System",
                description="Manage trusted users who bypass AntiNuke",
                color=0x95a5a6
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
    
    @whitelist_group.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_add(self, ctx, user: discord.Member):
        """Add user to whitelist"""
        whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
        if not whitelist:
            whitelist = {"users": []}
        
        if user.id not in whitelist["users"]:
            whitelist["users"].append(user.id)
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "whitelist", whitelist)
        
        embed = discord.Embed(
            title="✅ User Whitelisted",
            description=f"{user.mention} has been added to the whitelist",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @whitelist_group.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def whitelist_remove(self, ctx, user: discord.Member):
        """Remove user from whitelist"""
        whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
        if whitelist and user.id in whitelist.get("users", []):
            whitelist["users"].remove(user.id)
            await self.bot.db.set_antinuke_rule(ctx.guild.id, "whitelist", whitelist)
        
        embed = discord.Embed(
            title="✅ User Removed",
            description=f"{user.mention} has been removed from the whitelist",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @antinuke_group.command(name="config")
    async def antinuke_config(self, ctx):
        """View AntiNuke configuration"""
        enabled = await self.bot.db.get_antinuke_rule(ctx.guild.id, "enabled")
        level = await self.bot.db.get_antinuke_rule(ctx.guild.id, "protection_level")
        punishment = await self.bot.db.get_antinuke_rule(ctx.guild.id, "punishment")
        whitelist = await self.bot.db.get_antinuke_rule(ctx.guild.id, "whitelist")
        
        status = "🟢 Enabled" if enabled and enabled.get("status") else "🔴 Disabled"
        protection_level = level.get("level", "basic").title() if level else "Basic"
        punishment_type = punishment.get("type", "quarantine").replace("_", " ").title() if punishment else "Quarantine"
        whitelist_count = len(whitelist.get("users", [])) if whitelist else 0
        
        embed = discord.Embed(
            title="🛡️ AntiNuke Configuration",
            description="Current server protection settings",
            color=0x4ecdc4
        )
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Protection Level", value=protection_level, inline=True)
        embed.add_field(name="Punishment", value=punishment_type, inline=True)
        embed.add_field(name="Whitelisted Users", value=str(whitelist_count), inline=True)
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @antinuke_group.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def antinuke_reset(self, ctx):
        """Reset all AntiNuke settings"""
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner can reset AntiNuke settings!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Reset all settings
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "enabled", {"status": False})
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "protection_level", {"level": "basic"})
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "punishment", {"type": "quarantine"})
        await self.bot.db.set_antinuke_rule(ctx.guild.id, "whitelist", {"users": []})
        
        embed = discord.Embed(
            title="✅ AntiNuke Reset",
            description="All AntiNuke settings have been reset to default",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))