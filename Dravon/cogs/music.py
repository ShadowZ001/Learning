import discord
from discord.ext import commands
import wavelink
import asyncio
import os
from utils.embed_utils import add_dravon_footer

class MusicHelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.select(
        placeholder="Select a music category to learn more...",
        options=[
            discord.SelectOption(label="🎵 Basic Playback", description="Play, pause, skip, stop commands", value="playback"),
            discord.SelectOption(label="📜 Queue Management", description="Queue, shuffle, autoplay features", value="queue"),
            discord.SelectOption(label="🔊 Audio Controls", description="Volume and audio settings", value="audio"),
            discord.SelectOption(label="🎛️ Player Controls", description="Interactive button controls", value="controls"),
            discord.SelectOption(label="⚙️ Setup & Config", description="Lavalink setup and configuration", value="setup")
        ]
    )
    async def music_help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        if category == "playback":
            embed = discord.Embed(
                title="🎵 Basic Playback Commands",
                description="Essential commands to play and control music",
                color=0xe91e63
            )
            embed.add_field(
                name="Commands",
                value="`>play <song/url>` - Play music from YouTube, Spotify, SoundCloud\n`>skip` - Skip to the next track in queue\n`>stop` - Stop playback and clear the entire queue\n`>pause` - Pause the current track\n`>resume` - Resume paused playback",
                inline=False
            )
            embed.add_field(
                name="Usage Examples",
                value="• `>play Never Gonna Give You Up`\n• `>play https://youtube.com/watch?v=...`\n• `>play spotify:track:...`",
                inline=False
            )
        
        elif category == "queue":
            embed = discord.Embed(
                title="📜 Queue Management Commands",
                description="Manage your music queue and playlist",
                color=0x9c27b0
            )
            embed.add_field(
                name="Commands",
                value="`>queue` - Display current queue (paginated)\n`>shuffle` - Shuffle the current queue\n`>clear` - Clear the entire queue\n`>remove <position>` - Remove track at position\n`>move <from> <to>` - Move track position",
                inline=False
            )
            embed.add_field(
                name="Autoplay Feature",
                value="🔁 **Autoplay Mode** - Automatically plays related songs when queue is empty\nToggle with the autoplay button in the music player!",
                inline=False
            )
        
        elif category == "audio":
            embed = discord.Embed(
                title="🔊 Audio Controls",
                description="Control volume and audio settings",
                color=0x2196f3
            )
            embed.add_field(
                name="Commands",
                value="`>volume <1-100>` - Set playback volume\n`>bass <-5 to 5>` - Adjust bass levels\n`>treble <-5 to 5>` - Adjust treble levels\n`>reset` - Reset all audio filters",
                inline=False
            )
            embed.add_field(
                name="Volume Tips",
                value="• Default volume: 100%\n• Recommended range: 50-80%\n• Use lower volumes in voice channels",
                inline=False
            )
        
        elif category == "controls":
            embed = discord.Embed(
                title="🎛️ Interactive Player Controls",
                description="Use the music player buttons for easy control",
                color=0x4caf50
            )
            embed.add_field(
                name="Button Controls",
                value="⏭️ **Skip** - Skip to next track\n⏹️ **Stop** - Stop and clear queue\n▶️/⏸️ **Play/Pause** - Toggle playback\n🔁 **Autoplay** - Toggle autoplay mode\n🔀 **Shuffle** - Shuffle current queue",
                inline=False
            )
            embed.add_field(
                name="Player Features",
                value="• **Real-time Updates** - Player embed updates automatically\n• **Persistent Controls** - Buttons work across sessions\n• **Multi-Guild Support** - Independent players per server",
                inline=False
            )
        
        elif category == "setup":
            embed = discord.Embed(
                title="⚙️ Setup & Configuration",
                description="Lavalink setup and troubleshooting",
                color=0xff9800
            )
            embed.add_field(
                name="Requirements",
                value="• **Lavalink Server** - Required for music functionality\n• **Voice Channel** - Bot needs to join voice channels\n• **Permissions** - Connect, Speak, Use Voice Activity",
                inline=False
            )
            embed.add_field(
                name="Configuration (.env)",
                value="```\nLAVALINK_HOST=localhost\nLAVALINK_PORT=2333\nLAVALINK_PASSWORD=youshallnotpass\nLAVALINK_SECURE=false\n```",
                inline=False
            )
            embed.add_field(
                name="Troubleshooting",
                value="• **Connection Failed** - Check if Lavalink is running\n• **No Audio** - Verify bot has voice permissions\n• **Search Failed** - Try different search terms",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        view = MusicHelpView()
        await interaction.response.edit_message(embed=embed, view=view)

class MusicPlayerView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="skip")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.current:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return
        
        await self.player.skip()
        await interaction.response.send_message("⏭️ Skipped to next track!", ephemeral=True)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, custom_id="stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.current:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
            return
        
        await self.player.stop()
        self.player.queue.clear()
        
        # Clean up music message
        music_cog = interaction.client.get_cog('Music')
        if music_cog and interaction.guild.id in music_cog.music_messages:
            try:
                del music_cog.music_messages[interaction.guild.id]
            except:
                pass
        
        await interaction.response.send_message("⏹️ Stopped playback and cleared queue!", ephemeral=True)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.success, custom_id="pause_resume")
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.current:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return
        
        if self.player.paused:
            await self.player.resume()
            button.emoji = "⏸️"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("▶️ Resumed playback!", ephemeral=True)
        else:
            await self.player.pause()
            button.emoji = "▶️"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("⏸️ Paused playback!", ephemeral=True)
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary, custom_id="autoplay")
    async def autoplay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.autoplay = not self.player.autoplay
        status = "enabled" if self.player.autoplay else "disabled"
        await interaction.response.send_message(f"🔁 Autoplay {status}!", ephemeral=True)
    
    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary, custom_id="shuffle")
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.queue:
            await interaction.response.send_message("Queue is empty!", ephemeral=True)
            return
        
        self.player.queue.shuffle()
        await interaction.response.send_message("🔀 Queue shuffled!", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_messages = {}  # Store music player messages per guild
        self.active_nodes = []  # Track active nodes
        self.node_priority = ["primary", "backup1", "backup2"]  # Priority order
    
    async def cog_load(self):
        """Initialize Lavalink connection with intelligent node management"""
        # Start with primary node only
        await self.connect_primary_node()
        
        # Start node monitoring task
        self.bot.loop.create_task(self.monitor_nodes())
    
    async def connect_primary_node(self):
        """Connect to primary node first"""
        primary_node = wavelink.Node(
            uri=f"http://{os.getenv('LAVALINK_HOST', 'localhost')}:{os.getenv('LAVALINK_PORT', '2333')}",
            password=os.getenv('LAVALINK_PASSWORD', 'youshallnotpass'),
            identifier="primary"
        )
        
        try:
            await wavelink.Pool.connect(client=self.bot, nodes=[primary_node])
            self.active_nodes = ["primary"]
            print("✅ Connected to primary Lavalink node")
        except Exception as e:
            print(f"❌ Primary node failed, connecting to backup: {e}")
            await self.connect_backup_node()
    
    async def connect_backup_node(self):
        """Connect to next available backup node"""
        backup_nodes = [
            wavelink.Node(
                uri=f"https://{os.getenv('LAVALINK_HOST2', 'lavalink.oops.wtf')}:{os.getenv('LAVALINK_PORT2', '443')}",
                password=os.getenv('LAVALINK_PASSWORD2', 'www.freelavalink.ga'),
                identifier="backup1"
            ),
            wavelink.Node(
                uri=f"https://{os.getenv('LAVALINK_HOST3', 'lava-v3.ajieblogs.eu.org')}:{os.getenv('LAVALINK_PORT3', '443')}",
                password=os.getenv('LAVALINK_PASSWORD3', 'https://dsc.gg/ajidevserver'),
                identifier="backup2"
            )
        ]
        
        for node in backup_nodes:
            if node.identifier not in self.active_nodes:
                try:
                    await wavelink.Pool.connect(client=self.bot, nodes=[node])
                    self.active_nodes.append(node.identifier)
                    print(f"✅ Connected to backup node: {node.identifier}")
                    return
                except Exception as e:
                    print(f"❌ Failed to connect to {node.identifier}: {e}")
        
        print("❌ No Lavalink nodes available")
    
    async def monitor_nodes(self):
        """Monitor node health and manage connections"""
        while not self.bot.is_closed():
            await asyncio.sleep(30)  # Check every 30 seconds
            
            try:
                # Check if primary is available and we're not using it
                if "primary" not in self.active_nodes:
                    try:
                        primary_node = wavelink.Node(
                            uri=f"http://{os.getenv('LAVALINK_HOST')}:{os.getenv('LAVALINK_PORT')}",
                            password=os.getenv('LAVALINK_PASSWORD'),
                            identifier="primary"
                        )
                        await wavelink.Pool.connect(client=self.bot, nodes=[primary_node])
                        
                        # Disconnect backup nodes when primary is back
                        for node_id in self.active_nodes.copy():
                            if node_id != "primary":
                                try:
                                    node = wavelink.Pool.get_node(node_id)
                                    if node:
                                        await node.disconnect()
                                        self.active_nodes.remove(node_id)
                                        print(f"🔄 Disconnected backup node: {node_id}")
                                except:
                                    pass
                        
                        self.active_nodes = ["primary"]
                        print("🔄 Switched back to primary node")
                    except:
                        pass
                
                # Check if current nodes are still working
                try:
                    current_node = wavelink.Pool.get_node()
                    if not current_node or not hasattr(current_node, 'is_connected') or not current_node.is_connected():
                        print("🔄 Current node disconnected, finding backup...")
                        await self.connect_backup_node()
                except Exception as node_error:
                    print(f"🔄 Node check failed: {node_error}, finding backup...")
                    await self.connect_backup_node()
                    
            except Exception as e:
                print(f"❌ Node monitoring error: {e}")
    
    def get_player(self, guild_id):
        """Get player with error handling for node failures"""
        try:
            player = wavelink.Pool.get_player(guild_id)
            return player
        except Exception:
            return None
    
    @commands.command(name="nodestatus", hidden=True)
    @commands.has_permissions(administrator=True)
    async def node_status(self, ctx):
        """Show node status (Admin only, no sensitive info)"""
        embed = discord.Embed(
            title="🎵 Music Node Status",
            color=0x58a6ff
        )
        
        try:
            current_node = wavelink.Pool.get_node()
            if current_node:
                status = "🟢 Connected" if hasattr(current_node, 'is_connected') and current_node.is_connected() else "🔴 Disconnected"
                embed.add_field(
                    name="Current Node",
                    value=f"**{current_node.identifier}**\nStatus: {status}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Current Node",
                    value="🔴 No active nodes",
                    inline=False
                )
            
            embed.add_field(
                name="Active Nodes",
                value=f"**{len(self.active_nodes)}** node(s) active",
                inline=True
            )
            
            embed.set_footer(text="Node details are protected for security")
            
        except Exception as e:
            embed.add_field(
                name="Error",
                value="Failed to get node status",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    def create_music_embed(self, player):
        """Create the music player embed"""
        embed = discord.Embed(
            title="🎶 Music Player",
            color=0x7289da
        )
        
        if player.current:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{player.current.title}**\nBy: {player.current.author}",
                inline=False
            )
        else:
            embed.add_field(
                name="🎵 Now Playing",
                value="**Nothing playing right now**",
                inline=False
            )
        
        # Status
        if player.current:
            status = "🎵 Playing" if not player.paused else "⏸️ Paused"
        else:
            status = "⏹️ Stopped"
        
        embed.add_field(name="🎛️ Status", value=status, inline=True)
        
        # Queue
        if player.queue:
            queue_list = []
            for i, track in enumerate(list(player.queue)[:5], 1):
                queue_list.append(f"{i}. {track.title}")
            queue_text = "\n".join(queue_list)
            if len(player.queue) > 5:
                queue_text += f"\n... and {len(player.queue) - 5} more"
        else:
            queue_text = "Empty"
        
        embed.add_field(name="📜 Queue", value=queue_text, inline=True)
        
        # Volume
        embed.add_field(name="🔊 Volume", value=f"{player.volume}%", inline=True)
        
        embed.add_field(
            name="✨ Enjoy Free Music Experience",
            value="🎧 Use the buttons below to control playback!",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413172497964339200/e8ce1391-d56f-493b-827c-e4193504d635.jpg?ex=68baf6f2&is=68b9a572&hm=84ef8272435663ce53d9817be2781ed63bdde5bbb09735f08b0f8eff2aee027d&")
        embed = add_dravon_footer(embed)
        return embed
    
    async def update_music_embed(self, guild_id):
        """Update the music player embed"""
        if guild_id not in self.music_messages:
            return
        
        player = self.get_player(guild_id)
        if not player:
            return
        
        embed = self.create_music_embed(player)
        view = MusicPlayerView(player)
        
        try:
            message = self.music_messages[guild_id]
            await message.edit(embed=embed, view=view)
        except:
            pass
    
    @commands.hybrid_command(name="play")
    async def play(self, ctx, *, query: str):
        """Play a song from YouTube, Spotify, or SoundCloud"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ Error",
                description="You need to be in a voice channel to use music commands!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Check if user is trying to play Spotify without premium
        premium_cog = self.bot.get_cog('Premium')
        if premium_cog:
            is_premium = await premium_cog.is_premium(ctx.author.id)
            
            # Check if it's a Spotify URL/query and user isn't premium
            if ("spotify" in query.lower() or "open.spotify.com" in query) and not is_premium:
                embed = discord.Embed(
                    title="🔒 Premium Feature",
                    description="Spotify music streaming is a premium-only feature!\n\nUpgrade to premium to enjoy:\n🎶 High-quality Spotify streaming\n🎵 Unlimited Spotify playlists\n✨ And much more!",
                    color=0xffd700
                )
                embed = add_dravon_footer(embed)
                await ctx.send(embed=embed)
                return
        
        player = self.get_player(ctx.guild.id)
        
        # If bot is in different channel, disconnect first
        if player and player.channel and player.channel != ctx.author.voice.channel:
            await player.disconnect()
            player = None
        
        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Connection Error",
                    description=f"Failed to connect to voice channel: {str(e)}",
                    color=0xff0000
                )
                embed = add_dravon_footer(embed)
                await ctx.send(embed=embed)
                return
        
        # Search for tracks based on premium mode
        try:
            if premium_cog and await premium_cog.is_premium(ctx.author.id):
                music_mode = await premium_cog.get_music_mode(ctx.author.id)
                if music_mode == "spotify" and ("spotify" in query.lower() or "open.spotify.com" in query):
                    # Premium Spotify mode
                    tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource.Spotify)
                else:
                    # Premium Lavalink mode or regular search
                    tracks = await wavelink.Playable.search(query)
            else:
                # Non-premium users only get basic Lavalink
                tracks = await wavelink.Playable.search(query)
            
            if not tracks:
                embed = discord.Embed(
                    title="❌ No Results",
                    description=f"No tracks found for: `{query}`",
                    color=0xff0000
                )
                embed = add_dravon_footer(embed)
                await ctx.send(embed=embed)
                return
        except Exception as e:
            embed = discord.Embed(
                title="❌ Search Error",
                description="Failed to search for tracks. Trying backup nodes...",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        track = tracks[0]
        
        if player.current:
            player.queue.put(track)
            embed = discord.Embed(
                title="📜 Added to Queue",
                description=f"**{track.title}**\nBy: {track.author}\nPosition: {len(player.queue)}",
                color=0x00ff00
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        else:
            await player.play(track)
            embed = self.create_music_embed(player)
            view = MusicPlayerView(player)
            message = await ctx.send(embed=embed, view=view)
            self.music_messages[ctx.guild.id] = message
    
    @commands.hybrid_command(name="skip")
    async def skip(self, ctx):
        """Skip the current song"""
        player = self.get_player(ctx.guild.id)
        
        if not player or not player.current:
            embed = discord.Embed(
                title="❌ Error",
                description="Nothing is playing!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        await player.skip()
        embed = discord.Embed(
            title="⏭️ Skipped",
            description="Skipped to the next track!",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="stop")
    async def stop(self, ctx):
        """Stop the music and clear the queue"""
        player = self.get_player(ctx.guild.id)
        
        if not player or not player.current:
            embed = discord.Embed(
                title="❌ Error",
                description="Nothing is currently playing!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        await player.stop()
        player.queue.clear()
        
        # Clean up music message
        if ctx.guild.id in self.music_messages:
            try:
                await self.music_messages[ctx.guild.id].delete()
                del self.music_messages[ctx.guild.id]
            except:
                pass
        
        embed = discord.Embed(
            title="⏹️ Stopped",
            description="Stopped playback and cleared the queue!",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="queue")
    async def queue(self, ctx):
        """Display the current queue"""
        player = self.get_player(ctx.guild.id)
        
        if not player or not player.queue:
            embed = discord.Embed(
                title="📜 Queue",
                description="The queue is empty!",
                color=0x7289da
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        queue_list = []
        for i, track in enumerate(list(player.queue)[:10], 1):
            queue_list.append(f"{i}. **{track.title}** - {track.author}")
        
        embed = discord.Embed(
            title="📜 Current Queue",
            description="\n".join(queue_list),
            color=0x7289da
        )
        
        if len(player.queue) > 10:
            embed.add_field(
                name="And more...",
                value=f"{len(player.queue) - 10} more tracks in queue",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="volume")
    async def volume(self, ctx, volume: int):
        """Adjust the music volume (1-100)"""
        if not 1 <= volume <= 100:
            embed = discord.Embed(
                title="❌ Invalid Volume",
                description="Volume must be between 1 and 100!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player:
            embed = discord.Embed(
                title="❌ Error",
                description="No music player found!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        await player.set_volume(volume)
        
        embed = discord.Embed(
            title="🔊 Volume Changed",
            description=f"Volume set to {volume}%",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload):
        """Handle track end events"""
        await self.update_music_embed(payload.player.guild.id)
    
    @commands.hybrid_command(name="node")
    async def node_command(self, ctx, action: str = None, node_name: str = None):
        """Node management for premium users and bot admins"""
        premium_cog = self.bot.get_cog('Premium')
        is_premium = premium_cog and await premium_cog.is_premium(ctx.author.id)
        is_bot_admin = ctx.author.id == 1037768611126841405
        
        if not is_premium and not is_bot_admin:
            embed = discord.Embed(
                title="🔒 Premium Feature",
                description="Node switching is only available for premium users and bot admins!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        if action is None or action.lower() == "list":
            embed = discord.Embed(
                title="🎵 Available Music Nodes",
                description="**Available Lavalink Nodes:**\n\n🟢 **primary** - Main Lavalink server\n🟡 **backup1** - Backup server 1\n🟠 **backup2** - Backup server 2\n\n**Premium Spotify:**\n🎶 **spotify** - High-quality Spotify streaming\n\n**Usage:** `>node switch <node_name>`",
                color=0x7289da
            )
            
            current_node = wavelink.Pool.get_node()
            if current_node:
                embed.add_field(
                    name="Current Active Node",
                    value=f"**{current_node.identifier}**",
                    inline=False
                )
            
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        
        elif action.lower() == "switch" and node_name:
            if node_name.lower() == "spotify":
                if not is_premium:
                    embed = discord.Embed(
                        title="🔒 Premium Required",
                        description="Spotify node is only available for premium users!",
                        color=0xff0000
                    )
                    embed = add_dravon_footer(embed)
                    await ctx.send(embed=embed)
                    return
                
                # Set user's music mode to Spotify
                await self.bot.db.set_premium_music_mode(ctx.author.id, "spotify")
                embed = discord.Embed(
                    title="✅ Switched to Spotify",
                    description="Your music mode has been set to **Spotify**!\nYou can now play high-quality Spotify tracks.",
                    color=0x00ff00
                )
            else:
                # Switch to Lavalink node
                valid_nodes = ["primary", "backup1", "backup2"]
                if node_name.lower() not in valid_nodes:
                    embed = discord.Embed(
                        title="❌ Invalid Node",
                        description=f"Available nodes: {', '.join(valid_nodes)}, spotify",
                        color=0xff0000
                    )
                    embed = add_dravon_footer(embed)
                    await ctx.send(embed=embed)
                    return
                
                # Set user's music mode to Lavalink
                await self.bot.db.set_premium_music_mode(ctx.author.id, "lavalink")
                embed = discord.Embed(
                    title="✅ Switched to Lavalink",
                    description=f"Your music mode has been set to **Lavalink** ({node_name.lower()})!\nYou can now play from YouTube and other sources.",
                    color=0x00ff00
                )
            
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🎵 Node Commands",
                description="**Available Commands:**\n\n`>node list` - View available nodes\n`>node switch <node_name>` - Switch to a specific node\n\n**Available Nodes:**\n• primary, backup1, backup2 (Lavalink)\n• spotify (Premium only)",
                color=0x7289da
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
    
    @commands.command(name="mhelp")
    async def music_help(self, ctx):
        """Display comprehensive music help with categories"""
        
        embed = discord.Embed(
            title="🎵 Dravon Music Player Help",
            description="**Complete music system with multi-platform support**\n\nSupports YouTube, Spotify, and SoundCloud with autoplay and interactive controls!\n\n*Select a category from the dropdown below for detailed information!*",
            color=0xe91e63
        )
        
        embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413172308410892372/ba87b97c-3bb6-46c6-855d-f8b3076779d2.jpg?ex=68baf6c5&is=68b9a545&hm=8d31576fa4bfb3804a0d7ea5f1f4f98e6ddcb32430cf9a5f487a1e0b0ce62b11&")
        embed = add_dravon_footer(embed)
        
        view = MusicHelpView()
        await ctx.send(embed=embed, view=view)
    
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload):
        """Handle track start events"""
        await self.update_music_embed(payload.player.guild.id)

async def setup(bot):
    await bot.add_cog(Music(bot))