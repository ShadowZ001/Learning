import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="delrole")
    @app_commands.describe(role="The role to delete")
    async def delete_role(self, ctx, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You need 'Manage Roles' permission to use this command.")
            return
        
        if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot delete a role higher than or equal to your highest role.")
            return
        
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("I cannot delete a role higher than or equal to my highest role.")
            return
        
        try:
            role_name = role.name
            await role.delete(reason=f"Role deleted by {ctx.author}")
            
            embed = discord.Embed(
                title="🗑️ Role Deleted",
                description=f"Successfully deleted role **{role_name}**",
                color=0xff0000
            )
            embed.set_footer(text=f"Deleted by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete this role.")
        except discord.HTTPException:
            await ctx.send("Failed to delete the role.")
    
    @commands.hybrid_command(name="nick")
    @app_commands.describe(nickname="The new nickname", user="The user to change nickname for")
    async def change_nickname(self, ctx, nickname: str, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
        # Check permissions
        if user != ctx.author:
            if not ctx.author.guild_permissions.manage_nicknames:
                await ctx.send("You need 'Manage Nicknames' permission to change other users' nicknames.")
                return
            
            if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                await ctx.send("You cannot change the nickname of someone with a higher or equal role.")
                return
        
        if user.top_role.position >= ctx.guild.me.top_role.position:
            await ctx.send("I cannot change the nickname of someone with a higher or equal role than me.")
            return
        
        try:
            old_nick = user.display_name
            await user.edit(nick=nickname, reason=f"Nickname changed by {ctx.author}")
            
            embed = discord.Embed(
                title="✏️ Nickname Changed",
                description=f"Changed {user.mention}'s nickname\n**From:** {old_nick}\n**To:** {nickname}",
                color=0x00ff00
            )
            embed.set_footer(text=f"Changed by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to change this user's nickname.")
        except discord.HTTPException:
            await ctx.send("Failed to change the nickname.")
    
    @commands.hybrid_command(name="clearwarn")
    @app_commands.describe(user="The user to clear warnings for")
    async def clear_warnings(self, ctx, user: discord.Member):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You need 'Manage Messages' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="✅ Warnings Cleared",
            description=f"Cleared all warnings for {user.mention}",
            color=0x00ff00
        )
        embed.set_footer(text=f"Cleared by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.hybrid_group(name="role")
    async def role_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `role add <user> <role>` or `role remove <user> <role>`")
    
    @role_group.command(name="add")
    @app_commands.describe(user="The user to add role to", role="The role to add")
    async def add_role(self, ctx, user: discord.Member, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You need 'Manage Roles' permission to use this command.")
            return
        
        if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot assign a role higher than or equal to your highest role.")
            return
        
        if role in user.roles:
            await ctx.send(f"{user.mention} already has the {role.mention} role.")
            return
        
        try:
            await user.add_roles(role, reason=f"Role added by {ctx.author}")
            embed = discord.Embed(
                title="➕ Role Added",
                description=f"Added {role.mention} to {user.mention}",
                color=0x00ff00
            )
            embed.set_footer(text=f"Added by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I don't have permission to add this role.")
    
    @role_group.command(name="remove")
    @app_commands.describe(user="The user to remove role from", role="The role to remove")
    async def remove_role(self, ctx, user: discord.Member, role: discord.Role):
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You need 'Manage Roles' permission to use this command.")
            return
        
        if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot remove a role higher than or equal to your highest role.")
            return
        
        if role not in user.roles:
            await ctx.send(f"{user.mention} doesn't have the {role.mention} role.")
            return
        
        try:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
            embed = discord.Embed(
                title="➖ Role Removed",
                description=f"Removed {role.mention} from {user.mention}",
                color=0xff0000
            )
            embed.set_footer(text=f"Removed by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I don't have permission to remove this role.")
    
    @commands.hybrid_command(name="addemote")
    @app_commands.describe(name="The name for the emoji", image="Image URL or attach an image file")
    async def add_emote(self, ctx, name: str, image: str = None):
        if not ctx.author.guild_permissions.manage_emojis:
            await ctx.send("You need 'Manage Emojis' permission to use this command.")
            return
        
        try:
            if ctx.message.attachments:
                image_data = await ctx.message.attachments[0].read()
            elif image:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(image) as resp:
                        image_data = await resp.read()
            else:
                await ctx.send("Please provide an image URL or attach an image file.")
                return
            
            emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data, reason=f"Emoji added by {ctx.author}")
            
            embed = discord.Embed(
                title="😀 Emoji Added",
                description=f"Added emoji {emoji} with name `{name}`",
                color=0x00ff00
            )
            embed.set_footer(text=f"Added by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to add emojis.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to add emoji: {e}")
    
    @commands.hybrid_command(name="avatar")
    @app_commands.describe(user="The user to get avatar of")
    async def avatar(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
        embed = discord.Embed(
            title=f"{user.display_name}'s Avatar",
            color=0x7289da
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="banner")
    @app_commands.describe(user="The user to get banner of")
    async def banner(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
        # Fetch user to get banner
        user_obj = await self.bot.fetch_user(user.id)
        
        if user_obj.banner:
            embed = discord.Embed(
                title=f"{user.display_name}'s Banner",
                color=0x7289da
            )
            embed.set_image(url=user_obj.banner.url)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        else:
            embed = discord.Embed(
                title=f"{user.display_name}'s Banner",
                description="This user doesn't have a banner.",
                color=0x7289da
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mc")
    async def member_count(self, ctx):
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"👥 {guild.name} Members",
            description=f"**Total Members:** {guild.member_count}",
            color=0x7289da
        )
        
        online = len([m for m in guild.members if m.status != discord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = guild.member_count - bots
        
        embed.add_field(name="🟢 Online", value=online, inline=True)
        embed.add_field(name="👤 Humans", value=humans, inline=True)
        embed.add_field(name="🤖 Bots", value=bots, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="color")
    @app_commands.describe(hex_color="Hex color code (e.g., #ff0000)")
    async def color(self, ctx, hex_color: str):
        if not hex_color.startswith("#"):
            hex_color = "#" + hex_color
        
        try:
            color_int = int(hex_color.replace("#", ""), 16)
            
            embed = discord.Embed(
                title=f"Color: {hex_color.upper()}",
                color=color_int
            )
            embed.add_field(name="Hex", value=hex_color.upper(), inline=True)
            embed.add_field(name="RGB", value=f"({(color_int >> 16) & 255}, {(color_int >> 8) & 255}, {color_int & 255})", inline=True)
            embed.add_field(name="Decimal", value=str(color_int), inline=True)
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("Invalid hex color format! Use format like #ff0000 or ff0000")
    
    @commands.hybrid_command(name="emotes")
    async def emotes(self, ctx):
        guild = ctx.guild
        
        if not guild.emojis:
            await ctx.send("This server has no custom emojis.")
            return
        
        embed = discord.Embed(
            title=f"😀 {guild.name} Emojis ({len(guild.emojis)})",
            color=0x7289da
        )
        
        emoji_list = ""
        for emoji in guild.emojis[:50]:  # Limit to 50 to avoid embed limits
            emoji_list += f"{emoji} `:{emoji.name}:`\n"
        
        if len(guild.emojis) > 50:
            emoji_list += f"\n*... and {len(guild.emojis) - 50} more emojis*"
        
        embed.description = emoji_list
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="members")
    @app_commands.describe(role="The role to list members of")
    async def members_in_role(self, ctx, role: discord.Role):
        members = role.members[:50]  # Limit to 50 members
        
        if not members:
            await ctx.send(f"No members found with the {role.mention} role.")
            return
        
        embed = discord.Embed(
            title=f"👥 Members with {role.name} ({len(role.members)})",
            color=role.color if role.color != discord.Color.default() else 0x7289da
        )
        
        member_list = "\n".join([f"{i+1}. {member.display_name} ({member.mention})" for i, member in enumerate(members)])
        
        if len(role.members) > 50:
            member_list += f"\n\n*... and {len(role.members) - 50} more members*"
        
        embed.description = member_list
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))