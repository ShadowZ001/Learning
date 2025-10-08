import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="admin")
    @commands.has_permissions(administrator=True)
    async def admin_panel(self, ctx):
        """Admin control panel"""
        embed = discord.Embed(
            title="⚙️ Admin Panel",
            description="Administrator commands and server management",
            color=0x808080
        )
        embed.add_field(
            name="🛠️ Available Commands",
            value="`>antinuke setup` - Security system\n`>automod setup` - Auto moderation\n`>ticket setup` - Ticket system\n`>welcome setup` - Welcome messages",
            inline=False
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))