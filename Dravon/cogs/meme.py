import discord
from discord.ext import commands
import aiohttp
import base64
import asyncio

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client_id = "5fUgyJz_xF4sgkrVWli7fA"
        self.client_secret = "yytZtqTTJln9Hjs1942L-8rUkBWUUA"
        self.access_token = None
        self.subreddits = ["memes", "dankmemes", "funny", "wholesomememes", "memeeconomy"]
    
    async def get_access_token(self):
        """Get Reddit API access token"""
        if self.access_token:
            return self.access_token
        
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "User-Agent": "DravonBot/1.0"
        }
        data = {"grant_type": "client_credentials"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://www.reddit.com/api/v1/access_token", 
                                  headers=headers, data=data) as resp:
                if resp.status == 200:
                    token_data = await resp.json()
                    self.access_token = token_data["access_token"]
                    return self.access_token
        return None
    
    async def fetch_meme(self):
        """Fetch a random meme from Reddit"""
        token = await self.get_access_token()
        if not token:
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "DravonBot/1.0"
        }
        
        import random
        # Randomize subreddit and sorting
        subreddit = random.choice(self.subreddits)
        sort_type = random.choice(["hot", "top", "new"])
        limit = random.randint(25, 100)
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://oauth.reddit.com/r/{subreddit}/{sort_type}.json?limit={limit}"
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        posts = data["data"]["children"]
                        
                        # Filter for image posts
                        image_posts = [
                            post["data"] for post in posts 
                            if not post["data"]["is_video"] 
                            and any(post["data"]["url"].endswith(ext) for ext in [".jpg", ".png", ".gif"])
                            and not post["data"]["over_18"]
                        ]
                        
                        if image_posts:
                            meme = random.choice(image_posts)
                            return {
                                "title": meme["title"],
                                "url": meme["url"]
                            }
        except:
            pass
        return None
    
    @commands.hybrid_command(name="meme")
    async def meme_command(self, ctx):
        """Fetch a random meme from Reddit"""
        
        # Loading message
        embed = discord.Embed(
            title="🎭 Fetching Meme...",
            description="Getting a fresh meme from Reddit...",
            color=0xffd700
        )
        message = await ctx.send(embed=embed)
        
        # Fetch meme
        meme = await self.fetch_meme()
        
        if not meme:
            embed = discord.Embed(
                title="❌ Meme Fetch Failed",
                description="Couldn't fetch a meme right now. Try again later!",
                color=0xff0000
            )
            await message.edit(embed=embed)
            return
        
        # Send meme title as normal message and image as embed
        await message.edit(content=meme["title"], embed=None)
        
        # Create simple image embed
        embed = discord.Embed(color=0x808080)
        embed.set_image(url=meme["url"])
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Meme(bot))