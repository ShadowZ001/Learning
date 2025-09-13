import discord
from discord.ext import commands
import re

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = set()
        self.link_filter = set()
        self.spam_filter = set()
        self.caps_filter = set()
        self.profanity_filter = set()
        self.bad_words = ['fuck', 'shit', 'bitch', 'damn', 'ass', 'hell', 'crap', 'piss']
    
    @commands.hybrid_group(name="automod")
    async def automod_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"AutoMod — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Configuration Commands",
                value="`>automod setup` - Enable AutoMod\n`>automod links enable/disable` - Link filtering\n`>automod spam enable/disable` - Spam protection\n`>automod caps enable/disable` - Caps filtering\n`>automod profanity enable/disable` - Bad word filter",
                inline=False
            )
            await ctx.send(embed=embed)
    
    @automod_group.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def automod_setup(self, ctx):
        self.enabled_guilds.add(ctx.guild.id)
        self.link_filter.add(ctx.guild.id)
        self.spam_filter.add(ctx.guild.id)
        self.caps_filter.add(ctx.guild.id)
        self.profanity_filter.add(ctx.guild.id)
        
        embed = discord.Embed(
            title="AutoMod Enabled",
            description="AutoMod has been enabled with all filters active.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @automod_group.command(name="links")
    @commands.has_permissions(manage_guild=True)
    async def automod_links(self, ctx, action: str):
        if action.lower() == "enable":
            self.link_filter.add(ctx.guild.id)
            await ctx.send("Link filter enabled.")
        elif action.lower() == "disable":
            self.link_filter.discard(ctx.guild.id)
            await ctx.send("Link filter disabled.")
    
    @automod_group.command(name="profanity")
    @commands.has_permissions(manage_guild=True)
    async def automod_profanity(self, ctx, action: str):
        if action.lower() == "enable":
            self.profanity_filter.add(ctx.guild.id)
            await ctx.send("Profanity filter enabled.")
        elif action.lower() == "disable":
            self.profanity_filter.discard(ctx.guild.id)
            await ctx.send("Profanity filter disabled.")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        if message.guild.id not in self.enabled_guilds:
            return
        
        # Link filter
        if message.guild.id in self.link_filter:
            if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content):
                try:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, links are not allowed!", delete_after=3)
                except:
                    pass
                return
        
        # Profanity filter
        if message.guild.id in self.profanity_filter:
            for word in self.bad_words:
                if word.lower() in message.content.lower():
                    try:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention}, watch your language!", delete_after=3)
                    except:
                        pass
                    return
        
        # Caps filter
        if message.guild.id in self.caps_filter:
            if len(message.content) > 10 and sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.7:
                try:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, please don't use excessive caps!", delete_after=3)
                except:
                    pass

async def setup(bot):
    await bot.add_cog(AutoMod(bot))