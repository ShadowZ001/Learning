import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class InviteSetupView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select the channel for invite messages...", channel_types=[discord.ChannelType.text])
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        
        # Save to database
        await self.bot.db.set_invite_logs_channel(self.guild.id, channel.id)
        
        embed = discord.Embed(
            title="✅ Invite Setup Complete",
            description=f"Invite join messages will now be sent to {channel.mention}",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        
        await interaction.response.edit_message(embed=embed, view=None)

class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}  # Cache invites for tracking
    
    async def cog_load(self):
        """Cache all guild invites on startup"""
        for guild in self.bot.guilds:
            try:
                invites = await guild.invites()
                self.invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
            except:
                self.invite_cache[guild.id] = {}
    
    @commands.hybrid_command(name="inviteinfo")
    async def invite_info(self, ctx):
        """Show invite system information"""
        embed = discord.Embed(
            title="🎟️ Invite System",
            description="**Track server invites and see who's bringing new members!**\n\n**Available Commands:**\n• `/invitesetup` - Configure invite logging\n• `/invites <user>` - Check user's invite stats\n• `/inviteboard` - View invite leaderboard",
            color=0x7289da
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="invitesetup")
    @commands.has_permissions(manage_guild=True)
    async def invite_setup(self, ctx):
        """Set up where invite join messages will be sent"""
        embed = discord.Embed(
            title="🎟️ Invite Setup",
            description="Select the channel where invite join messages should be sent.",
            color=0x7289da
        )
        embed = add_dravon_footer(embed)
        
        view = InviteSetupView(self.bot, ctx.guild)
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="invites")
    async def invites_command(self, ctx, user: discord.Member = None):
        """Check how many invites a specific user has"""
        if user is None:
            user = ctx.author
        
        # Get user invite data from database
        invite_data = await self.bot.db.get_user_invites(ctx.guild.id, user.id)
        
        if not invite_data:
            invite_data = {"total": 0, "joins": 0, "leaves": 0, "bonus": 0}
        
        embed = discord.Embed(
            title=f"**{user.display_name}**",
            color=user.color if hasattr(user, 'color') else 0x7289da
        )
        
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        
        embed.add_field(
            name="✨ Invites",
            value=str(invite_data.get("total", 0)),
            inline=True
        )
        
        embed.add_field(
            name="👥 Joins",
            value=str(invite_data.get("joins", 0)),
            inline=True
        )
        
        embed.add_field(
            name="❌ Leaves",
            value=str(invite_data.get("leaves", 0)),
            inline=True
        )
        
        embed.add_field(
            name="🎁 Bonus",
            value=str(invite_data.get("bonus", 0)),
            inline=True
        )
        
        embed.set_footer(text="Track your invites and climb the leaderboard!")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="inviteboard")
    async def invite_board(self, ctx):
        """Shows a leaderboard of top inviters in the server"""
        # Get all invite data for the guild
        all_invites = await self.bot.db.get_guild_invites(ctx.guild.id)
        
        if not all_invites or len(all_invites) == 0:
            embed = discord.Embed(
                title="📊 Invite Leaderboard",
                description="No invite data found for this server. Start inviting members to see the leaderboard!",
                color=0x7289da
            )
            await ctx.send(embed=embed)
            return
        
        # Sort users by total invites
        sorted_users = sorted(all_invites.items(), key=lambda x: x[1].get("total", 0), reverse=True)
        
        # Create leaderboard description
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, data) in enumerate(sorted_users[:10]):
            user = ctx.guild.get_member(int(user_id))
            if user:
                medal = medals[i] if i < 3 else f"{i+1}."
                invites = data.get("total", 0)
                leaderboard_text += f"{medal} {user.display_name} — {invites}\n"
        
        if not leaderboard_text:
            leaderboard_text = "No active inviters found."
        
        embed = discord.Embed(
            title=f"📊 {ctx.guild.name} Invite Leaderboard",
            description=leaderboard_text,
            color=0x7289da
        )
        
        # Add user's personal stats
        user_data = all_invites.get(str(ctx.author.id), {"total": 0})
        user_rank = next((i+1 for i, (uid, _) in enumerate(sorted_users) if uid == str(ctx.author.id)), "Unranked")
        user_invites = user_data.get("total", 0)
        total_inviters = len(sorted_users)
        total_invites = sum(data.get("total", 0) for data in all_invites.values())
        
        embed.add_field(
            name="📈 Your Stats",
            value=f"**Your Rank:** {user_rank}\n**Your Invites:** {user_invites}\n**Total Inviters:** {total_inviters}\n**Total Invites in Server:** {total_invites}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_group(name="invite")
    async def invite_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🎟️ Invite Management",
                description="**Manage server invites**\n\n**Commands:**\n• `/invites <user>` - Check invite stats\n• `/invite add <user> <amount>` - Add bonus invites\n• `/invite remove <user> <amount>` - Remove invites\n• `/invite clear <user>` - Reset user invites\n• `/invite resetall` - Reset all invites",
                color=0x7289da
            )
            await ctx.send(embed=embed)
    
    @invite_group.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def invites_add(self, ctx, user: discord.Member, amount: int):
        """Give bonus invites to a user"""
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!", ephemeral=True)
            return
        
        await self.bot.db.add_user_bonus_invites(ctx.guild.id, user.id, amount)
        await ctx.send(f"✅ Added {amount} bonus invites to {user.mention}!", ephemeral=True)
    
    @invite_group.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def invites_remove(self, ctx, user: discord.Member, amount: int):
        """Remove invites from a user"""
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!", ephemeral=True)
            return
        
        await self.bot.db.remove_user_invites(ctx.guild.id, user.id, amount)
        await ctx.send(f"✅ Removed {amount} invites from {user.mention}!", ephemeral=True)
    
    @invite_group.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def invites_clear(self, ctx, user: discord.Member):
        """Reset a user's invites to 0"""
        await self.bot.db.clear_user_invites(ctx.guild.id, user.id)
        await ctx.send(f"✅ Cleared all invites for {user.mention}!", ephemeral=True)
    
    @invite_group.command(name="resetall")
    @commands.has_permissions(administrator=True)
    async def invites_resetall(self, ctx):
        """Reset the entire server's invites"""
        await self.bot.db.clear_guild_invites(ctx.guild.id)
        await ctx.send("✅ Reset all invites for this server!", ephemeral=True)
    
    @invite_group.command(name="test")
    @commands.has_permissions(manage_guild=True)
    async def invite_test(self, ctx):
        """Test invite tracking system"""
        logs_channel_id = await self.bot.db.get_invite_logs_channel(ctx.guild.id)
        if not logs_channel_id:
            await ctx.send("❌ No invite logs channel configured! Use `/invitesetup` first.", ephemeral=True)
            return
        
        logs_channel = ctx.guild.get_channel(logs_channel_id)
        if not logs_channel:
            await ctx.send("❌ Invite logs channel not found!", ephemeral=True)
            return
        
        # Send test message
        test_message = f"✛ {ctx.author.mention} joined the server invited by @TestUser now has (5)\n✛ {ctx.guild.name} now has {ctx.guild.member_count} members"
        await logs_channel.send(test_message)
        await ctx.send(f"✅ Test message sent to {logs_channel.mention}!", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track when someone joins via invite"""
        guild = member.guild
        
        # Get invite logs channel
        logs_channel_id = await self.bot.db.get_invite_logs_channel(guild.id)
        if not logs_channel_id:
            return
        
        logs_channel = guild.get_channel(logs_channel_id)
        if not logs_channel:
            return
        
        try:
            # Get current invites
            current_invites = await guild.invites()
            current_invite_dict = {invite.code: invite.uses for invite in current_invites}
            
            # Compare with cached invites to find which was used
            cached_invites = self.invite_cache.get(guild.id, {})
            used_invite = None
            inviter = None
            
            for code, uses in current_invite_dict.items():
                if code in cached_invites and uses > cached_invites[code]:
                    # This invite was used
                    used_invite = next((inv for inv in current_invites if inv.code == code), None)
                    if used_invite:
                        inviter = used_invite.inviter
                    break
            
            # Update cache
            self.invite_cache[guild.id] = current_invite_dict
            
            if inviter:
                # Update inviter's stats in database
                await self.bot.db.add_user_invites(guild.id, inviter.id, 1)
                
                # Get updated invite count
                invite_data = await self.bot.db.get_user_invites(guild.id, inviter.id)
                total_invites = invite_data.get("total", 1) if invite_data else 1
                
                # Send join message
                message = f"✛ {member.mention} joined the server invited by {inviter.mention} now has ({total_invites})\n✛ {guild.name} now has {guild.member_count} members"
                await logs_channel.send(message)
            else:
                # Unknown invite source
                message = f"✛ {member.display_name} joined the server\n✛ {guild.name} now has {guild.member_count} members"
                await logs_channel.send(message)
                
        except Exception as e:
            print(f"Error tracking invite: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Track when someone leaves (reduce inviter's count)"""
        guild = member.guild
        
        try:
            # Find who invited this member (this would require storing join data)
            # For now, we'll just update the cache
            invites = await guild.invites()
            self.invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Cache invites when bot joins a guild"""
        try:
            invites = await guild.invites()
            self.invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
        except:
            self.invite_cache[guild.id] = {}
    
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """Update cache when new invite is created"""
        if invite.guild.id not in self.invite_cache:
            self.invite_cache[invite.guild.id] = {}
        self.invite_cache[invite.guild.id][invite.code] = invite.uses
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """Update cache when invite is deleted"""
        if invite.guild.id in self.invite_cache:
            self.invite_cache[invite.guild.id].pop(invite.code, None)

async def setup(bot):
    await bot.add_cog(Invites(bot))