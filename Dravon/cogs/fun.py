import discord
from discord.ext import commands
import random
# from utils.embed_utils import add_dravon_footer

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="8ball")
    async def eightball(self, ctx, *, question):
        """Ask the magic 8ball"""
        responses = [
            "Yes", "No", "Maybe", "Definitely", "Absolutely not",
            "Ask again later", "Very likely", "Unlikely", "Certainly",
            "Don't count on it", "Yes definitely", "Reply hazy, try again"
        ]
        
        embed = discord.Embed(
            title="🎱 Magic 8Ball",
            description=f"**Question:** {question}\n**Answer:** {random.choice(responses)}",
            color=0x808080
        )
        embed.set_footer(text="Powered by Dravon™")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="coinflip")
    async def coinflip(self, ctx):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"Result: **{result}**",
            color=0x808080
        )
        embed.set_footer(text="Powered by Dravon™")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="dice")
    async def dice(self, ctx, sides: int = 6):
        """Roll a dice"""
        if sides < 2:
            sides = 6
        if sides > 100:
            sides = 100
            
        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"Rolled a **{result}** on a {sides}-sided dice",
            color=0x808080
        )
        embed.set_footer(text="Powered by Dravon™")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))