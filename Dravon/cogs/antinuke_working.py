import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()
        self.whitelisted_users = {}  # guild_id: [user_ids]
        self.action_tracker = {}     # guild_id: {user_id: [timestamps]}
        self.punishment_type = {}    # guild_id: punishment_type
    
    @commands.hybrid_group(name="antinuke")
    async def antinuke_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"AntiNuke — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Setup Commands",
                value="`>antinuke setup` - Enable AntiNuke\n`>antinuke whitelist add <user>` - Add trusted user\n`>antinuke punishment <type>` - Set punishment (kick/ban/quarantine)",
                inline=False
            )
            await ctx.send(embed=embed)
    
    @antinuke_group.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def antinuke_setup(self, ctx):
        self.enabled_guilds.add(ctx.guild.id)
        self.punishment_type[ctx.guild.id] = "kick"
        
        embed = discord.Embed(
            title="AntiNuke Enabled",
            description="AntiNuke protection is now active.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @antinuke_group.group(name="whitelist")
    async def whitelist_group(self, ctx):
        pass
    
    @whitelist_group.command(name="add")
    @commands.has_permissions(administrator=True)
    async def whitelist_add(self, ctx, user: discord.Member):
        if ctx.guild.id not in self.whitelisted_users:
            self.whitelisted_users[ctx.guild.id] = []
        
        if user.id not in self.whitelisted_users[ctx.guild.id]:
            self.whitelisted_users[ctx.guild.id].append(user.id)
        
        embed = discord.Embed(
            title="User Whitelisted",
            description=f"{user.mention} has been added to the whitelist.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @antinuke_group.command(name="punishment")
    @commands.has_permissions(administrator=True)
    async def set_punishment(self, ctx, punishment_type: str):
        if punishment_type.lower() in ["kick", "ban", "quarantine"]:
            self.punishment_type[ctx.guild.id] = punishment_type.lower()
            await ctx.send(f"Punishment set to: {punishment_type}")
        else:
            await ctx.send("Valid punishments: kick, ban, quarantine")
    
    def is_whitelisted(self, guild_id, user_id):
        if guild_id not in self.whitelisted_users:
            return False
        return user_id in self.whitelisted_users[guild_id]
    
    def track_action(self, guild_id, user_id):
        now = datetime.now()
        if guild_id not in self.action_tracker:
            self.action_tracker[guild_id] = {}
        if user_id not in self.action_tracker[guild_id]:
            self.action_tracker[guild_id][user_id] = []
        
        # Remove old actions (older than 1 minute)
        self.action_tracker[guild_id][user_id] = [
            timestamp for timestamp in self.action_tracker[guild_id][user_id]
            if now - timestamp < timedelta(minutes=1)
        ]
        
        self.action_tracker[guild_id][user_id].append(now)
        return len(self.action_tracker[guild_id][user_id])
    
    async def execute_punishment(self, guild, user, reason):
        punishment = self.punishment_type.get(guild.id, "kick")
        
        try:
            if punishment == "kick":
                await user.kick(reason=f"AntiNuke: {reason}")
            elif punishment == "ban":
                await user.ban(reason=f"AntiNuke: {reason}")
            elif punishment == "quarantine":
                # Create quarantine role if doesn't exist
                quarantine_role = discord.utils.get(guild.roles, name="Quarantined")
                if not quarantine_role:
                    quarantine_role = await guild.create_role(
                        name="Quarantined",
                        permissions=discord.Permissions.none(),
                        reason="AntiNuke Quarantine Role"
                    )
                await user.add_roles(quarantine_role, reason=f"AntiNuke: {reason}")
        except Exception as e:
            print(f"AntiNuke punishment failed: {e}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id not in self.enabled_guilds:
            return
        
        # Get audit log entry
        try:
            async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                if entry.target.id == message.author.id and entry.user != self.bot.user:
                    if self.is_whitelisted(message.guild.id, entry.user.id):
                        return
                    
                    action_count = self.track_action(message.guild.id, entry.user.id)
                    if action_count >= 5:  # 5 deletions in 1 minute
                        await self.execute_punishment(message.guild, entry.user, "Mass message deletion")
                break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id not in self.enabled_guilds:
            return
        
        try:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
                if entry.target.id == member.id and entry.user != self.bot.user:
                    if self.is_whitelisted(member.guild.id, entry.user.id):
                        return
                    
                    action_count = self.track_action(member.guild.id, entry.user.id)
                    if action_count >= 3:  # 3 kicks in 1 minute
                        await self.execute_punishment(member.guild, entry.user, "Mass member kicks")
                break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild.id not in self.enabled_guilds:
            return
        
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                if entry.target.id == user.id and entry.user != self.bot.user:
                    if self.is_whitelisted(guild.id, entry.user.id):
                        return
                    
                    action_count = self.track_action(guild.id, entry.user.id)
                    if action_count >= 3:  # 3 bans in 1 minute
                        await self.execute_punishment(guild, entry.user, "Mass member bans")
                break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if channel.guild.id not in self.enabled_guilds:
            return
        
        try:
            async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                if entry.user != self.bot.user:
                    if self.is_whitelisted(channel.guild.id, entry.user.id):
                        return
                    
                    action_count = self.track_action(channel.guild.id, entry.user.id)
                    if action_count >= 3:  # 3 channel deletions in 1 minute
                        await self.execute_punishment(channel.guild, entry.user, "Mass channel deletion")
                break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if role.guild.id not in self.enabled_guilds:
            return
        
        try:
            async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
                if entry.user != self.bot.user:
                    if self.is_whitelisted(role.guild.id, entry.user.id):
                        return
                    
                    action_count = self.track_action(role.guild.id, entry.user.id)
                    if action_count >= 3:  # 3 role deletions in 1 minute
                        await self.execute_punishment(role.guild, entry.user, "Mass role deletion")
                break
        except:
            pass

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))