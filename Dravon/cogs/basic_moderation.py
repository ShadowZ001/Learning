import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import re

def parse_time(time_str):
    """Parse time string like '1h', '30m', '2d' into seconds"""
    if not time_str:
        return None
    
    time_regex = re.compile(r'(\d+)([smhd])')
    matches = time_regex.findall(time_str.lower())
    
    if not matches:
        return None
    
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
    
    return total_seconds

class BasicModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def send_dm(self, user, embed):
        """Send DM to user with error handling"""
        try:
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            return False
        except Exception:
            return False
    
    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_command(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a member from the server"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot kick someone with a higher or equal role!", ephemeral=True)
            return
        
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot kick someone with a higher or equal role than me!", ephemeral=True)
            return
        
        # Send DM to user
        dm_embed = discord.Embed(
            title="🦶 You have been kicked",
            description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
            color=0xff9500
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        dm_sent = await self.send_dm(member, dm_embed)
        
        try:
            await member.kick(reason=f"Kicked by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ Member Kicked",
                description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**DM Sent:** {'✅' if dm_sent else '❌'}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to kick member: {str(e)}", ephemeral=True)
    
    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_command(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a member from the server"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot ban someone with a higher or equal role!", ephemeral=True)
            return
        
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot ban someone with a higher or equal role than me!", ephemeral=True)
            return
        
        # Send DM to user
        dm_embed = discord.Embed(
            title="🔨 You have been banned",
            description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
            color=0xff0000
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        dm_sent = await self.send_dm(member, dm_embed)
        
        try:
            await member.ban(reason=f"Banned by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ Member Banned",
                description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**DM Sent:** {'✅' if dm_sent else '❌'}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to ban member: {str(e)}", ephemeral=True)
    
    @commands.hybrid_command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute_command(self, ctx, member: discord.Member, time: str, *, reason: str = "No reason provided"):
        """Mute a member for a specified time"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot mute someone with a higher or equal role!", ephemeral=True)
            return
        
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot mute someone with a higher or equal role than me!", ephemeral=True)
            return
        
        # Parse time
        duration = parse_time(time)
        if not duration:
            await ctx.send("❌ Invalid time format! Use formats like: 1h, 30m, 2d", ephemeral=True)
            return
        
        if duration > 2419200:  # 28 days max
            await ctx.send("❌ Maximum mute duration is 28 days!", ephemeral=True)
            return
        
        # Calculate end time
        end_time = datetime.utcnow() + timedelta(seconds=duration)
        
        # Send DM to user
        dm_embed = discord.Embed(
            title="🔇 You have been muted",
            description=f"**Server:** {ctx.guild.name}\n**Duration:** {time}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}\n**Ends:** <t:{int(end_time.timestamp())}:F>",
            color=0xffaa00
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        dm_sent = await self.send_dm(member, dm_embed)
        
        try:
            await member.timeout(end_time, reason=f"Muted by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ Member Muted",
                description=f"**Member:** {member.mention}\n**Duration:** {time}\n**Reason:** {reason}\n**Ends:** <t:{int(end_time.timestamp())}:F>\n**DM Sent:** {'✅' if dm_sent else '❌'}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to mute this member!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to mute member: {str(e)}", ephemeral=True)
    
    @commands.hybrid_command(name="tempmute")
    @commands.has_permissions(moderate_members=True)
    async def tempmute_command(self, ctx, member: discord.Member, time: str, *, reason: str = "No reason provided"):
        """Temporarily mute a member (alias for mute)"""
        await self.mute_command(ctx, member, time, reason=reason)
    
    @commands.hybrid_command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_command(self, ctx, user_id: str, *, reason: str = "No reason provided"):
        """Unban a user from the server"""
        try:
            user_id = int(user_id)
            user = await self.bot.fetch_user(user_id)
        except:
            await ctx.send("❌ Invalid user ID!", ephemeral=True)
            return
        
        try:
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f"**Member:** {user.mention}\n**Reason:** {reason}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except discord.NotFound:
            await ctx.send("❌ User is not banned!", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban this user!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to unban user: {str(e)}", ephemeral=True)
    
    @commands.hybrid_command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute_command(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Unmute a member"""
        if not member.is_timed_out():
            await ctx.send("❌ This member is not muted!", ephemeral=True)
            return
        
        try:
            await member.timeout(None, reason=f"Unmuted by {ctx.author} | {reason}")
            
            embed = discord.Embed(
                title="✅ Member Unmuted",
                description=f"**Member:** {member.mention}\n**Reason:** {reason}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute this member!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to unmute member: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BasicModeration(bot))