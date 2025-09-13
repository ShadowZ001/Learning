import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta

class AntiNukeSetupView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.select(
        placeholder="🛡️ Configure AntiNuke Protection...",
        options=[
            discord.SelectOption(label="🔧 Enable/Disable System", description="Toggle AntiNuke protection", value="toggle", emoji="🔧"),
            discord.SelectOption(label="👥 Manage Whitelist", description="Add/remove trusted users", value="whitelist", emoji="👥"),
            discord.SelectOption(label="⚡ Protection Level", description="Basic, Strong, or Extreme", value="level", emoji="⚡"),
            discord.SelectOption(label="⚖️ Auto Punishment", description="Set punishment type", value="punishment", emoji="⚖️"),
            discord.SelectOption(label="📝 Logging Channel", description="Set logs channel", value="logs", emoji="📝")
        ]
    )
    async def setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        
        if value == "toggle":
            embed = discord.Embed(
                title="🛡️ AntiNuke System Toggle",
                description="Choose to enable or disable the AntiNuke system",
                color=0x2f3136
            )
            view = ToggleView(self.bot, self.guild)
            await interaction.response.edit_message(embed=embed, view=view)

class ToggleView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.button(label="🟢 Enable AntiNuke", style=discord.ButtonStyle.success)
    async def enable_antinuke(self, interaction: discord.Interaction, button: discord.ui.Button):
        antinuke_cog = self.bot.get_cog('AntiNuke')
        if antinuke_cog:
            antinuke_cog.enabled_guilds.add(self.guild.id)
            antinuke_cog.punishment_type[self.guild.id] = "kick"
        
        embed = discord.Embed(
            title="✅ AntiNuke Enabled",
            description="🛡️ Your server is now protected by Dravon™ AntiNuke system!",
            color=0x2f3136
        )
        await interaction.response.edit_message(embed=embed, view=None)

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()
        self.whitelisted_users = {}
        self.action_tracker = {}
        self.punishment_type = {}
    
    def is_owner_or_extra(self, guild, user):
        return user.id == guild.owner_id or user.id == 1037768611126841405
    
    @commands.hybrid_group(name="antinuke")
    async def antinuke_group(self, ctx):
        if not self.is_owner_or_extra(ctx.guild, ctx.author):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="This command can only be used by the server owner or extra owners.",
                color=0x808080
            )
            embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return
        
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"🛡️ AntiNuke — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="🚀 Setup Commands",
                value="`>antinuke setup` - Interactive setup wizard\n`>antinuke config` - View current settings\n`>antinuke whitelist add <user>` - Add trusted user",
                inline=False
            )
            await ctx.send(embed=embed)
    
    @antinuke_group.command(name="setup")
    async def antinuke_setup(self, ctx):
        embed = discord.Embed(
            title="🛡️ Dravon™ AntiNuke v6.0 Setup",
            description="**🚀 Advanced Server Protection System**\n\nProtect your server from malicious attacks with our state-of-the-art security system.",
            color=0x808080
        )
        embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        view = AntiNukeSetupView(self.bot, ctx.guild)
        await ctx.send(embed=embed, view=view)
    
    @antinuke_group.group(name="whitelist")
    async def whitelist_group(self, ctx):
        pass
    
    @whitelist_group.command(name="add")
    async def whitelist_add(self, ctx, user: discord.Member):
        if ctx.guild.id not in self.whitelisted_users:
            self.whitelisted_users[ctx.guild.id] = []
        
        if user.id not in self.whitelisted_users[ctx.guild.id]:
            self.whitelisted_users[ctx.guild.id].append(user.id)
        
        embed = discord.Embed(
            title="✅ User Whitelisted",
            description=f"👤 {user.mention} has been added to the whitelist.",
            color=0x808080
        )
        embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
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
        except Exception as e:
            print(f"AntiNuke punishment failed: {e}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id not in self.enabled_guilds:
            return
        
        try:
            async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                if entry.target.id == message.author.id and entry.user != self.bot.user:
                    if self.is_whitelisted(message.guild.id, entry.user.id):
                        return
                    
                    action_count = self.track_action(message.guild.id, entry.user.id)
                    if action_count >= 5:
                        await self.execute_punishment(message.guild, entry.user, "Mass message deletion")
                break
        except:
            pass

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))