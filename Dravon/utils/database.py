from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any, List
from datetime import datetime

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb+srv://ayanshpatel9991_db_user:Ayanshpatel12309@cluster0.51k9d3b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.db = self.client.bot_database
    
    async def get_prefix(self, guild_id: int) -> Optional[str]:
        result = await self.db.prefixes.find_one({"guild_id": guild_id})
        return result["prefix"] if result else None
    
    async def set_prefix(self, guild_id: int, prefix: str):
        await self.db.prefixes.update_one(
            {"guild_id": guild_id},
            {"$set": {"prefix": prefix}},
            upsert=True
        )
    
    async def get_welcome_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        result = await self.db.welcome_configs.find_one({"guild_id": guild_id})
        return result["config"] if result else None
    
    async def set_welcome_config(self, guild_id: int, config: Dict[str, Any]):
        await self.db.welcome_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {"config": config}},
            upsert=True
        )
    
    async def get_autoresponders(self, guild_id: int) -> Dict[str, Any]:
        result = await self.db.autoresponders.find_one({"guild_id": guild_id})
        return result["responders"] if result else {}
    
    async def set_autoresponder(self, guild_id: int, trigger: str, config: Dict[str, Any]):
        await self.db.autoresponders.update_one(
            {"guild_id": guild_id},
            {"$set": {f"responders.{trigger}": config}},
            upsert=True
        )
    
    async def delete_autoresponder(self, guild_id: int, trigger: str) -> bool:
        result = await self.db.autoresponders.update_one(
            {"guild_id": guild_id},
            {"$unset": {f"responders.{trigger}": ""}}
        )
        return result.modified_count > 0
    
    async def get_invite_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        result = await self.db.invite_configs.find_one({"guild_id": guild_id})
        return result["config"] if result else None
    
    async def set_invite_config(self, guild_id: int, config: Dict[str, Any]):
        await self.db.invite_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {"config": config}},
            upsert=True
        )
    
    async def get_autorule_config(self, guild_id: int, rule_type: str) -> Optional[Dict[str, Any]]:
        result = await self.db.autorule_configs.find_one({"guild_id": guild_id})
        return result["rules"].get(rule_type) if result and "rules" in result else None
    
    async def set_autorule_config(self, guild_id: int, rule_type: str, config: Dict[str, Any]):
        await self.db.autorule_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {f"rules.{rule_type}": config}},
            upsert=True
        )
    
    async def get_all_autorule_configs(self, guild_id: int) -> Dict[str, Any]:
        result = await self.db.autorule_configs.find_one({"guild_id": guild_id})
        return result["rules"] if result and "rules" in result else {}
    
    async def set_autorule_logs_channel(self, guild_id: int, channel_id: int):
        await self.db.log_channels.update_one(
            {"guild_id": guild_id},
            {"$set": {"autorule_logs": channel_id}},
            upsert=True
        )
    
    async def get_autorule_logs_channel(self, guild_id: int) -> Optional[int]:
        result = await self.db.log_channels.find_one({"guild_id": guild_id})
        return result.get("autorule_logs") if result else None
    
    async def get_autorole_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        result = await self.db.autorole_configs.find_one({"guild_id": guild_id})
        return result["config"] if result else None
    
    async def set_autorole_config(self, guild_id: int, config: Dict[str, Any]):
        await self.db.autorole_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {"config": config}},
            upsert=True
        )
    
    async def get_automod_rule(self, guild_id: int, filter_type: str) -> Optional[Dict[str, Any]]:
        result = await self.db.automod_rules.find_one({"guild_id": guild_id})
        return result["rules"].get(filter_type) if result and "rules" in result else None
    
    async def set_automod_rule(self, guild_id: int, filter_type: str, config: Dict[str, Any]):
        await self.db.automod_rules.update_one(
            {"guild_id": guild_id},
            {"$set": {f"rules.{filter_type}": config}},
            upsert=True
        )
    
    async def get_all_automod_rules(self, guild_id: int) -> Dict[str, Any]:
        result = await self.db.automod_rules.find_one({"guild_id": guild_id})
        return result["rules"] if result and "rules" in result else {}
    
    async def get_antinuke_rule(self, guild_id: int, rule_type: str) -> Optional[Dict[str, Any]]:
        result = await self.db.antinuke_rules.find_one({"guild_id": guild_id})
        return result["rules"].get(rule_type) if result and "rules" in result else None
    
    async def set_antinuke_rule(self, guild_id: int, rule_type: str, config: Dict[str, Any]):
        await self.db.antinuke_rules.update_one(
            {"guild_id": guild_id},
            {"$set": {f"rules.{rule_type}": config}},
            upsert=True
        )
    
    async def get_all_antinuke_rules(self, guild_id: int) -> Dict[str, Any]:
        result = await self.db.antinuke_rules.find_one({"guild_id": guild_id})
        return result["rules"] if result and "rules" in result else {}
    
    async def add_extra_owner(self, guild_id: int, user_id: int):
        await self.db.extra_owners.update_one(
            {"guild_id": guild_id},
            {"$addToSet": {"owners": user_id}},
            upsert=True
        )
    
    async def get_extra_owners(self, guild_id: int) -> list[int]:
        result = await self.db.extra_owners.find_one({"guild_id": guild_id})
        return result["owners"] if result else []
    
    async def set_welcome_logs_channel(self, guild_id: int, channel_id: int):
        await self.db.log_channels.update_one(
            {"guild_id": guild_id},
            {"$set": {"welcome_logs": channel_id}},
            upsert=True
        )
    
    async def set_automod_logs_channel(self, guild_id: int, channel_id: int):
        await self.db.log_channels.update_one(
            {"guild_id": guild_id},
            {"$set": {"automod_logs": channel_id}},
            upsert=True
        )
    
    async def set_antinuke_logs_channel(self, guild_id: int, channel_id: int):
        await self.db.log_channels.update_one(
            {"guild_id": guild_id},
            {"$set": {"antinuke_logs": channel_id}},
            upsert=True
        )
    
    async def get_ticket_logs_channel(self, guild_id: int) -> Optional[int]:
        result = await self.db.ticket_configs.find_one({"guild_id": guild_id})
        return result["config"].get("logs_channel") if result and "config" in result else None
    
    async def get_embed_config(self, guild_id: int, embed_name: str) -> Optional[Dict[str, Any]]:
        result = await self.db.embed_configs.find_one({"guild_id": guild_id})
        return result["embeds"].get(embed_name) if result and "embeds" in result else None
    
    async def set_embed_setting(self, guild_id: int, embed_name: str, setting: str, value: Any):
        await self.db.embed_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {f"embeds.{embed_name}.{setting}": value}},
            upsert=True
        )
    
    async def get_all_embeds(self, guild_id: int) -> Dict[str, Any]:
        result = await self.db.embed_configs.find_one({"guild_id": guild_id})
        return result["embeds"] if result and "embeds" in result else {}
    
    async def delete_embed(self, guild_id: int, embed_name: str) -> bool:
        result = await self.db.embed_configs.update_one(
            {"guild_id": guild_id},
            {"$unset": {f"embeds.{embed_name}": ""}}
        )
        return result.modified_count > 0
    
    async def create_giveaway(self, giveaway_data: Dict[str, Any]):
        await self.db.giveaways.insert_one(giveaway_data)
    
    async def get_giveaway(self, giveaway_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.giveaways.find_one({"id": giveaway_id})
    
    async def get_giveaway_by_message(self, message_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.giveaways.find_one({"message_id": message_id})
    
    async def add_giveaway_participant(self, giveaway_id: str, user_id: int):
        await self.db.giveaways.update_one(
            {"id": giveaway_id},
            {"$addToSet": {"participants": user_id}}
        )
    
    async def remove_giveaway_participant(self, giveaway_id: str, user_id: int):
        await self.db.giveaways.update_one(
            {"id": giveaway_id},
            {"$pull": {"participants": user_id}}
        )
    
    async def end_giveaway(self, giveaway_id: str):
        await self.db.giveaways.update_one(
            {"id": giveaway_id},
            {"$set": {"ended": True}}
        )
    
    async def get_guild_giveaways(self, guild_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.giveaways.find({"guild_id": guild_id}).sort("end_time", -1)
        return await cursor.to_list(length=None)
    
    async def delete_giveaway(self, giveaway_id: str):
        await self.db.giveaways.delete_one({"id": giveaway_id})
    
    async def pause_giveaway(self, giveaway_id: str, paused: bool):
        await self.db.giveaways.update_one(
            {"id": giveaway_id},
            {"$set": {"paused": paused}}
        )
    
    async def get_guild_invites(self, guild_id: int) -> Dict[str, Dict[str, int]]:
        result = await self.db.invite_stats.find_one({"guild_id": guild_id})
        return result["users"] if result and "users" in result else {}
    
    async def get_user_invites(self, guild_id: int, user_id: int) -> Optional[Dict[str, int]]:
        result = await self.db.invite_stats.find_one({"guild_id": guild_id})
        if result and "users" in result:
            return result["users"].get(str(user_id))
        return None
    
    async def set_user_invites(self, guild_id: int, user_id: int, invite_data: Dict[str, int]):
        await self.db.invite_stats.update_one(
            {"guild_id": guild_id},
            {"$set": {f"users.{user_id}": invite_data}},
            upsert=True
        )
    
    async def reset_user_invites(self, guild_id: int, user_id: int):
        await self.db.invite_stats.update_one(
            {"guild_id": guild_id},
            {"$unset": {f"users.{user_id}": ""}}
        )
    
    async def add_user_invites(self, guild_id: int, user_id: int, amount: int):
        current = await self.get_user_invites(guild_id, user_id) or {"total": 0, "valid": 0, "fake": 0, "left": 0}
        current["total"] += amount
        current["valid"] += amount
        await self.set_user_invites(guild_id, user_id, current)
    
    async def remove_user_invites(self, guild_id: int, user_id: int, amount: int):
        current = await self.get_user_invites(guild_id, user_id) or {"total": 0, "valid": 0, "fake": 0, "left": 0}
        current["total"] = max(0, current["total"] - amount)
        current["valid"] = max(0, current["valid"] - amount)
        await self.set_user_invites(guild_id, user_id, current)
    
    async def get_boost_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        result = await self.db.boost_configs.find_one({"guild_id": guild_id})
        return result["config"] if result else None
    
    async def set_boost_setting(self, guild_id: int, setting: str, value: Any):
        await self.db.boost_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {f"config.{setting}": value}},
            upsert=True
        )
    
    async def reset_boost_config(self, guild_id: int):
        await self.db.boost_configs.delete_one({"guild_id": guild_id})
    
    async def get_leave_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        result = await self.db.leave_configs.find_one({"guild_id": guild_id})
        return result["config"] if result else None
    
    async def set_leave_setting(self, guild_id: int, setting: str, value: Any):
        await self.db.leave_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {f"config.{setting}": value}},
            upsert=True
        )
    
    async def reset_leave_config(self, guild_id: int):
        await self.db.leave_configs.delete_one({"guild_id": guild_id})
    
    async def get_ticket_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        result = await self.db.ticket_configs.find_one({"guild_id": guild_id})
        return result["config"] if result else None
    
    async def set_ticket_setting(self, guild_id: int, setting: str, value: Any):
        await self.db.ticket_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {f"config.{setting}": value}},
            upsert=True
        )
    
    async def add_ticket_category(self, guild_id: int, category: Dict[str, str]):
        await self.db.ticket_configs.update_one(
            {"guild_id": guild_id},
            {"$push": {"config.categories": category}},
            upsert=True
        )
    
    async def set_ticket_category_channel(self, guild_id: int, category_value: str, channel_id: int):
        await self.db.ticket_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {f"config.category_channels.{category_value}": channel_id}},
            upsert=True
        )
    
    async def set_ticket_logs_channel(self, guild_id: int, channel_id: int):
        await self.db.ticket_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {"config.logs_channel": channel_id}},
            upsert=True
        )
    
    async def reset_ticket_config(self, guild_id: int):
        await self.db.ticket_configs.delete_one({"guild_id": guild_id})
    
    async def reset_embed_configs(self, guild_id: int):
        await self.db.embed_configs.delete_one({"guild_id": guild_id})
    
    async def set_premium_user(self, user_id: int, expiry_date):
        data = {"user_id": user_id, "granted_at": datetime.now()}
        if expiry_date:
            data["expiry"] = expiry_date
        await self.db.premium_users.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )
    
    async def get_premium_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.premium_users.find_one({"user_id": user_id})
    
    async def remove_premium_user(self, user_id: int):
        await self.db.premium_users.delete_one({"user_id": user_id})
    
    async def get_all_premium_users(self) -> List[Dict[str, Any]]:
        cursor = self.db.premium_users.find({})
        return await cursor.to_list(length=None)
    
    async def set_premium_music_mode(self, user_id: int, mode: str):
        await self.db.premium_users.update_one(
            {"user_id": user_id},
            {"$set": {"music_mode": mode}},
            upsert=True
        )
    
    async def get_premium_music_mode(self, user_id: int) -> Optional[str]:
        result = await self.db.premium_users.find_one({"user_id": user_id})
        return result.get("music_mode") if result else None
    
    async def set_premium_guild(self, guild_id: int, activator_id: int):
        await self.db.premium_guilds.update_one(
            {"guild_id": guild_id},
            {"$set": {"activator_id": activator_id, "activated_at": datetime.now()}},
            upsert=True
        )
    
    async def get_premium_guild(self, guild_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.premium_guilds.find_one({"guild_id": guild_id})
    
    async def get_user_premium_guilds(self, user_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.premium_guilds.find({"activator_id": user_id})
        return await cursor.to_list(length=None)
    
    async def remove_premium_guild(self, guild_id: int):
        await self.db.premium_guilds.delete_one({"guild_id": guild_id})
    
    async def get_levelup_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        result = await self.db.levelup_configs.find_one({"guild_id": guild_id})
        return result["config"] if result else None
    
    async def set_levelup_setting(self, guild_id: int, setting: str, value: Any):
        await self.db.levelup_configs.update_one(
            {"guild_id": guild_id},
            {"$set": {f"config.{setting}": value}},
            upsert=True
        )
    
    async def reset_levelup_config(self, guild_id: int):
        await self.db.levelup_configs.delete_one({"guild_id": guild_id})
    
    async def get_user_xp(self, guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.user_xp.find_one({"guild_id": guild_id, "user_id": user_id})
    
    async def set_user_xp(self, guild_id: int, user_id: int, xp: int, level: int):
        await self.db.user_xp.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"xp": xp, "level": level}},
            upsert=True
        )
    
    async def get_leaderboard(self, guild_id: int, page: int = 0) -> List[Dict[str, Any]]:
        skip = page * 10
        cursor = self.db.user_xp.find({"guild_id": guild_id}).sort("xp", -1).skip(skip).limit(10)
        return await cursor.to_list(length=10)
    
    async def set_afk_user(self, user_id: int, reason: str, dm_enabled: bool = True):
        await self.db.afk_users.update_one(
            {"user_id": user_id},
            {"$set": {"reason": reason, "dm_enabled": dm_enabled}},
            upsert=True
        )
    
    async def get_afk_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.afk_users.find_one({"user_id": user_id})
    
    async def remove_afk_user(self, user_id: int):
        await self.db.afk_users.delete_one({"user_id": user_id})
    
    async def add_whitelist_user(self, guild_id: int, user_id: int):
        await self.db.whitelist_users.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"guild_id": guild_id, "user_id": user_id}},
            upsert=True
        )
    
    async def get_whitelist_user(self, guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        return await self.db.whitelist_users.find_one({"guild_id": guild_id, "user_id": user_id})
    
    async def get_whitelist_users(self, guild_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.whitelist_users.find({"guild_id": guild_id})
        return await cursor.to_list(length=None)
    
    async def remove_whitelist_user(self, guild_id: int, user_id: int):
        await self.db.whitelist_users.delete_one({"guild_id": guild_id, "user_id": user_id})
    
    async def is_whitelisted(self, guild_id: int, user_id: int) -> bool:
        """Check if user is whitelisted (includes owners)"""
        # Get guild to check ownership
        guild = self.client.get_guild(guild_id) if hasattr(self, 'client') else None
        
        # Server owner is always whitelisted
        if guild and guild.owner_id == user_id:
            return True
        
        # Extra owners (bot admins) are always whitelisted
        extra_owners = [1037768611126841405]
        if user_id in extra_owners:
            return True
        
        # Check database whitelist
        whitelist_data = await self.get_whitelist_user(guild_id, user_id)
        return whitelist_data is not None