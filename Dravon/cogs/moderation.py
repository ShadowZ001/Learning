import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server"""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**{member}** has been kicked.\n**Reason:** {reason}",
                color=0x808080
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to kick member: {str(e)}")
    
    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server"""
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member}** has been banned.\n**Reason:** {reason}",
                color=0x808080
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to ban member: {str(e)}")
    
    @commands.hybrid_command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="No reason provided"):
        """Unban a user from the server"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f"**{user}** has been unbanned.\n**Reason:** {reason}",
                color=0x808080
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to unban user: {str(e)}")
    
    @commands.hybrid_command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 60, *, reason="No reason provided"):
        """Timeout a member"""
        try:
            await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=duration), reason=reason)
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**{member}** has been muted for **{duration} minutes**.\n**Reason:** {reason}",
                color=0x808080
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to mute member: {str(e)}")
    
    @commands.hybrid_command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Remove timeout from a member"""
        try:
            await member.timeout(None, reason=reason)
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**{member}** has been unmuted.\n**Reason:** {reason}",
                color=0x808080
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to unmute member: {str(e)}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))