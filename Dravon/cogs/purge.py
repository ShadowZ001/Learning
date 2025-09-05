import discord
from discord.ext import commands
from discord import app_commands

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    
    @commands.hybrid_command(name="purge")
    @app_commands.describe(amount="Number of normal user messages to delete (1-1000)")
    async def purge_normal(self, ctx, amount: int):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You need 'Manage Messages' permission to use this command.")
            return
        
        if amount < 1 or amount > 1000:
            await ctx.send("Amount must be between 1 and 1000.")
            return
        
        try:
            # Delete only normal user messages (not bots)
            def check(message):
                return not message.author.bot
            
            deleted = await ctx.channel.purge(limit=amount*2, check=check)  # Check more messages to find enough user messages
            
            embed = discord.Embed(
                title="🗑️ User Messages Purged",
                description=f"Deleted **{len(deleted)}** user messages",
                color=0xff0000
            )
            
            embed.set_footer(text=f"Purged by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, delete_after=5)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages in this channel.")
        except discord.HTTPException:
            await ctx.send("Failed to delete some messages.")
    
    @commands.hybrid_command(name="pb")
    @app_commands.describe(amount="Number of bot messages to delete (1-1000)")
    async def purge_bots(self, ctx, amount: int):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You need 'Manage Messages' permission to use this command.")
            return
        
        if amount < 1 or amount > 1000:
            await ctx.send("Amount must be between 1 and 1000.")
            return
        
        try:
            # Delete only bot messages
            def check(message):
                return message.author.bot
            
            deleted = await ctx.channel.purge(limit=amount*2, check=check)  # Check more messages to find enough bot messages
            
            embed = discord.Embed(
                title="🤖 Bot Messages Purged",
                description=f"Deleted **{len(deleted)}** bot messages",
                color=0xff0000
            )
            
            embed.set_footer(text=f"Purged by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, delete_after=5)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages in this channel.")
        except discord.HTTPException:
            await ctx.send("Failed to delete some messages.")

async def setup(bot):
    await bot.add_cog(Purge(bot))