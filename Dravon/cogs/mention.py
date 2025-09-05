import discord
from discord.ext import commands
import random

class Mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = [
            "👋 Hey there! I'm **Dravon Bot** - your all-in-one Discord server management solution! Use `>help` to get started.",
            "🎵 Looking for music? Try `>play <song>` to start jamming! Premium users get Spotify access too!",
            "🛡️ Need security? My AntiNuke v6.0 system protects your server 24/7. Use `>antinuke enable` to get started!",
            "🎫 Want a ticket system? Set up professional support with `>ticket panel` - it's super easy!",
            "📊 Track your server activity with my level system! Use `>levels enable` to start rewarding active members.",
            "⚡ Premium users can use commands without prefix! Get premium access in our support server.",
            "🎮 I'm packed with features: moderation, music, security, tickets, levels, and so much more!",
            "👑 Created by the amazing Dravon team! Join our support server for help and updates.",
            "🚀 Over 1000+ servers trust me for their management needs. Want to see why? Try `>serverinfo`!",
            "💎 From basic moderation to advanced security - I've got everything your server needs!",
            "🎯 Quick start: `>help` for commands, `>docs` for full documentation, or join our support server!",
            "🔥 New to Discord bots? No worries! I'm designed to be user-friendly with step-by-step guides.",
            "🌟 Fun fact: I can play music from YouTube, Spotify (premium), and even handle 24/7 streaming!",
            "⚙️ My AutoMod keeps your chat clean while my AntiNuke protects against raids and nukes!",
            "📈 Want to boost engagement? My level system with custom rewards will keep your members active!"
        ]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            response = random.choice(self.responses)
            embed = discord.Embed(
                description=response,
                color=0x58a6ff
            )
            embed.set_author(
                name="Dravon Bot",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            embed.add_field(
                name="🔗 Quick Links",
                value="[Support Server](https://discord.gg/UKR78VcEtg) • [Documentation](https://dravon-docs.netlify.app) • [Invite Me](https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot)",
                inline=False
            )
            embed.set_footer(text="Use >help for commands • >docs for documentation")
            
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mention(bot))