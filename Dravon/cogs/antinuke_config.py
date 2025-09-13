import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class AntiNukeConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="antinuke")
    async def antinuke_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"AntiNuke — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            embed.add_field(
                name="🛡️ Setup Commands",
                value="`>antinuke setup` - Interactive setup wizard\n`>antinuke fastsetup` - Quick secure setup\n`>antinuke config` - View current settings\n`>antinuke reset` - Reset all settings",
                inline=False
            )
            
            embed.add_field(
                name="👥 Whitelist Commands",
                value="`>antinuke whitelist add <user>` - Add trusted user\n`>antinuke whitelist remove <user>` - Remove user\n`>antinuke whitelist list` - View whitelisted users",
                inline=False
            )
            
            embed.add_field(
                name="⚖️ Punishment Commands",
                value="`>antinuke punishment set` - Configure punishment\n`>antinuke punishment view` - View punishment settings",
                inline=False
            )
            
            embed.add_field(
                name="📝 Logging Commands",
                value="`>antinuke logs <channel>` - Set logs channel\n`>antinuke logs` - View current logs channel",
                inline=False
            )
            
            embed.add_field(
                name="🚨 Emergency Commands",
                value="`>antinuke emergency` - Toggle emergency lockdown\n`>antinuke status` - View protection status",
                inline=False
            )
            
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiNukeConfig(bot))