import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta
import re

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        
        if str(reaction.emoji) != "🎉":
            return
        
        # Check if this is a giveaway message
        giveaway = await self.bot.db.get_giveaway_by_message(reaction.message.id)
        if not giveaway:
            return
        
        if giveaway.get("ended", False):
            return
        
        if giveaway.get("paused", False):
            return
        
        # Check if user already joined
        if user.id in giveaway.get("participants", []):
            return
        
        # Add user to participants
        await self.bot.db.add_giveaway_participant(giveaway["id"], user.id)
    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        
        if str(reaction.emoji) != "🎉":
            return
        
        # Check if this is a giveaway message
        giveaway = await self.bot.db.get_giveaway_by_message(reaction.message.id)
        if not giveaway:
            return
        
        if giveaway.get("ended", False):
            return
        
        # Remove user from participants
        await self.bot.db.remove_giveaway_participant(giveaway["id"], user.id)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string like '1h', '30m', '2d' into timedelta"""
        pattern = r'(\d+)([smhd])'
        matches = re.findall(pattern, duration_str.lower())
        
        total_seconds = 0
        for amount, unit in matches:
            amount = int(amount)
            if unit == 's':
                total_seconds += amount
            elif unit == 'm':
                total_seconds += amount * 60
            elif unit == 'h':
                total_seconds += amount * 3600
            elif unit == 'd':
                total_seconds += amount * 86400
        
        return timedelta(seconds=total_seconds)
    
    @commands.hybrid_group(name="giveaway")
    async def giveaway_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use giveaway commands like `giveaway create`, `giveaway list`, etc.")
    
    @giveaway_group.command(name="create")
    @app_commands.describe(
        prize="The prize for the giveaway",
        duration="Duration (e.g., 1h, 30m, 2d)",
        winners="Number of winners",
        channel="Channel to host the giveaway"
    )
    async def create_giveaway(self, ctx, prize: str, duration: str, winners: int, channel: discord.TextChannel = None):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to create giveaways.")
            return
        
        if channel is None:
            channel = ctx.channel
        
        try:
            duration_delta = self.parse_duration(duration)
            if duration_delta.total_seconds() < 60:
                await ctx.send("Duration must be at least 1 minute.")
                return
        except:
            await ctx.send("Invalid duration format. Use format like '1h', '30m', '2d'.")
            return
        
        if winners < 1:
            await ctx.send("Number of winners must be at least 1.")
            return
        
        # Create giveaway
        end_time = datetime.utcnow() + duration_delta
        giveaway_id = f"{ctx.guild.id}_{int(datetime.utcnow().timestamp())}"
        
        embed = discord.Embed(
            title="🎉 **GIVEAWAY** 🎉",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{int(end_time.timestamp())}:R>\n**Hosted by:** {ctx.author.mention}\n\nReact with 🎉 to enter!",
            color=0x00ff00
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413084513600405565/51ffee9c-e922-4b90-8d42-562d407afee6.jpg")
        embed.set_footer(text="Powered By Dravon", icon_url=self.bot.user.display_avatar.url)
        
        message = await channel.send(embed=embed)
        await message.add_reaction("🎉")
        
        # Save giveaway to database
        giveaway_data = {
            "id": giveaway_id,
            "guild_id": ctx.guild.id,
            "channel_id": channel.id,
            "message_id": message.id,
            "prize": prize,
            "winners": winners,
            "end_time": end_time,
            "host_id": ctx.author.id,
            "participants": [],
            "ended": False,
            "paused": False
        }
        
        await self.bot.db.create_giveaway(giveaway_data)
        
        # Schedule giveaway end
        asyncio.create_task(self.schedule_giveaway_end(giveaway_id, duration_delta.total_seconds()))
        
        await ctx.send(f"✅ Giveaway created in {channel.mention}!")
    
    async def schedule_giveaway_end(self, giveaway_id: str, delay: float):
        """Schedule giveaway to end after delay"""
        await asyncio.sleep(delay)
        await self.end_giveaway_task(giveaway_id)
    
    async def end_giveaway_task(self, giveaway_id: str):
        """End giveaway and select winners"""
        giveaway = await self.bot.db.get_giveaway(giveaway_id)
        if not giveaway or giveaway.get("ended", False):
            return
        
        participants = giveaway.get("participants", [])
        winners_count = giveaway["winners"]
        
        if len(participants) == 0:
            # No participants
            embed = discord.Embed(
                title="🎉 **GIVEAWAY ENDED** 🎉",
                description=f"**Prize:** {giveaway['prize']}\n**Winners:** No participants\n**Entries:** 0\n\nNo one entered this giveaway!",
                color=0xff0000
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413084513600405565/51ffee9c-e922-4b90-8d42-562d407afee6.jpg")
            embed.set_footer(text="Powered By Dravon", icon_url=self.bot.user.display_avatar.url)
        else:
            # Select winners
            actual_winners = min(winners_count, len(participants))
            winners = random.sample(participants, actual_winners)
            
            winner_mentions = [f"<@{winner_id}>" for winner_id in winners]
            
            embed = discord.Embed(
                title="🎉 **GIVEAWAY ENDED** 🎉",
                description=f"**Prize:** {giveaway['prize']}\n**Winner{'s' if len(winners) > 1 else ''}:** {', '.join(winner_mentions)}\n**Entries:** {len(participants)}\n**Hosted by:** <@{giveaway['host_id']}>\n\nCongratulations!",
                color=0x00ff00
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413084513600405565/51ffee9c-e922-4b90-8d42-562d407afee6.jpg")
            embed.set_footer(text="Powered By Dravon", icon_url=self.bot.user.display_avatar.url)
        
        # Update message
        try:
            guild = self.bot.get_guild(giveaway["guild_id"])
            channel = guild.get_channel(giveaway["channel_id"])
            message = await channel.fetch_message(giveaway["message_id"])
            
            await message.edit(embed=embed)
            await message.clear_reactions()
            
            if len(participants) > 0:
                await channel.send(f"🎉 Congratulations {', '.join(winner_mentions)}! You won **{giveaway['prize']}**!")
        except:
            pass
        
        # Mark as ended
        await self.bot.db.end_giveaway(giveaway_id)
    
    @giveaway_group.command(name="end")
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def end_giveaway(self, ctx, message_id: str):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to end giveaways.")
            return
        
        # Find giveaway by message ID
        giveaway = await self.bot.db.get_giveaway_by_message(int(message_id))
        if not giveaway:
            await ctx.send("Giveaway not found.")
            return
        
        if giveaway.get("ended", False):
            await ctx.send("This giveaway has already ended.")
            return
        
        await self.end_giveaway_task(giveaway["id"])
        await ctx.send("✅ Giveaway ended successfully!")
    
    @giveaway_group.command(name="reroll")
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def reroll_giveaway(self, ctx, message_id: str):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to reroll giveaways.")
            return
        
        giveaway = await self.bot.db.get_giveaway_by_message(int(message_id))
        if not giveaway:
            await ctx.send("Giveaway not found.")
            return
        
        if not giveaway.get("ended", False):
            await ctx.send("This giveaway hasn't ended yet.")
            return
        
        participants = giveaway.get("participants", [])
        if len(participants) == 0:
            await ctx.send("No participants to reroll.")
            return
        
        # Select new winners
        winners_count = giveaway["winners"]
        actual_winners = min(winners_count, len(participants))
        winners = random.sample(participants, actual_winners)
        winner_mentions = [f"<@{winner_id}>" for winner_id in winners]
        
        embed = discord.Embed(
            title="🎉 **GIVEAWAY REROLLED** 🎉",
            description=f"**Prize:** {giveaway['prize']}\n**New Winner{'s' if len(winners) > 1 else ''}:** {', '.join(winner_mentions)}\n**Entries:** {len(participants)}\n**Rerolled by:** {ctx.author.mention}\n\nCongratulations!",
            color=0x00ff00
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413084513600405565/51ffee9c-e922-4b90-8d42-562d407afee6.jpg")
        embed.set_footer(text="Powered By Dravon", icon_url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
        await ctx.send(f"🎉 Congratulations {', '.join(winner_mentions)}! You won **{giveaway['prize']}**!")
    
    @giveaway_group.command(name="list")
    async def list_giveaways(self, ctx):
        giveaways = await self.bot.db.get_guild_giveaways(ctx.guild.id)
        
        if not giveaways:
            await ctx.send("No giveaways found for this server.")
            return
        
        embed = discord.Embed(
            title="🎉 Server Giveaways",
            color=0x7289da
        )
        
        for giveaway in giveaways[:10]:  # Limit to 10
            status = "🔴 Ended" if giveaway.get("ended") else "⏸️ Paused" if giveaway.get("paused") else "🟢 Active"
            embed.add_field(
                name=f"{giveaway['prize']}",
                value=f"**Status:** {status}\n**Winners:** {giveaway['winners']}\n**ID:** {giveaway['id']}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @giveaway_group.command(name="delete")
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def delete_giveaway(self, ctx, message_id: str):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to delete giveaways.")
            return
        
        giveaway = await self.bot.db.get_giveaway_by_message(int(message_id))
        if not giveaway:
            await ctx.send("Giveaway not found.")
            return
        
        # Delete message
        try:
            channel = self.bot.get_channel(giveaway["channel_id"])
            message = await channel.fetch_message(giveaway["message_id"])
            await message.delete()
        except:
            pass
        
        # Delete from database
        await self.bot.db.delete_giveaway(giveaway["id"])
        await ctx.send("✅ Giveaway deleted successfully!")
    
    @giveaway_group.command(name="pause")
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def pause_giveaway(self, ctx, message_id: str):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to pause giveaways.")
            return
        
        giveaway = await self.bot.db.get_giveaway_by_message(int(message_id))
        if not giveaway:
            await ctx.send("Giveaway not found.")
            return
        
        if giveaway.get("ended", False):
            await ctx.send("Cannot pause an ended giveaway.")
            return
        
        await self.bot.db.pause_giveaway(giveaway["id"], True)
        await ctx.send("⏸️ Giveaway paused successfully!")
    
    @giveaway_group.command(name="resume")
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def resume_giveaway(self, ctx, message_id: str):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to resume giveaways.")
            return
        
        giveaway = await self.bot.db.get_giveaway_by_message(int(message_id))
        if not giveaway:
            await ctx.send("Giveaway not found.")
            return
        
        if giveaway.get("ended", False):
            await ctx.send("Cannot resume an ended giveaway.")
            return
        
        await self.bot.db.pause_giveaway(giveaway["id"], False)
        await ctx.send("▶️ Giveaway resumed successfully!")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))