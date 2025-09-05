import discord
from discord.ext import commands
import random
import aiohttp
from utils.embed_utils import add_dravon_footer

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.kiss_gifs = [
            "https://nekos.life/api/v2/img/kiss",
            "https://api.waifu.pics/sfw/kiss",
            "https://nekos.life/api/v2/img/kiss",
            "https://api.waifu.pics/sfw/kiss",
            "https://nekos.life/api/v2/img/kiss"
        ]
        
        self.slap_gifs = [
            "https://nekos.life/api/v2/img/slap",
            "https://api.waifu.pics/sfw/slap",
            "https://nekos.life/api/v2/img/slap",
            "https://api.waifu.pics/sfw/slap"
        ]
        
        self.kill_gifs = [
            "https://nekos.life/api/v2/img/pat",
            "https://api.waifu.pics/sfw/kill",
            "https://nekos.life/api/v2/img/pat",
            "https://api.waifu.pics/sfw/kill"
        ]
    
    @commands.hybrid_command(name="kiss")
    async def kiss(self, ctx, user: discord.Member):
        """Kiss someone with a cute anime gif"""
        if user == ctx.author:
            embed = discord.Embed(
                title="💋 Self Kiss?",
                description="You can't kiss yourself silly! Find someone else to kiss! 😘",
                color=0xff69b4
            )
        elif user == self.bot.user:
            embed = discord.Embed(
                title="💋 Bot Kiss",
                description=f"Aww, {ctx.author.mention} wants to kiss me! That's so sweet! 😊💕",
                color=0xff69b4
            )
        else:
            embed = discord.Embed(
                title="💋 Kiss",
                description=f"{ctx.author.mention} kisses {user.mention}! 😘💕",
                color=0xff69b4
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/kiss") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gif_url = data.get('url', 'https://media.giphy.com/media/3o7qDSOvfaCO9b3MlO/giphy.gif')
                    else:
                        gif_url = 'https://media.giphy.com/media/3o7qDSOvfaCO9b3MlO/giphy.gif'
        except:
            gif_url = 'https://media.giphy.com/media/3o7qDSOvfaCO9b3MlO/giphy.gif'
        
        embed.set_image(url=gif_url)
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="slap")
    async def slap(self, ctx, user: discord.Member):
        """Slap someone with an anime gif"""
        if user == ctx.author:
            embed = discord.Embed(
                title="👋 Self Slap?",
                description="Why would you slap yourself? That's not very nice! 😅",
                color=0xff4444
            )
        elif user == self.bot.user:
            embed = discord.Embed(
                title="👋 Bot Slap",
                description=f"Ouch! {ctx.author.mention} slapped me! That wasn't very nice! 😢",
                color=0xff4444
            )
        else:
            embed = discord.Embed(
                title="👋 Slap",
                description=f"{ctx.author.mention} slaps {user.mention}! That must have hurt! 😵",
                color=0xff4444
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/slap") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gif_url = data.get('url', 'https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif')
                    else:
                        gif_url = 'https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif'
        except:
            gif_url = 'https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif'
        
        embed.set_image(url=gif_url)
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="kill")
    async def kill(self, ctx, user: discord.Member):
        """Playfully 'kill' someone with a funny anime gif"""
        if user == ctx.author:
            embed = discord.Embed(
                title="💀 Self Destruction?",
                description="You can't kill yourself! That's not allowed here! 😤",
                color=0x8b0000
            )
        elif user == self.bot.user:
            embed = discord.Embed(
                title="💀 Bot Assassination",
                description=f"NOOOO! {ctx.author.mention} killed me! I'll be back though! 👻",
                color=0x8b0000
            )
        else:
            embed = discord.Embed(
                title="💀 Elimination",
                description=f"{ctx.author.mention} eliminated {user.mention}! RIP! 💀⚰️",
                color=0x8b0000
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/pat") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gif_url = data.get('url', 'https://media.giphy.com/media/l2JhpjWPccQhsAMfu/giphy.gif')
                    else:
                        gif_url = 'https://media.giphy.com/media/l2JhpjWPccQhsAMfu/giphy.gif'
        except:
            gif_url = 'https://media.giphy.com/media/l2JhpjWPccQhsAMfu/giphy.gif'
        
        embed.set_image(url=gif_url)
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))