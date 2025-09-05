import discord
from discord.ext import commands
from discord import app_commands

class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}
    
    @commands.hybrid_command(name="invites")
    @app_commands.describe(user="The user to check invites for")
    async def invites(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
        try:
            invites = await ctx.guild.invites()
            user_invites = [invite for invite in invites if invite.inviter == user]
            total_uses = sum(invite.uses for invite in user_invites)
        except discord.Forbidden:
            await ctx.send("I don't have permission to view invites in this server.")
            return
        
        embed = discord.Embed(
            title=f"📊 Invite Statistics",
            description=f"➡️ **{user.display_name}** has **{total_uses}** invites\n\n" +
                       f"**📈 Joins:** {total_uses}\n" +
                       f"**📉 Left:** 0\n" +
                       f"**🚫 Fake:** 0\n" +
                       f"**🔄 Rejoins:** 0\n\n" +
                       f"➡️ **Need Support** - support",
            color=0x00ff00
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_group(name="invite")
    async def invite_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `invite tracking channel set <channel>` or `invite test` commands.")
    
    @invite_group.group(name="tracking")
    async def tracking_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `invite tracking channel set <channel>` to setup invite tracking.")
    
    @tracking_group.command(name="channel")
    @app_commands.describe(action="Use 'set' to configure", channel="The channel to send invite tracking messages")
    async def tracking_channel(self, ctx, action: str, channel: discord.TextChannel = None):
        if action.lower() != "set":
            await ctx.send("Use `invite tracking channel set <channel>` to setup invite tracking.")
            return
        
        if not channel:
            await ctx.send("Please specify a channel: `invite tracking channel set <channel>`")
            return
        
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        # Save tracking channel to database
        config = {"tracking_channel": channel.id}
        await self.bot.db.set_invite_config(ctx.guild.id, config)
        
        # Cache current invites
        try:
            invites = await ctx.guild.invites()
            self.invite_cache[ctx.guild.id] = {invite.code: invite.uses for invite in invites}
        except discord.Forbidden:
            pass
        
        await ctx.send(f"✅ Invite tracking has been set to {channel.mention}")
    
    @invite_group.command(name="test")
    async def test_tracking(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        # Get tracking config
        config = await self.bot.db.get_invite_config(ctx.guild.id)
        if not config or not config.get("tracking_channel"):
            await ctx.send("❌ Invite tracking is not set up. Use `invite tracking channel set <channel>` first.")
            return
        
        tracking_channel = self.bot.get_channel(config["tracking_channel"])
        if not tracking_channel:
            await ctx.send("❌ Tracking channel not found. Please reconfigure invite tracking.")
            return
        
        # Send test message
        test_message = f"📥 **{ctx.author.display_name}** joined using **Test User**'s invite (`TEST123`) - This is a test message"
        await tracking_channel.send(test_message)
        await ctx.send(f"✅ Test message sent to {tracking_channel.mention}")
    
    @invite_group.command(name="config")
    async def tracking_config(self, ctx):
        config = await self.bot.db.get_invite_config(ctx.guild.id)
        
        if not config or not config.get("tracking_channel"):
            embed = discord.Embed(
                title="📋 Invite Tracking Configuration",
                description="Invite tracking is not configured for this server.",
                color=0x7289da
            )
        else:
            tracking_channel = self.bot.get_channel(config["tracking_channel"])
            channel_mention = tracking_channel.mention if tracking_channel else "Channel not found"
            
            embed = discord.Embed(
                title="📋 Invite Tracking Configuration",
                description=f"**Status:** ✅ Active\n**Tracking Channel:** {channel_mention}\n**Features:** Member joins, Vanity URL detection",
                color=0x00ff00
            )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        
        # Get tracking config
        config = await self.bot.db.get_invite_config(guild.id)
        if not config or not config.get("tracking_channel"):
            return
        
        tracking_channel = self.bot.get_channel(config["tracking_channel"])
        if not tracking_channel:
            return
        
        try:
            # Get current invites
            current_invites = await guild.invites()
            current_invite_dict = {invite.code: invite.uses for invite in current_invites}
            
            # Compare with cached invites
            cached_invites = self.invite_cache.get(guild.id, {})
            
            inviter = None
            invite_code = None
            
            # Find which invite was used
            for code, uses in current_invite_dict.items():
                if code in cached_invites and uses > cached_invites[code]:
                    # Find the invite object
                    for invite in current_invites:
                        if invite.code == code:
                            inviter = invite.inviter
                            invite_code = code
                            break
                    break
            
            # Update cache
            self.invite_cache[guild.id] = current_invite_dict
            
            # Send tracking message
            if inviter:
                message = f"📥 **{member.display_name}** joined using **{inviter.display_name}**'s invite (`{invite_code}`)"
            else:
                # Check for vanity URL
                if guild.vanity_url_code:
                    message = f"📥 **{member.display_name}** joined using **Vanity URL** (`{guild.vanity_url_code}`)"
                else:
                    message = f"📥 **{member.display_name}** joined but I couldn't determine the invite used"
            
            await tracking_channel.send(message)
            
        except discord.Forbidden:
            pass



async def setup(bot):
    await bot.add_cog(Invites(bot))