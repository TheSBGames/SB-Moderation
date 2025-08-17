import os
import math
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

def calculate_shard_count() -> int:
    """Calculate optimal shard count based on guild count."""
    guild_count = int(os.getenv("EXPECTED_GUILD_COUNT", 10000))
    # Discord recommends 1000-1500 guilds per shard
    return max(1, math.ceil(guild_count / 1000))

class Config:
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("DISCORD_TOKEN")
    OWNER_ID: int = int(os.getenv("OWNER_ID", 1186506712040099850))
    
    # Default Bot Settings (hardcoded, can be overridden per guild)
    DEFAULT_PREFIX: str = "&"
    DEFAULT_LOG_LEVEL: str = "INFO"
    
    # Bot Status Configuration
    STATUS_TYPE: str = "listening"  # playing, streaming, listening, watching, competing
    STATUS_NAME: str = "SB"
    STATUS_URL: str = ""  # Only used if status_type is "streaming"
    
    # Music System Configuration (hardcoded)
    LAVALINK_CONFIG = {
        "host": "localhost",
        "port": 2333,
        "password": "youshallnotpass",
        "identifier": "Main Node",
        "region": "us_central"
    }
    
    # Sharding Configuration
    SHARD_COUNT: int = int(os.getenv("SHARD_COUNT", calculate_shard_count()))
    SHARD_IDS: list = None  # Will be set by the launcher for each instance
    
    # Database Configuration
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGO_MAX_POOL_SIZE: int = int(os.getenv("MONGO_MAX_POOL_SIZE", 100))
    MONGO_MIN_POOL_SIZE: int = int(os.getenv("MONGO_MIN_POOL_SIZE", 10))
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 300))  # 5 minutes
    MAX_CACHE_SIZE: int = int(os.getenv("MAX_CACHE_SIZE", 10000))
    
    # Rate Limiting
    GLOBAL_RATE_LIMIT: int = int(os.getenv("GLOBAL_RATE_LIMIT", 30))  # commands per
    GLOBAL_RATE_LIMIT_PERIOD: int = int(os.getenv("GLOBAL_RATE_LIMIT_PERIOD", 10))  # seconds
    
    # Performance Settings
    CHUNK_GUILDS_AT_STARTUP: bool = os.getenv("CHUNK_GUILDS_AT_STARTUP", "false").lower() == "true"
    MEMBER_CACHE_FLAGS: str = os.getenv("MEMBER_CACHE_FLAGS", "NONE")  # NONE, ALL, or specific flags
    
    # Feature Intervals (in seconds)
    METRICS_UPDATE_INTERVAL: int = int(os.getenv("METRICS_UPDATE_INTERVAL", 60))
    MAINTENANCE_INTERVAL: int = int(os.getenv("MAINTENANCE_INTERVAL", 300))
    
    # YouTube Configuration
    YT_MAX_SUBSCRIPTIONS: int = 0  # 0 means unlimited
    YT_NOTIFY_RETRY_ATTEMPTS: int = 3
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", 8000))
    
    # Error Reporting
    ERROR_WEBHOOK_URL: str = os.getenv("ERROR_WEBHOOK_URL")
    ERROR_CHANNEL_ID: int = int(os.getenv("ERROR_CHANNEL_ID", 0))

    # Top.gg Configuration
    TOPGG_TOKEN: str = os.getenv("TOPGG_TOKEN")
    TOPGG_WEBHOOK_AUTH: str = os.getenv("TOPGG_WEBHOOK_AUTH")
    TOPGG_WEBHOOK_URL: str = os.getenv("TOPGG_WEBHOOK_URL")
    TOPGG_WEBHOOK_PORT: int = int(os.getenv("TOPGG_WEBHOOK_PORT", 8080))
    
    @classmethod
    def get_shard_config(cls) -> Dict[str, Any]:
        """Get shard configuration for bot initialization."""
        return {
            "shard_count": cls.SHARD_COUNT,
            "shard_ids": cls.SHARD_IDS
        }
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            "ttl": cls.CACHE_TTL,
            "maxsize": cls.MAX_CACHE_SIZE
        }
    
    @classmethod
    def get_mongo_config(cls) -> Dict[str, Any]:
        """Get MongoDB configuration."""
        return {
            "uri": cls.MONGO_URI,
            "maxPoolSize": cls.MONGO_MAX_POOL_SIZE,
            "minPoolSize": cls.MONGO_MIN_POOL_SIZE
        }