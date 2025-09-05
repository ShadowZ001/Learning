import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class TeamsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.select(
        placeholder="Select a team member to learn more...",
        options=[
            discord.SelectOption(label="👑 Owner/Founder", description="Learn about the founder", value="owner"),
            discord.SelectOption(label="🤝 Co-Owner", description="Learn about the co-owner", value="co_owner"),
            discord.SelectOption(label="💻 Developer", description="Learn about the developer", value="developer"),
            discord.SelectOption(label="🌐 Community Manager", description="Learn about the community manager", value="community_manager")
        ]
    )
    async def team_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        role = select.values[0]
        
        if role == "owner":
            embed = discord.Embed(
                title="👑 Founder / Owner",
                description="<@1037768611126841405> is the visionary leader and founder of this project.\nThey set the direction, ensure quality, and make the big decisions that shape the future of this bot.\nWithout their vision, none of this would exist.",
                color=0xffd700
            )
        
        elif role == "co_owner":
            embed = discord.Embed(
                title="🤝 Co-Owner",
                description="<@1255206310904074290> is the right hand of the founder.\nThey help manage the project, organize tasks, and step in whenever important decisions need support.\nA crucial pillar of the team.",
                color=0xff6b6b
            )
        
        elif role == "developer":
            embed = discord.Embed(
                title="💻 Developer",
                description="<@1037768611126841405> is the brains behind the code.\nFrom core features to advanced systems, they design and maintain the bot's functionalities.\nAlways working to keep the bot stable, fast, and secure.",
                color=0x4ecdc4
            )
        
        elif role == "community_manager":
            embed = discord.Embed(
                title="🌐 Community Manager",
                description="<@1130089558734803025> bridges the gap between the users and the team.\nThey manage communication, feedback, and make sure the community stays engaged, happy, and heard.",
                color=0x45b7d1
            )
        
        embed = add_dravon_footer(embed)
        view = TeamsView()
        await interaction.response.edit_message(embed=embed, view=view)

class Teams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="teams")
    async def teams(self, ctx):
        """Display team information with interactive dropdown"""
        
        embed = discord.Embed(
            title="🤝 Meet Our Team",
            description="These are the dedicated people who keep this bot running smoothly and safe for the community.\nClick the dropdown below to learn more about each member's role.",
            color=0x7289da
        )
        
        embed.add_field(
            name="👑 Founder/Owner",
            value="<@1037768611126841405>",
            inline=True
        )
        
        embed.add_field(
            name="🤝 Co-Owner",
            value="<@1255206310904074290>",
            inline=True
        )
        
        embed.add_field(
            name="💻 Developer",
            value="<@1037768611126841405>",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Community Manager",
            value="<@1130089558734803025>",
            inline=True
        )
        
        embed.set_footer(text="Strong Team. Strong Community.")
        
        view = TeamsView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Teams(bot))