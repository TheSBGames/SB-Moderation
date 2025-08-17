from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
from core.config import Config
from core.logger import get_logger
import asyncio
from typing import Dict, Any, Optional, List
from cachetools import TTLCache
import time

class Database:
    def __init__(self):
        # Initialize MongoDB connection with connection pooling
        self.client = AsyncIOMotorClient(
            Config.MONGO_URI,
            maxPoolSize=Config.MONGO_MAX_POOL_SIZE,
            minPoolSize=Config.MONGO_MIN_POOL_SIZE,
            retryWrites=True,
            retryReads=True
        )
        self.db = self.client.get_default_database()
        
        # Initialize caches
        self.cache_config = Config.get_cache_config()
        self.guild_cache = TTLCache(**self.cache_config)
        self.user_cache = TTLCache(**self.cache_config)
        
        # Track query metrics
        self.query_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Initialize collections with proper indexes
        self._init_collections()

    async def _init_collections(self):
        """Initialize collections and indexes."""
        try:
            # Guild settings indexes
            await self.db.guild_settings.create_indexes([
                IndexModel([("_id", ASCENDING)]),
                IndexModel([("prefix", ASCENDING)]),
                IndexModel([("automod.enabled", ASCENDING)])
            ])
            
            # User data indexes
            await self.db.users.create_indexes([
                IndexModel([("_id", ASCENDING)]),
                IndexModel([("guild_id", ASCENDING)]),
                IndexModel([("warns", ASCENDING)]),
                IndexModel([("xp", DESCENDING)])
            ])
            
            # Tickets indexes
            await self.db.tickets.create_indexes([
                IndexModel([("guild_id", ASCENDING)]),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)])
            ])
            
            # Auto-mod logs indexes
            await self.db.automod_logs.create_indexes([
                IndexModel([("guild_id", ASCENDING)]),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("action", ASCENDING)]),
                IndexModel([("timestamp", DESCENDING)])
            ])
            
            get_logger().info("Database indexes created successfully")
            
        except Exception as e:
            get_logger().error(f"Error creating database indexes: {str(e)}")

    async def get_guild_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get guild settings with caching."""
        # Check cache first
        cache_key = f"guild:{guild_id}"
        if cache_key in self.guild_cache:
            self.cache_hits += 1
            return self.guild_cache[cache_key]

        # Query database with timeout
        start_time = time.time()
        try:
            settings = await asyncio.wait_for(
                self.db.guild_settings.find_one({"_id": guild_id}),
                timeout=5.0
            )
            
            # Update cache and metrics
            if settings:
                self.guild_cache[cache_key] = settings
            self.cache_misses += 1
            self.query_times.append(time.time() - start_time)
            
            return settings
            
        except asyncio.TimeoutError:
            get_logger().error(f"Database timeout getting guild settings for {guild_id}")
            return None
        except Exception as e:
            get_logger().error(f"Database error getting guild settings: {str(e)}")
            return None

    async def update_guild_settings(self, guild_id: int, update: Dict[str, Any]) -> bool:
        """Update guild settings with cache invalidation."""
        try:
            result = await self.db.guild_settings.update_one(
                {"_id": guild_id},
                {"$set": update},
                upsert=True
            )
            
            # Invalidate cache
            cache_key = f"guild:{guild_id}"
            if cache_key in self.guild_cache:
                del self.guild_cache[cache_key]
                
            return result.modified_count > 0 or result.upserted_id is not None
            
        except Exception as e:
            get_logger().error(f"Database error updating guild settings: {str(e)}")
            return False

    async def get_user_data(self, guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data with caching."""
        cache_key = f"user:{guild_id}:{user_id}"
        if cache_key in self.user_cache:
            self.cache_hits += 1
            return self.user_cache[cache_key]

        try:
            data = await self.db.users.find_one({
                "guild_id": guild_id,
                "_id": user_id
            })
            
            if data:
                self.user_cache[cache_key] = data
            self.cache_misses += 1
            
            return data
            
        except Exception as e:
            get_logger().error(f"Database error getting user data: {str(e)}")
            return None

    async def bulk_get_users(self, guild_id: int, user_ids: List[int]) -> List[Dict[str, Any]]:
        """Efficiently get data for multiple users."""
        try:
            # Get cached users
            cached_users = {}
            missing_ids = []
            
            for user_id in user_ids:
                cache_key = f"user:{guild_id}:{user_id}"
                if cache_key in self.user_cache:
                    cached_users[user_id] = self.user_cache[cache_key]
                    self.cache_hits += 1
                else:
                    missing_ids.append(user_id)
            
            # Query database for missing users
            if missing_ids:
                cursor = self.db.users.find({
                    "guild_id": guild_id,
                    "_id": {"$in": missing_ids}
                })
                
                async for user in cursor:
                    user_id = user["_id"]
                    cache_key = f"user:{guild_id}:{user_id}"
                    self.user_cache[cache_key] = user
                    cached_users[user_id] = user
                    self.cache_misses += 1
            
            return [cached_users.get(user_id) for user_id in user_ids]
            
        except Exception as e:
            get_logger().error(f"Database error in bulk user fetch: {str(e)}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        avg_query_time = sum(self.query_times) / len(self.query_times) if self.query_times else 0
        cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        return {
            "average_query_time": avg_query_time,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cached_guilds": len(self.guild_cache),
            "cached_users": len(self.user_cache)
        }

    async def close(self):
        """Cleanup database resources."""
        # Clear caches
        self.guild_cache.clear()
        self.user_cache.clear()
        
        # Close MongoDB connection
        self.client.close()
        get_logger().info("Database connection closed")