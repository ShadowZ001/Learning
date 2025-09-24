import discord
from discord.ext import commands
from datetime import datetime, timedelta
import re

def parse_time(time_str):
    """Parse time string like 1h, 30m, 1d into seconds"""
    if not time_str:
        return None
    
    time_regex = re.compile(r'(\d+)([smhd])')
    matches = time_regex.findall(time_str.lower())
    
    total_seconds = 0
    for amount, unit in matches:
        amount = int(amount)
        if unit == 's':
            total_seconds += amount
        elif unit == 'm':
            total_seconds += amount * 60
        elif unit == 'h':
            total_seconds += amount * 3600
        elif unit == 'd':
            total_seconds += amount * 86400
    
    return total_seconds if total_seconds > 0 else None

class WarnConfigView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose configuration option...",
        options=[
            discord.SelectOption(label="Max Warn Limit", description="Set maximum warnings before punishment", value="max_warn"),
            discord.SelectOption(label="Warn Punishment", description="Set punishment type", value="punishment"),
            discord.SelectOption(label="Save Config", description="Save current configuration", value="save"),
            discord.SelectOption(label="Disable Config", description="Disable warning system", value="disable"),
            discord.SelectOption(label="Warn Log Channel", description="Set warning log channel", value="log_channel")
        ]
    )
    async def config_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "max_warn":
            modal = MaxWarnModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif select.values[0] == "punishment":
            modal = PunishmentModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif select.values[0] == "save":
            await interaction.response.send_message("✅ Configuration saved!", ephemeral=True)
        elif select.values[0] == "disable":
            try:
                await self.bot.db.set_warn_config(self.guild_id, "disabled", 0)
            except:
                pass
            await interaction.response.send_message("✅ Warning system disabled!", ephemeral=True)
        elif select.values[0] == "log_channel":
            modal = LogChannelModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)

