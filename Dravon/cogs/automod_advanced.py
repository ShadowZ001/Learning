import discord
from discord.ext import commands
import re

class AutoModSetupView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.select(
        placeholder="🤖 Configure AutoMod Settings...",
        options=[
            discord.SelectOption(label="🔧 Enable/Disable System", description="Toggle AutoMod protection", value="toggle", emoji="🔧"),
            discord.SelectOption(label="🔗 Link Filter", description="Block links and URLs", value="links", emoji="🔗"),
            discord.SelectOption(label="🤬 Profanity Filter", description="Block bad words", value="profanity", emoji="🤬"),
            discord.SelectOption(label="📢 Caps Filter", description="Block excessive caps", value="caps", emoji="📢"),
            discord.SelectOption(label="🚫 Spam Filter", description="Block spam messages", value="spam", emoji="🚫"),
            discord.SelectOption(label="🔞 NSFW Filter", description="Block inappropriate content", value="nsfw", emoji="🔞"),
            discord.SelectOption(label="👥 Whitelist Users", description="Add trusted users", value="whitelist", emoji="👥"),
            discord.SelectOption(label="📝 Logs Channel", description="Set logging channel", value="logs", emoji="📝")
        ]
    )
    async def setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            value = select.values[0]
            
            if value == "toggle":
                embed = discord.Embed(
                    title="🤖 AutoMod System Toggle",
                    description="Choose to enable or disable the AutoMod system",
                    color=0x2f3136
                )
                view = AutoModToggleView(self.bot, self.guild)
                await interaction.response.edit_message(embed=embed, view=view)
            
            elif value == "whitelist":
                embed = discord.Embed(
                    title="👥 AutoMod Whitelist",
                    description="Use `/automod whitelist add <user>` to add trusted users",
                    color=0x2f3136
                )
                await interaction.response.edit_message(embed=embed, view=None)
            
            else:
                embed = discord.Embed(
                    title=f"🔧 {value.title()} Filter",
                    description=f"Configure {value} filter settings",
                    color=0x2f3136
                )
                await interaction.response.edit_message(embed=embed, view=None)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message("An error occurred. Please try again.", ephemeral=True)

class AutoModToggleView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.button(label="🟢 Enable AutoMod", style=discord.ButtonStyle.success)
    async def enable_automod(self, interaction: discord.Interaction, button: discord.ui.Button):
        automod_cog = self.bot.get_cog('AutoMod')
        if automod_cog:
            automod_cog.enabled_guilds.add(self.guild.id)
            automod_cog.link_filter.add(self.guild.id)
            automod_cog.profanity_filter.add(self.guild.id)
            automod_cog.caps_filter.add(self.guild.id)
        
        embed = discord.Embed(
            title="✅ AutoMod Enabled",
            description="🤖 AutoMod protection is now active with all filters enabled!",
            color=0x2f3136
        )
        await interaction.response.edit_message(embed=embed, view=None)

class WhitelistUserView(discord.ui.View):
    def __init__(self, bot, guild, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
        self.user = user
    
    @discord.ui.select(
        placeholder="🔐 Select permissions to grant...",
        options=[
            discord.SelectOption(label="🛡️ AntiNuke Bypass", description="Bypass AntiNuke protection", value="antinuke", emoji="🛡️"),
            discord.SelectOption(label="🤖 AutoMod Bypass", description="Bypass AutoMod filters", value="automod", emoji="🤖"),
            discord.SelectOption(label="📝 AutoRule Bypass", description="Bypass AutoRule filters", value="autorule", emoji="📝"),
            discord.SelectOption(label="🌟 All Permissions", description="Grant all bypass permissions", value="all", emoji="🌟")
        ]
    )
    async def permission_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        permission = select.values[0]
        
        if permission == "antinuke":
            antinuke_cog = self.bot.get_cog('AntiNuke')
            if antinuke_cog:
                if self.guild.id not in antinuke_cog.whitelisted_users:
                    antinuke_cog.whitelisted_users[self.guild.id] = []
                if self.user.id not in antinuke_cog.whitelisted_users[self.guild.id]:
                    antinuke_cog.whitelisted_users[self.guild.id].append(self.user.id)
        
        elif permission == "automod":
            automod_cog = self.bot.get_cog('AutoMod')
            if automod_cog:
                if self.guild.id not in automod_cog.whitelisted_users:
                    automod_cog.whitelisted_users[self.guild.id] = []
                if self.user.id not in automod_cog.whitelisted_users[self.guild.id]:
                    automod_cog.whitelisted_users[self.guild.id].append(self.user.id)
        
        embed = discord.Embed(
            title="✅ Permissions Granted",
            description=f"🔐 {self.user.mention} has been granted {permission} bypass permissions.",
            color=0x2f3136
        )
        await interaction.response.edit_message(embed=embed, view=None)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()
        self.link_filter = set()
        self.profanity_filter = set()
        self.caps_filter = set()
        self.whitelisted_users = {}
        self.bad_words = ['fuck', 'shit', 'bitch', 'damn', 'ass', 'hell', 'crap', 'piss']
    
    def is_owner_or_extra(self, guild, user):
        return user.id == guild.owner_id or user.id == 1037768611126841405
    
    @commands.hybrid_group(name="automod")
    async def automod_group(self, ctx):
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
                title=f"🤖 AutoMod — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="🚀 Configuration Commands",
                value="`>automod setup` - Interactive setup wizard\n`>automod whitelist add <user>` - Add trusted user",
                inline=False
            )
            await ctx.send(embed=embed)
    
    @automod_group.command(name="setup")
    async def automod_setup(self, ctx):
        embed = discord.Embed(
            title="🤖 Dravon™ AutoMod Setup",
            description="**🚀 Advanced Automatic Moderation System**\n\nProtect your server with intelligent content filtering.",
            color=0x808080
        )
        embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        view = AutoModSetupView(self.bot, ctx.guild)
        await ctx.send(embed=embed, view=view)
    
    @automod_group.group(name="whitelist")
    async def whitelist_group(self, ctx):
        pass
    
    @whitelist_group.command(name="add")
    async def whitelist_add(self, ctx, user: discord.Member):
        embed = discord.Embed(
            title="🔐 Grant Permissions",
            description=f"Select which permissions to grant to {user.mention}",
            color=0x2f3136
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        view = WhitelistUserView(self.bot, ctx.guild, user)
        await ctx.send(embed=embed, view=view)
    
    def is_whitelisted(self, guild_id, user_id):
        if guild_id not in self.whitelisted_users:
            return False
        return user_id in self.whitelisted_users[guild_id]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        if message.guild.id not in self.enabled_guilds:
            return
        
        if self.is_whitelisted(message.guild.id, message.author.id):
            return
        
        # Link filter
        if message.guild.id in self.link_filter:
            if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content):
                try:
                    await message.delete()
                    await message.channel.send(f"🔗 {message.author.mention}, links are not allowed!", delete_after=3)
                except:
                    pass
                return
        
        # Profanity filter
        if message.guild.id in self.profanity_filter:
            for word in self.bad_words:
                if word.lower() in message.content.lower():
                    try:
                        await message.delete()
                        await message.channel.send(f"🤬 {message.author.mention}, watch your language!", delete_after=3)
                    except:
                        pass
                    return

async def setup(bot):
    await bot.add_cog(AutoMod(bot))