import discord
from discord.ext import commands

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.media_channels = {}  # guild_id: [channel_ids]
        self.bypass_roles = {}    # guild_id: [role_ids]
    
    @commands.hybrid_group(name="media")
    async def media_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"Media Filter — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            embed.add_field(
                name="Media Channel Management",
                value="`>media channel add <channel>` - Add media-only channel\n`>media channel remove <channel>` - Remove media channel\n`>media channel list` - View all media channels\n`>media channel reset` - Clear all media channels",
                inline=False
            )
            
            embed.add_field(
                name="Bypass Role Management",
                value="`>media bypass add <role>` - Add bypass role\n`>media bypass remove <role>` - Remove bypass role\n`>media bypass list` - View all bypass roles\n`>media bypass reset` - Clear all bypass roles",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @media_group.group(name="channel")
    async def media_channel(self, ctx):
        pass
    
    @media_channel.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def media_channel_add(self, ctx, channel: discord.TextChannel):
        """Add a media-only channel"""
        if ctx.guild.id not in self.media_channels:
            self.media_channels[ctx.guild.id] = []
        
        if channel.id not in self.media_channels[ctx.guild.id]:
            self.media_channels[ctx.guild.id].append(channel.id)
        
        embed = discord.Embed(
            title="Media Channel Added",
            description=f"{channel.mention} has been added as a media-only channel.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @media_channel.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def media_channel_remove(self, ctx, channel: discord.TextChannel):
        """Remove a media-only channel"""
        embed = discord.Embed(
            title="Media Channel Removed",
            description=f"{channel.mention} is no longer a media-only channel.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @media_channel.command(name="list")
    async def media_channel_list(self, ctx):
        """List all media-only channels"""
        embed = discord.Embed(
            title="Media-Only Channels",
            description="No media channels configured.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @media_channel.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def media_channel_reset(self, ctx):
        """Reset all media-only channels"""
        embed = discord.Embed(
            title="Media Channels Reset",
            description="All media-only channels have been cleared.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @media_group.group(name="bypass")
    async def media_bypass(self, ctx):
        pass
    
    @media_bypass.command(name="add")
    @commands.has_permissions(manage_roles=True)
    async def media_bypass_add(self, ctx, role: discord.Role):
        """Add a bypass role for media channels"""
        if ctx.guild.id not in self.bypass_roles:
            self.bypass_roles[ctx.guild.id] = []
        
        if role.id not in self.bypass_roles[ctx.guild.id]:
            self.bypass_roles[ctx.guild.id].append(role.id)
        
        embed = discord.Embed(
            title="Bypass Role Added",
            description=f"{role.mention} can now bypass media-only restrictions.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @media_bypass.command(name="remove")
    @commands.has_permissions(manage_roles=True)
    async def media_bypass_remove(self, ctx, role: discord.Role):
        """Remove a bypass role for media channels"""
        embed = discord.Embed(
            title="Bypass Role Removed",
            description=f"{role.mention} can no longer bypass media-only restrictions.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @media_bypass.command(name="list")
    async def media_bypass_list(self, ctx):
        """List all bypass roles"""
        embed = discord.Embed(
            title="Media Bypass Roles",
            description="No bypass roles configured.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @media_bypass.command(name="reset")
    @commands.has_permissions(manage_roles=True)
    async def media_bypass_reset(self, ctx):
        """Reset all bypass roles"""
        embed = discord.Embed(
            title="Bypass Roles Reset",
            description="All bypass roles have been cleared.",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        # Only filter in designated media channels
        if (message.guild.id in self.media_channels and 
            message.channel.id in self.media_channels[message.guild.id]):
            
            # Check if user has bypass role
            if message.guild.id in self.bypass_roles:
                for role_id in self.bypass_roles[message.guild.id]:
                    if any(role.id == role_id for role in message.author.roles):
                        return
            
            # Check if message has attachments (media) or embeds
            if not message.attachments and not message.embeds:
                try:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, this channel is for media only!", delete_after=3)
                except:
                    pass

async def setup(bot):
    await bot.add_cog(Media(bot))