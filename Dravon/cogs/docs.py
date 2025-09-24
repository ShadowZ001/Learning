import discord
from discord.ext import commands

class Docs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='docs', aliases=['documentation'])
    async def docs(self, ctx):
        try:
            embed = discord.Embed(
                title="📚 Dravon Bot Documentation",
                description="Access our comprehensive documentation website for detailed guides, commands, and setup instructions.",
                color=0x58a6ff
            )
            embed.add_field(
                name="🌐 Website",
                value="[**Visit Documentation**](https://dravon-docs.netlify.app)",
                inline=False
            )
            embed.add_field(
                name="📖 What you'll find:",
                value="• Complete command guides\n• Step-by-step setup tutorials\n• Premium features overview\n• Security & moderation tools\n• Music system documentation",
                inline=False
            )
            if self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)
                embed.set_footer(text="Dravon Bot Documentation", icon_url=self.bot.user.avatar.url)
            else:
                embed.set_footer(text="Dravon Bot Documentation")
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"📚 **Dravon Bot Documentation**: https://dravon-docs.netlify.app")

async def setup(bot):
    await bot.add_cog(Docs(bot))
    print("Docs cog loaded successfully")