class MaxWarnModal(discord.ui.Modal, title="Set Max Warn Limit"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    max_warns = discord.ui.TextInput(
        label="Maximum Warnings (1-50)",
        placeholder="Enter number between 1-50...",
        max_length=2
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.max_warns.value)
            if 1 <= limit <= 50:
                try:
                    await self.bot.db.set_warn_config(self.guild_id, "kick", limit)
                except:
                    pass
                await interaction.response.send_message(f"✅ Max warn limit set to {limit}!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Limit must be between 1-50!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid number!", ephemeral=True)

class PunishmentModal(discord.ui.Modal, title="Set Warn Punishment"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    punishment = discord.ui.TextInput(
        label="Punishment Type",
        placeholder="ban, kick, or mute 1h...",
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        punishment_type = self.punishment.value.lower().strip()
        if punishment_type in ["ban", "kick"] or punishment_type.startswith("mute"):
            try:
                await self.bot.db.set_warn_config(self.guild_id, punishment_type, 3)
            except:
                pass
            await interaction.response.send_message(f"✅ Punishment set to {punishment_type}!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Invalid punishment! Use: ban, kick, or mute 1h", ephemeral=True)

class LogChannelModal(discord.ui.Modal, title="Set Warning Log Channel"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    channel = discord.ui.TextInput(
        label="Channel ID or #channel",
        placeholder="Enter channel ID or mention...",
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        channel_input = self.channel.value.strip()
        try:
            if channel_input.startswith('<#') and channel_input.endswith('>'):
                channel_id = int(channel_input[2:-1])
            elif channel_input.startswith('#'):
                channel = discord.utils.get(interaction.guild.channels, name=channel_input[1:])
                channel_id = channel.id if channel else None
            else:
                channel_id = int(channel_input)
            
            if channel_id:
                try:
                    await self.bot.db.set_warn_log_channel(self.guild_id, channel_id)
                except:
                    pass
                await interaction.response.send_message(f"✅ Warning log channel set to <#{channel_id}>!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Channel not found!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Invalid channel!", ephemeral=True)

class ModerationNew(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def is_premium(self, user_id, guild_id):
        """Check if user or guild has premium"""
        try:
            premium_cog = self.bot.get_cog('Premium')
            if premium_cog:
                user_premium = await premium_cog.is_premium(user_id)
                guild_premium = await premium_cog.is_premium_guild(guild_id)
                return user_premium or guild_premium
        except:
            pass
        return False
    
    async def send_dm(self, user, embed):
        """Send DM to user with error handling"""
        try:
            await user.send(embed=embed)
        except:
            pass
    
    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        """Ban a user from the server"""
        if user.id == ctx.author.id:
            await ctx.send("❌ You cannot ban yourself!")
            return
        
        if user.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot ban someone with equal or higher role!")
            return
        
        try:
            await user.ban(reason=f"Banned by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ User Banned",
                description=f"**User:** {user.mention}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to ban user: {str(e)}")
    
    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        """Kick a user from the server"""
        if user.id == ctx.author.id:
            await ctx.send("❌ You cannot kick yourself!")
            return
        
        if user.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot kick someone with equal or higher role!")
            return
        
        try:
            await user.kick(reason=f"Kicked by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ User Kicked",
                description=f"**User:** {user.mention}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to kick user: {str(e)}")
    
    @commands.hybrid_command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute_user(self, ctx, user: discord.Member, time: str, *, reason: str = "No reason provided"):
        """Mute a user for specified time"""
        if user.id == ctx.author.id:
            await ctx.send("❌ You cannot mute yourself!")
            return
        
        if user.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot mute someone with equal or higher role!")
            return
        
        seconds = parse_time(time)
        if not seconds:
            await ctx.send("❌ Invalid time format! Use: 1h, 30m, 1d, etc.")
            return
        
        if seconds > 2419200:
            await ctx.send("❌ Mute duration cannot exceed 28 days!")
            return
        
        try:
            until = datetime.now() + timedelta(seconds=seconds)
            await user.timeout(until, reason=f"Muted by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ User Muted",
                description=f"**User:** {user.mention}\n**Duration:** {time}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to mute user: {str(e)}")
    
    @commands.hybrid_group(name="role", fallback="help")
    @commands.has_permissions(manage_roles=True)
    async def role_group(self, ctx):
        """Role management commands"""
        embed = discord.Embed(
            title="🎭 Role Commands",
            description="**Usage:**\n• `/role add <user> <role>` - Add role to user\n• `/role remove <user> <role>` - Remove role from user",
            color=0x7289da
        )
        await ctx.send(embed=embed)
    
    @role_group.group(name="add", invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def role_add_group(self, ctx, user: discord.Member, role: discord.Role):
        """Add a role to a user"""
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot assign a role equal or higher than your highest role!")
            return
        
        if role in user.roles:
            await ctx.send(f"❌ {user.mention} already has the {role.mention} role!")
            return
        
        try:
            await user.add_roles(role, reason=f"Role added by {ctx.author}")
            
            embed = discord.Embed(
                title="✅ Role Added",
                description=f"Added {role.mention} to {user.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to add role: {str(e)}")
    
    @role_add_group.command(name="humans")
    @commands.has_permissions(manage_roles=True)
    async def role_add_humans(self, ctx, role: discord.Role):
        """Add role to all humans in the server"""
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot assign a role equal or higher than your highest role!")
            return
        
        humans = [member for member in ctx.guild.members if not member.bot]
        added_count = 0
        
        for member in humans:
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason=f"Bulk role add by {ctx.author}")
                    added_count += 1
                except:
                    pass
        
        embed = discord.Embed(
            title="✅ Role Added to Humans",
            description=f"Added {role.mention} to {added_count} humans",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @role_add_group.command(name="bots")
    @commands.has_permissions(manage_roles=True)
    async def role_add_bots(self, ctx, role: discord.Role):
        """Add role to all bots in the server"""
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot assign a role equal or higher than your highest role!")
            return
        
        bots = [member for member in ctx.guild.members if member.bot]
        added_count = 0
        
        for member in bots:
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason=f"Bulk role add by {ctx.author}")
                    added_count += 1
                except:
                    pass
        
        embed = discord.Embed(
            title="✅ Role Added to Bots",
            description=f"Added {role.mention} to {added_count} bots",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @role_group.command(name="remove")
    @commands.has_permissions(manage_roles=True)
    async def role_remove(self, ctx, user: discord.Member, role: discord.Role):
        """Remove a role from a user"""
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You cannot remove a role equal or higher than your highest role!")
            return
        
        if role not in user.roles:
            await ctx.send(f"❌ {user.mention} doesn't have the {role.mention} role!")
            return
        
        try:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
            
            embed = discord.Embed(
                title="✅ Role Removed",
                description=f"Removed {role.mention} from {user.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to remove role: {str(e)}")
    
    @commands.hybrid_group(name="warn", fallback="user")
    @commands.has_permissions(moderate_members=True)
    async def warn_group(self, ctx, user: discord.Member = None, *, reason: str = "No reason provided"):
        """Warn a user"""
        if user is None:
            embed = discord.Embed(
                title="⚠️ Warn Commands",
                description="**Usage:**\n• `/warn user <user> [reason]` - Warn a user\n• `/warn clear <user>` - Clear user warnings\n• `/warn list` - List all warned users\n• `/warn status` - Show warning status\n• `/warn config` - Configure warning system",
                color=0xffd700
            )
            await ctx.send(embed=embed)
            return
            
        if user.id == ctx.author.id:
            await ctx.send("❌ You cannot warn yourself!")
            return
        
        try:
            await self.bot.db.add_warning(ctx.guild.id, user.id, ctx.author.id, reason)
            warnings = await self.bot.db.get_user_warnings(ctx.guild.id, user.id)
            warning_count = len(warnings)
        except:
            warning_count = 1
        
        embed = discord.Embed(
            title="✅ User Warned",
            description=f"**User:** {user.mention}\n**Reason:** {reason}\n**Warning #{warning_count}**",
            color=0xffd700
        )
        await ctx.send(embed=embed)
        
        # Send to log channel
        try:
            log_channel_id = await self.bot.db.get_warn_log_channel(ctx.guild.id)
            if log_channel_id:
                log_channel = ctx.guild.get_channel(log_channel_id)
                if log_channel:
                    log_embed = discord.Embed(
                        title="⚠️ User Warned",
                        description=f"**User:** {user.mention} ({user.id})\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}\n**Total Warnings:** {warning_count}",
                        color=0xffd700,
                        timestamp=datetime.now()
                    )
                    await log_channel.send(embed=log_embed)
        except:
            pass
    
    @warn_group.command(name="clear")
    @commands.has_permissions(moderate_members=True)
    async def warn_clear(self, ctx, user: discord.Member):
        """Clear all warnings for a user"""
        try:
            await self.bot.db.clear_user_warnings(ctx.guild.id, user.id)
        except:
            pass
        
        embed = discord.Embed(
            title="✅ Warnings Cleared",
            description=f"All warnings cleared for {user.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @warn_group.command(name="list")
    @commands.has_permissions(moderate_members=True)
    async def warn_list(self, ctx):
        """List all warned users"""
        try:
            warned_users = await self.bot.db.get_all_warned_users(ctx.guild.id)
        except:
            warned_users = []
        
        if not warned_users:
            embed = discord.Embed(
                title="📝 Warning List",
                description="No users have been warned.",
                color=0x7289da
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📝 Warning List",
            description=f"Users with warnings in {ctx.guild.name}",
            color=0x7289da
        )
        
        for user_data in warned_users[:10]:
            try:
                user = ctx.guild.get_member(user_data['user_id'])
                user_name = user.display_name if user else f"Unknown User ({user_data['user_id']})"
                embed.add_field(
                    name=f"⚠️ {user_name}",
                    value=f"{user_data['warning_count']} warnings",
                    inline=True
                )
            except:
                continue
        
        await ctx.send(embed=embed)
    
    @warn_group.command(name="status")
    @commands.has_permissions(moderate_members=True)
    async def warn_status(self, ctx):
        """Show warning system status"""
        try:
            config = await self.bot.db.get_warn_config(ctx.guild.id)
            log_channel_id = await self.bot.db.get_warn_log_channel(ctx.guild.id)
        except:
            config = None
            log_channel_id = None
        
        embed = discord.Embed(
            title="⚙️ Warning System Status",
            color=0x7289da
        )
        
        if config:
            embed.add_field(
                name="Status",
                value="✅ Enabled",
                inline=True
            )
            embed.add_field(
                name="Max Warnings",
                value=config.get('limit', 3),
                inline=True
            )
            embed.add_field(
                name="Punishment",
                value=config.get('punishment', 'kick').title(),
                inline=True
            )
        else:
            embed.add_field(
                name="Status",
                value="❌ Disabled",
                inline=True
            )
        
        if log_channel_id:
            embed.add_field(
                name="Log Channel",
                value=f"<#{log_channel_id}>",
                inline=True
            )
        else:
            embed.add_field(
                name="Log Channel",
                value="Not set",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @warn_group.command(name="config")
    @commands.has_permissions(administrator=True)
    async def warn_config(self, ctx):
        """Configure warning system"""
        embed = discord.Embed(
            title="⚙️ Warning System Configuration",
            description="Use the dropdown below to configure the warning system for your server.",
            color=0x7289da
        )
        
        view = WarnConfigView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ModerationNew(bot))