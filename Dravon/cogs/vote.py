import discord
from discord.ext import commands
import asyncio

class VoteView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="Vote on top.gg", style=discord.ButtonStyle.primary, emoji="🗳️")
    async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Send immediate response
        await interaction.response.send_message("🗳️ Thank you for voting! Opening vote page...", ephemeral=True)
        
        # Schedule DM after 10 seconds
        asyncio.create_task(self.send_thank_you_dm(interaction.user))
    
    async def send_thank_you_dm(self, user):
        """Send thank you DM after 10 seconds"""
        await asyncio.sleep(10)
        try:
            embed = discord.Embed(
                title="💖 Thanks for voting!",
                description="**Thanks for voting on top.gg for Dravon >3**\n\nYour support helps us grow and improve the bot for everyone!",
                color=0x00ff00
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413146132405817487/f41e57df-936d-428a-8aa8-a0b4ca2a1e64.jpg")
            embed.set_footer(text="Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await user.send(embed=embed)
        except:
            pass  # User has DMs disabled

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="vote")
    async def vote_command(self, ctx):
        """Vote for Dravon on top.gg"""
        embed = discord.Embed(
            description="Click the button below to vote for Dravon™ on Top.gg!",
            color=0x7289da
        )
        
        # Create view with vote button
        view = discord.ui.View(timeout=None)
        
        # Add the vote URL as a button
        vote_button = discord.ui.Button(
            label="Vote on top.gg",
            style=discord.ButtonStyle.link,
            url="https://dravon.top.gg",
            emoji="🗳️"
        )
        view.add_item(vote_button)
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Vote(bot))