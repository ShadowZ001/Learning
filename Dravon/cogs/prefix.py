import discord
from discord.ext import commands
from discord import app_commands

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="bot")
    async def dravon_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `bot prefix set <newprefix>` to change the bot prefix.")
    
    @dravon_group.group(name="prefix")
    async def prefix_group(self, ctx):
        if ctx.invoked_subcommand is None:
            current_prefix = await self.bot.db.get_prefix(ctx.guild.id) or "?"
            await ctx.send(f"Current prefix: `{current_prefix}`")
    
    @prefix_group.command(name="set")
    @app_commands.describe(new_prefix="The new prefix for the bot")
    async def set_prefix(self, ctx, new_prefix: str):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to change the prefix.")
            return
        
        if len(new_prefix) > 5:
            await ctx.send("Prefix cannot be longer than 5 characters.")
            return
        
        await self.bot.db.set_prefix(ctx.guild.id, new_prefix)
        
        embed = discord.Embed(
            title="Prefix Updated!",
            description=f"Bot prefix has been changed to: `{new_prefix}`",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Prefix(bot))