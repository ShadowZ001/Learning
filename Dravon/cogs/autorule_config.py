import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class AutoRuleConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="autorule")
    async def autorule_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"AutoRule — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            embed.add_field(
                name="⚙️ Setup Commands",
                value="`>autorule setup` - Interactive setup wizard\n`>autorule config` - View current settings\n`>autorule reset` - Reset all settings",
                inline=False
            )
            
            embed.add_field(
                name="📝 Rule Commands",
                value="`>autorule add <rule>` - Add new rule\n`>autorule remove <rule>` - Remove rule\n`>autorule list` - View all rules\n`>autorule edit <rule>` - Edit existing rule",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Management Commands",
                value="`>autorule enable <rule>` - Enable rule\n`>autorule disable <rule>` - Disable rule\n`>autorule logs <channel>` - Set logs channel",
                inline=False
            )
            
            embed.add_field(
                name="📊 Monitoring Commands",
                value="`>autorule stats` - View rule statistics\n`>autorule test <rule>` - Test rule functionality",
                inline=False
            )
            
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoRuleConfig(bot))