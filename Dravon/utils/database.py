import aiosqlite
import json
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = "dravon.db"
        self.init_db()
    
    def init_db(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create all necessary tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prefixes (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT DEFAULT '>'
            )
        ''')
        

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id INTEGER PRIMARY KEY,
                expiry TEXT,
                music_mode TEXT DEFAULT 'lavalink'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS premium_guilds (
                guild_id INTEGER PRIMARY KEY,
                activator_id INTEGER,
                activated_at REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS antinuke_rules (
                guild_id INTEGER,
                rule_type TEXT,
                config TEXT,
                PRIMARY KEY (guild_id, rule_type)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automod_rules (
                guild_id INTEGER,
                rule_type TEXT,
                config TEXT,
                PRIMARY KEY (guild_id, rule_type)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autorule_rules (
                guild_id INTEGER,
                rule_type TEXT,
                config TEXT,
                PRIMARY KEY (guild_id, rule_type)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_admins (
                user_id INTEGER PRIMARY KEY
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                settings TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeds (
                guild_id INTEGER,
                embed_name TEXT,
                config TEXT,
                PRIMARY KEY (guild_id, embed_name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extra_owners (
                guild_id INTEGER,
                user_id INTEGER,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verify_config (
                guild_id INTEGER PRIMARY KEY,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reaction_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                bio TEXT,
                commands_used INTEGER DEFAULT 0
            )
        ''')
        

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_data (
                guild_id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_xp (
                guild_id INTEGER,
                user_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS levelup_config (
                guild_id INTEGER PRIMARY KEY,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS canva_config (
                guild_id INTEGER PRIMARY KEY,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warn_config (
                guild_id INTEGER PRIMARY KEY,
                punishment TEXT DEFAULT 'kick',
                warn_limit INTEGER DEFAULT 3
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warn_log_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_messages (
                guild_id INTEGER,
                user_id INTEGER,
                message_count INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_messages (
                guild_id INTEGER,
                user_id INTEGER,
                date TEXT,
                message_count INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apply_config (
                guild_id INTEGER PRIMARY KEY,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                user_id INTEGER,
                badge TEXT,
                PRIMARY KEY (user_id, badge)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_config (
                guild_id INTEGER PRIMARY KEY,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS afk_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                timestamp TEXT,
                dm_enabled BOOLEAN DEFAULT 0
            )
        ''')
        
        # Add dm_enabled column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE afk_users ADD COLUMN dm_enabled BOOLEAN DEFAULT 0')
        except:
            pass  # Column already exists
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invite_logs (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_invites (
                guild_id INTEGER,
                user_id INTEGER,
                total INTEGER DEFAULT 0,
                joins INTEGER DEFAULT 0,
                leaves INTEGER DEFAULT 0,
                bonus INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def get_prefix(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else ">"
    
    async def set_prefix(self, guild_id, prefix):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO prefixes (guild_id, prefix) VALUES (?, ?)", (guild_id, prefix))
            await db.commit()
    
    async def get_bot_admins(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM bot_admins")
            results = await cursor.fetchall()
            return [row[0] for row in results]
    
    async def add_bot_admin(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO bot_admins (user_id) VALUES (?)", (user_id,))
            await db.commit()
    
    async def remove_bot_admin(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM bot_admins WHERE user_id = ?", (user_id,))
            await db.commit()
    
    async def set_afk_user(self, user_id, reason, global_afk=False, guild_id=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO afk_users (user_id, reason, timestamp, global_afk, guild_id) VALUES (?, ?, ?, ?, ?)", 
                           (user_id, reason, datetime.now().timestamp(), global_afk, guild_id))
            await db.commit()
    
    async def get_afk_user(self, user_id, guild_id=None):
        async with aiosqlite.connect(self.db_path) as db:
            # Check for global AFK first
            cursor = await db.execute("SELECT reason, timestamp, global_afk FROM afk_users WHERE user_id = ? AND global_afk = 1", (user_id,))
            result = await cursor.fetchone()
            if result:
                return {"reason": result[0], "timestamp": result[1], "global_afk": True}
            
            # Check for local AFK in specific guild
            if guild_id:
                cursor = await db.execute("SELECT reason, timestamp, global_afk FROM afk_users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
                result = await cursor.fetchone()
                if result:
                    return {"reason": result[0], "timestamp": result[1], "global_afk": False}
            
            return None
    
    async def remove_afk_user(self, user_id, guild_id=None):
        async with aiosqlite.connect(self.db_path) as db:
            if guild_id is None:
                # Remove global AFK
                await db.execute("DELETE FROM afk_users WHERE user_id = ? AND global_afk = 1", (user_id,))
            else:
                # Remove local AFK for specific guild
                await db.execute("DELETE FROM afk_users WHERE user_id = ? AND guild_id = ? AND global_afk = 0", (user_id, guild_id))
            await db.commit()
    
    async def get_premium_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT expiry, music_mode FROM premium_users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            if result:
                return {"expiry": result[0], "music_mode": result[1]}
            return None
    
    async def set_premium_user(self, user_id, expiry_date):
        expiry_str = expiry_date.isoformat() if expiry_date else None
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO premium_users (user_id, expiry) VALUES (?, ?)", (user_id, expiry_str))
            await db.commit()
    
    async def remove_premium_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM premium_users WHERE user_id = ?", (user_id,))
            await db.commit()
    
    async def get_premium_guild(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT activator_id, activated_at FROM premium_guilds WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return {"activator_id": result[0], "activated_at": result[1]}
            return None
    
    async def set_premium_guild(self, guild_id, activator_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO premium_guilds (guild_id, activator_id, activated_at) VALUES (?, ?, ?)", 
                           (guild_id, activator_id, datetime.now().timestamp()))
            await db.commit()
    
    async def get_user_premium_guilds(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT guild_id FROM premium_guilds WHERE activator_id = ?", (user_id,))
            results = await cursor.fetchall()
            return [row[0] for row in results]
    
    async def get_premium_music_mode(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT music_mode FROM premium_users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else "lavalink"
    
    async def set_premium_music_mode(self, user_id, mode):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO premium_users (user_id, music_mode) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET music_mode = ?", 
                           (user_id, mode, mode))
            await db.commit()
    
    async def get_antinuke_rule(self, guild_id, rule_type):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM antinuke_rules WHERE guild_id = ? AND rule_type = ?", (guild_id, rule_type))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    async def set_antinuke_rule(self, guild_id, rule_type, config):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO antinuke_rules (guild_id, rule_type, config) VALUES (?, ?, ?)", 
                           (guild_id, rule_type, json.dumps(config)))
            await db.commit()
    
    async def get_all_automod_rules(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT rule_type, config FROM automod_rules WHERE guild_id = ?", (guild_id,))
            results = await cursor.fetchall()
            rules = {}
            for rule_type, config in results:
                rules[rule_type] = json.loads(config)
            return rules
    
    async def set_automod_rule(self, guild_id, rule_type, config):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO automod_rules (guild_id, rule_type, config) VALUES (?, ?, ?)", 
                           (guild_id, rule_type, json.dumps(config)))
            await db.commit()
    
    async def set_automod_logs_channel(self, guild_id, channel_id):
        await self.set_automod_rule(guild_id, "logs_channel", {"channel_id": channel_id})
    
    async def get_247_mode(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                settings = json.loads(result[0])
                return settings.get("247_mode", False)
            return False
    
    async def set_247_mode(self, guild_id, enabled):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            
            if result:
                settings = json.loads(result[0])
            else:
                settings = {}
            
            settings["247_mode"] = enabled
            
            await db.execute("INSERT OR REPLACE INTO guild_settings (guild_id, settings) VALUES (?, ?)", 
                           (guild_id, json.dumps(settings)))
            await db.commit()
    
    async def has_antinuke_access(self, guild_id, user_id):
        # Check if user is whitelisted for antinuke
        whitelist = await self.get_antinuke_rule(guild_id, "whitelist")
        if whitelist and user_id in whitelist.get("users", []):
            return True
        return False
    
    # Welcome system methods
    async def get_welcome_config(self, guild_id):
        return {}
    
    async def set_welcome_config(self, guild_id, config):
        pass
    
    # Ticket system methods
    async def get_ticket_config(self, guild_id):
        return {}
    
    async def set_ticket_setting(self, guild_id, setting, value):
        pass
    
    async def add_ticket_category(self, guild_id, category):
        pass
    
    async def set_ticket_category_channel(self, guild_id, category, channel_id):
        pass
    
    async def set_ticket_logs_channel(self, guild_id, channel_id):
        pass
    
    async def reset_ticket_config(self, guild_id):
        pass
    
    # Giveaway system methods
    async def create_giveaway(self, giveaway_data):
        pass
    
    async def get_giveaway(self, giveaway_id):
        return None
    
    async def get_giveaway_by_message(self, message_id):
        return None
    
    async def add_giveaway_participant(self, giveaway_id, user_id):
        pass
    
    async def remove_giveaway_participant(self, giveaway_id, user_id):
        pass
    
    async def end_giveaway(self, giveaway_id):
        pass
    
    async def get_guild_giveaways(self, guild_id):
        return []
    
    async def delete_giveaway(self, giveaway_id):
        pass
    
    async def pause_giveaway(self, giveaway_id, paused):
        pass
    
    # Embed system methods
    async def set_embed_setting(self, guild_id, embed_name, setting, value):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM embeds WHERE guild_id = ? AND embed_name = ?", (guild_id, embed_name))
            result = await cursor.fetchone()
            
            if result:
                config = json.loads(result[0])
            else:
                config = {}
            
            config[setting] = value
            
            await db.execute("INSERT OR REPLACE INTO embeds (guild_id, embed_name, config) VALUES (?, ?, ?)", 
                           (guild_id, embed_name, json.dumps(config)))
            await db.commit()
    
    async def get_embed_config(self, guild_id, embed_name):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM embeds WHERE guild_id = ? AND embed_name = ?", (guild_id, embed_name))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return {}
    
    async def get_all_embeds(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT embed_name, config FROM embeds WHERE guild_id = ?", (guild_id,))
            results = await cursor.fetchall()
            embeds = {}
            for embed_name, config in results:
                embeds[embed_name] = json.loads(config)
            return embeds
    
    async def delete_embed(self, guild_id, embed_name):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM embeds WHERE guild_id = ? AND embed_name = ?", (guild_id, embed_name))
            await db.commit()
            return cursor.rowcount > 0
    
    # AutoRole system methods
    async def get_autorole_config(self, guild_id):
        return {}
    
    async def set_autorole_config(self, guild_id, config):
        pass
    
    # AutoRule system methods
    async def set_autorule_rule(self, guild_id, rule_type, config):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO autorule_rules (guild_id, rule_type, config) VALUES (?, ?, ?)", 
                           (guild_id, rule_type, json.dumps(config)))
            await db.commit()
    
    async def get_autorule_rule(self, guild_id, rule_type):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM autorule_rules WHERE guild_id = ? AND rule_type = ?", (guild_id, rule_type))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    async def get_all_autorule_configs(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT rule_type, config FROM autorule_rules WHERE guild_id = ?", (guild_id,))
            results = await cursor.fetchall()
            rules = {}
            for rule_type, config in results:
                rules[rule_type] = json.loads(config)
            return rules
    
    async def set_autorule_logs_channel(self, guild_id, channel_id):
        await self.set_autorule_rule(guild_id, "logs_channel", {"channel_id": channel_id})
    
    # Boost system methods
    async def set_boost_setting(self, guild_id, setting, value):
        pass
    
    async def get_boost_config(self, guild_id):
        return {}
    
    async def reset_boost_config(self, guild_id):
        pass
    
    # Application system methods
    async def set_apply_config(self, guild_id, setting, value):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM apply_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            
            if result:
                config = json.loads(result[0])
            else:
                config = {}
            
            if setting == "_full_config":
                config = json.loads(value)
            else:
                config[setting] = value
            
            await db.execute("INSERT OR REPLACE INTO apply_config (guild_id, config) VALUES (?, ?)", 
                           (guild_id, json.dumps(config)))
            await db.commit()
    
    async def get_apply_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM apply_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return {}
    
    # Leave system methods
    async def set_leave_setting(self, guild_id, setting, value):
        pass
    
    async def get_leave_config(self, guild_id):
        return {}
    
    async def reset_leave_config(self, guild_id):
        pass
    
    # Logs system methods
    async def set_welcome_logs_channel(self, guild_id, channel_id):
        pass
    
    async def set_antinuke_logs_channel(self, guild_id, channel_id):
        pass
    
    # Invite system methods
    async def set_invite_logs_channel(self, guild_id, channel_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO invite_logs (guild_id, channel_id) VALUES (?, ?)", 
                           (guild_id, channel_id))
            await db.commit()
    
    async def get_invite_logs_channel(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT channel_id FROM invite_logs WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async def get_user_invites(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT total, joins, leaves, bonus FROM user_invites WHERE guild_id = ? AND user_id = ?", 
                                    (guild_id, user_id))
            result = await cursor.fetchone()
            if result:
                return {"total": result[0], "joins": result[1], "leaves": result[2], "bonus": result[3]}
            return {"total": 0, "joins": 0, "leaves": 0, "bonus": 0}
    
    async def get_guild_invites(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id, total, joins, leaves, bonus FROM user_invites WHERE guild_id = ?", 
                                    (guild_id,))
            results = await cursor.fetchall()
            invites = {}
            for row in results:
                invites[str(row[0])] = {"total": row[1], "joins": row[2], "leaves": row[3], "bonus": row[4]}
            return invites
    
    async def add_user_invites(self, guild_id, user_id, amount):
        async with aiosqlite.connect(self.db_path) as db:
            # Insert or update user invite record
            await db.execute(
                "INSERT OR IGNORE INTO user_invites (guild_id, user_id, total, joins, leaves, bonus) VALUES (?, ?, 0, 0, 0, 0)",
                (guild_id, user_id)
            )
            
            # Update joins and recalculate total
            await db.execute(
                "UPDATE user_invites SET joins = joins + ?, total = joins - leaves + bonus + ? WHERE guild_id = ? AND user_id = ?",
                (amount, amount, guild_id, user_id)
            )
            await db.commit()
    
    async def add_user_bonus_invites(self, guild_id, user_id, amount):
        async with aiosqlite.connect(self.db_path) as db:
            # Insert or update user invite record
            await db.execute(
                "INSERT OR IGNORE INTO user_invites (guild_id, user_id, total, joins, leaves, bonus) VALUES (?, ?, 0, 0, 0, 0)",
                (guild_id, user_id)
            )
            
            # Update bonus and recalculate total
            await db.execute(
                "UPDATE user_invites SET bonus = bonus + ?, total = joins - leaves + bonus + ? WHERE guild_id = ? AND user_id = ?",
                (amount, amount, guild_id, user_id)
            )
            await db.commit()
    
    async def remove_user_invites(self, guild_id, user_id, amount):
        async with aiosqlite.connect(self.db_path) as db:
            # Insert or update user invite record
            await db.execute(
                "INSERT OR IGNORE INTO user_invites (guild_id, user_id, total, joins, leaves, bonus) VALUES (?, ?, 0, 0, 0, 0)",
                (guild_id, user_id)
            )
            
            # Update bonus (don't go below 0) and recalculate total
            await db.execute(
                "UPDATE user_invites SET bonus = MAX(0, bonus - ?), total = joins - leaves + MAX(0, bonus - ?) WHERE guild_id = ? AND user_id = ?",
                (amount, amount, guild_id, user_id)
            )
            await db.commit()
    
    async def clear_user_invites(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM user_invites WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            await db.commit()
    
    async def clear_guild_invites(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM user_invites WHERE guild_id = ?", (guild_id,))
            await db.commit()
    
    # Extra owner system methods
    async def add_extra_owner(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO extra_owners (guild_id, user_id) VALUES (?, ?)", (guild_id, user_id))
            await db.commit()
    
    async def remove_extra_owner(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM extra_owners WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            await db.commit()
    
    async def get_extra_owners(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM extra_owners WHERE guild_id = ?", (guild_id,))
            results = await cursor.fetchall()
            return [row[0] for row in results]
    
    # Verification system methods
    async def set_verify_config(self, guild_id, config):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO verify_config (guild_id, config) VALUES (?, ?)", 
                           (guild_id, json.dumps(config)))
            await db.commit()
    
    async def get_verify_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM verify_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    async def reset_verify_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM verify_config WHERE guild_id = ?", (guild_id,))
            await db.commit()
    
    # Reaction role system methods
    async def add_reaction_role(self, guild_id, config):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO reaction_roles (guild_id, config) VALUES (?, ?)", 
                           (guild_id, json.dumps(config)))
            await db.commit()
    
    async def get_reaction_roles(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM reaction_roles WHERE guild_id = ?", (guild_id,))
            results = await cursor.fetchall()
            return [json.loads(row[0]) for row in results]
    
    async def reset_reaction_roles(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM reaction_roles WHERE guild_id = ?", (guild_id,))
            await db.commit()
    
    # User profile system methods
    async def get_user_bio(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT bio FROM user_profiles WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async def set_user_bio(self, user_id, bio):
        async with aiosqlite.connect(self.db_path) as db:
            # Check if user exists
            cursor = await db.execute("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))
            exists = await cursor.fetchone()
            
            if exists:
                await db.execute("UPDATE user_profiles SET bio = ? WHERE user_id = ?", (bio, user_id))
            else:
                await db.execute("INSERT INTO user_profiles (user_id, bio, commands_used) VALUES (?, ?, 0)", (user_id, bio))
            await db.commit()
    
    async def get_user_commands_used(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT commands_used FROM user_profiles WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def increment_user_commands(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            # Check if user exists
            cursor = await db.execute("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))
            exists = await cursor.fetchone()
            
            if exists:
                await db.execute("UPDATE user_profiles SET commands_used = commands_used + 1 WHERE user_id = ?", (user_id,))
            else:
                await db.execute("INSERT INTO user_profiles (user_id, bio, commands_used) VALUES (?, NULL, 1)", (user_id,))
            await db.commit()
    
    # Warning system methods
    async def add_warning(self, guild_id, user_id, moderator_id, reason):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO warnings (guild_id, user_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)", 
                           (guild_id, user_id, moderator_id, reason, datetime.now().timestamp()))
            await db.commit()
    
    async def get_user_warnings(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT reason, moderator_id, timestamp FROM warnings WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            results = await cursor.fetchall()
            return [{'reason': row[0], 'moderator_id': row[1], 'timestamp': row[2]} for row in results]
    
    async def set_warn_config(self, guild_id, punishment, limit):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO warn_config (guild_id, punishment, warn_limit) VALUES (?, ?, ?)", 
                           (guild_id, punishment, limit))
            await db.commit()
    
    async def get_warn_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT punishment, warn_limit FROM warn_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return {'punishment': result[0], 'limit': result[1]}
            return None
    
    async def clear_user_warnings(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            await db.commit()
    
    async def get_all_warned_users(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id, COUNT(*) as warning_count FROM warnings WHERE guild_id = ? GROUP BY user_id ORDER BY warning_count DESC", (guild_id,))
            results = await cursor.fetchall()
            return [{'user_id': row[0], 'warning_count': row[1]} for row in results]
    
    async def get_user_warnings_count(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    # AFK system methods
    async def set_afk(self, user_id, reason, guild_id=None, global_afk=False):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO afk_users (user_id, reason, global_afk, guild_id) VALUES (?, ?, ?, ?)", 
                           (user_id, reason, global_afk, guild_id))
            await db.commit()
    
    async def get_afk(self, user_id, guild_id=None):
        async with aiosqlite.connect(self.db_path) as db:
            # Check global AFK first
            cursor = await db.execute("SELECT reason, global_afk, guild_id FROM afk_users WHERE user_id = ? AND global_afk = 1", (user_id,))
            result = await cursor.fetchone()
            if result:
                return {'reason': result[0], 'global_afk': True, 'guild_id': result[2]}
            
            # Check local AFK
            if guild_id:
                cursor = await db.execute("SELECT reason, global_afk, guild_id FROM afk_users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
                result = await cursor.fetchone()
                if result:
                    return {'reason': result[0], 'global_afk': False, 'guild_id': result[2]}
            
            return None
    
    async def remove_afk(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM afk_users WHERE user_id = ?", (user_id,))
            await db.commit()
    
    async def get_all_afk_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id, reason, global_afk, guild_id FROM afk_users")
            results = await cursor.fetchall()
            return [{
                'user_id': row[0],
                'reason': row[1], 
                'global_afk': bool(row[2]),
                'guild_id': row[3]
            } for row in results]
    
    # Maintenance system methods
    async def set_maintenance_data(self, guild_id, data):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO maintenance_data (guild_id, data) VALUES (?, ?)", 
                           (guild_id, json.dumps(data)))
            await db.commit()
    
    async def get_maintenance_data(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT data FROM maintenance_data WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    async def clear_maintenance_data(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM maintenance_data WHERE guild_id = ?", (guild_id,))
            await db.commit()
    
    # AI Chat system methods
    async def set_ai_channel(self, guild_id, channel_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO ai_channels (guild_id, channel_id) VALUES (?, ?)", 
                           (guild_id, channel_id))
            await db.commit()
    
    async def get_ai_channel(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT channel_id FROM ai_channels WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async def clear_ai_channel(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM ai_channels WHERE guild_id = ?", (guild_id,))
            await db.commit()
    
    # Level system methods
    async def get_user_xp(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT xp, level FROM user_xp WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            result = await cursor.fetchone()
            if result:
                return {"xp": result[0], "level": result[1]}
            return None
    
    async def set_user_xp(self, guild_id, user_id, xp, level):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO user_xp (guild_id, user_id, xp, level) VALUES (?, ?, ?, ?)", 
                           (guild_id, user_id, xp, level))
            await db.commit()
    
    async def get_leaderboard(self, guild_id, page=0):
        async with aiosqlite.connect(self.db_path) as db:
            offset = page * 10
            cursor = await db.execute("SELECT user_id, xp, level FROM user_xp WHERE guild_id = ? ORDER BY xp DESC LIMIT 10 OFFSET ?", 
                                    (guild_id, offset))
            results = await cursor.fetchall()
            return [{"user_id": row[0], "xp": row[1], "level": row[2]} for row in results]
    
    async def get_levelup_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM levelup_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    async def set_levelup_setting(self, guild_id, setting, value):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM levelup_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            
            if result:
                config = json.loads(result[0])
            else:
                config = {}
            
            config[setting] = value
            
            await db.execute("INSERT OR REPLACE INTO levelup_config (guild_id, config) VALUES (?, ?)", 
                           (guild_id, json.dumps(config)))
            await db.commit()
    
    async def reset_levelup_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM levelup_config WHERE guild_id = ?", (guild_id,))
            await db.commit()
    
    async def get_canva_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM canva_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return {"enabled": False}
    
    async def set_canva_setting(self, guild_id, setting, value):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM canva_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            
            if result:
                config = json.loads(result[0])
            else:
                config = {}
            
            config[setting] = value
            
            await db.execute("INSERT OR REPLACE INTO canva_config (guild_id, config) VALUES (?, ?)", 
                           (guild_id, json.dumps(config)))
            await db.commit()
    
    async def is_premium_server(self, guild_id):
        # Check if server has premium
        premium_guild = await self.get_premium_guild(guild_id)
        return premium_guild is not None
    
    async def set_warn_log_channel(self, guild_id, channel_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO warn_log_channels (guild_id, channel_id) VALUES (?, ?)", 
                           (guild_id, channel_id))
            await db.commit()
    
    async def get_warn_log_channel(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT channel_id FROM warn_log_channels WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None
    
    # Message tracking methods
    async def increment_user_messages(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Update all-time messages
            await db.execute(
                "INSERT OR IGNORE INTO user_messages (guild_id, user_id, message_count) VALUES (?, ?, 0)",
                (guild_id, user_id)
            )
            await db.execute(
                "UPDATE user_messages SET message_count = message_count + 1 WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            
            # Update daily messages
            await db.execute(
                "INSERT OR IGNORE INTO daily_messages (guild_id, user_id, date, message_count) VALUES (?, ?, ?, 0)",
                (guild_id, user_id, today)
            )
            await db.execute(
                "UPDATE daily_messages SET message_count = message_count + 1 WHERE guild_id = ? AND user_id = ? AND date = ?",
                (guild_id, user_id, today)
            )
            
            await db.commit()
    
    async def get_user_messages(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT message_count FROM user_messages WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_user_messages_today(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            today = datetime.now().strftime('%Y-%m-%d')
            cursor = await db.execute(
                "SELECT message_count FROM daily_messages WHERE guild_id = ? AND user_id = ? AND date = ?",
                (guild_id, user_id, today)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_message_leaderboard(self, guild_id, page=0):
        async with aiosqlite.connect(self.db_path) as db:
            offset = page * 10
            cursor = await db.execute(
                "SELECT user_id, message_count FROM user_messages WHERE guild_id = ? ORDER BY message_count DESC LIMIT 10 OFFSET ?",
                (guild_id, offset)
            )
            results = await cursor.fetchall()
            return [{'user_id': row[0], 'message_count': row[1]} for row in results]
    
    async def get_total_message_users(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM user_messages WHERE guild_id = ?",
                (guild_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    # Badge system methods
    async def add_user_badge(self, user_id, badge):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO user_badges (user_id, badge) VALUES (?, ?)",
                (user_id, badge)
            )
            await db.commit()
    
    async def remove_user_badge(self, user_id, badge):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM user_badges WHERE user_id = ? AND badge = ?",
                (user_id, badge)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def get_user_badges(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT badge FROM user_badges WHERE user_id = ?",
                (user_id,)
            )
            results = await cursor.fetchall()
            return [row[0] for row in results]
    
    # YouTube notification methods
    async def set_youtube_config(self, guild_id, setting, value):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM youtube_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            
            if result:
                config = json.loads(result[0])
            else:
                config = {}
            
            config[setting] = value
            
            await db.execute("INSERT OR REPLACE INTO youtube_config (guild_id, config) VALUES (?, ?)", 
                           (guild_id, json.dumps(config)))
            await db.commit()
    
    async def get_youtube_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT config FROM youtube_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            return {}
    
    async def get_all_youtube_configs(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT guild_id, config FROM youtube_config")
            results = await cursor.fetchall()
            configs = {}
            for guild_id, config in results:
                configs[guild_id] = json.loads(config)
            return configs
    
    async def reset_youtube_config(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM youtube_config WHERE guild_id = ?", (guild_id,))
            await db.commit()
    
    # AFK system methods
    async def set_afk(self, user_id, reason, timestamp, dm_enabled):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO afk_users (user_id, reason, timestamp, dm_enabled) VALUES (?, ?, ?, ?)",
                (user_id, reason, timestamp.isoformat(), dm_enabled)
            )
            await db.commit()
    
    async def get_afk(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT reason, timestamp, dm_enabled FROM afk_users WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            if result:
                return {
                    'reason': result[0],
                    'timestamp': result[1],
                    'dm_enabled': bool(result[2])
                }
            return None
    
    async def remove_afk(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM afk_users WHERE user_id = ?", (user_id,))
            await db.commit()