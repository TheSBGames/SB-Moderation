import discord
from discord.ext import commands, tasks
from core.config import PREFIX, SHARD_COUNT, Config
from core.database import Database
from core.logger import get_logger
import asyncio
import time
import os
from typing import Dict, Any
from cachetools import TTLCache
from prometheus_client import Counter, Histogram
import psutil
import functools

# Metrics for monitoring
COMMAND_COUNTER = Counter('bot_commands_total', 'Number of commands processed')
COMMAND_LATENCY = Histogram('bot_command_latency_seconds', 'Command processing latency')
ERROR_COUNTER = Counter('bot_errors_total', 'Number of errors encountered')
GUILD_COUNTER = Counter('bot_guilds_total', 'Number of guilds the bot is in')

class Bot(commands.AutoShardedBot):
    def __init__(self, command_prefix=PREFIX, **options):
        intents = discord.Intents.default()
        intents.members = True  # Enable member intents for role management
        intents.message_content = True  # Enable message content for moderation
        
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            shard_count=SHARD_COUNT,
            chunk_guilds_at_startup=False,  # Disable automatic guild chunking
            member_cache_flags=discord.MemberCacheFlags.none(),  # Minimal member caching
            **options
        )
        
        # Initialize database with connection pooling
        self.db = Database()
        self.author_credit = "Powered By SB Moderation™"
        
        # Caches
        self.prefix_cache = TTLCache(maxsize=10000, ttl=300)  # 5-minute TTL
        self.settings_cache = TTLCache(maxsize=10000, ttl=600)  # 10-minute TTL
        self.cooldowns = TTLCache(maxsize=100000, ttl=60)  # 1-minute TTL
        
        # Rate limiting
        self.global_rate_limit = commands.CooldownMapping.from_cooldown(
            30, 10, commands.BucketType.user
        )
        
        # Performance monitoring
        self.start_time = time.time()
        self.command_latency = []  # Rolling average of command latencies
        
        # Background tasks
        self.maintenance_task.start()
        self.metrics_task.start()

    async def setup_hook(self):
        """Initialize bot settings and connections."""
        try:
            # Connect to MongoDB first
            await self.db.connect()
            get_logger().info("Connected to MongoDB")
            
            # Load extensions
            extension_dir = os.path.join(os.path.dirname(__file__), "..", "cogs")
            loaded_extensions = []
            
            for folder in os.listdir(extension_dir):
                folder_path = os.path.join(extension_dir, folder)
                if os.path.isdir(folder_path):
                    for file in os.listdir(folder_path):
                        if file.endswith(".py") and not file.startswith("_"):
                            extension_path = f"cogs.{folder}.{file[:-3]}"
                            try:
                                await self.load_extension(extension_path)
                                loaded_extensions.append(extension_path)
                            except Exception as e:
                                get_logger().error(f"Failed to load extension {extension_path}: {str(e)}")

            get_logger().info(f"Loaded {len(loaded_extensions)} extensions")

            # Initialize Top.gg webhook if configured
            topgg_token = os.getenv('TOPGG_TOKEN')
            topgg_auth = os.getenv('TOPGG_WEBHOOK_AUTH')
            if topgg_token and topgg_auth:
                try:
                    from core.topgg_webhook import TopGGWebhook
                    self.topgg_webhook = TopGGWebhook(self, topgg_auth)
                    await self.topgg_webhook.start()
                    get_logger().info("Top.gg webhook initialized")
                except Exception as e:
                    get_logger().error(f"Failed to initialize Top.gg webhook: {str(e)}")
                    self.topgg_webhook = None

        except Exception as e:
            get_logger().error(f"Error in setup_hook: {str(e)}")
            raise

    async def on_ready(self):
        """Handle bot ready event and initialize metrics."""
        get_logger().info(f'Logged in as {self.user.name} - {self.user.id}')
        get_logger().info(f'Serving {len(self.guilds)} guilds across {self.shard_count} shards')
        GUILD_COUNTER.inc(len(self.guilds))
        
        # Set bot status based on config
        status_type = Config.STATUS_TYPE.lower()
        if status_type == "playing":
            activity = discord.Game(name=Config.STATUS_NAME)
        elif status_type == "streaming":
            activity = discord.Streaming(name=Config.STATUS_NAME, url=Config.STATUS_URL)
        elif status_type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=Config.STATUS_NAME)
        elif status_type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=Config.STATUS_NAME)
        elif status_type == "competing":
            activity = discord.Activity(type=discord.ActivityType.competing, name=Config.STATUS_NAME)
        else:
            activity = discord.Game(name=Config.STATUS_NAME)
            
        await self.change_presence(activity=activity)
        get_logger().info(f"Set status to: {status_type} {Config.STATUS_NAME}")
        
        # Initialize shard status
        for shard_id in range(self.shard_count):
            get_logger().info(f'Shard {shard_id}: {len([g for g in self.guilds if g.shard_id == shard_id])} guilds')

    async def get_prefix(self, message):
        """Get guild prefix with caching."""
        if not message.guild:
            return PREFIX
            
        # Check cache first
        cache_key = f"prefix:{message.guild.id}"
        if cache_key in self.prefix_cache:
            return self.prefix_cache[cache_key]
            
        # Check for no-prefix users
        if message.author.id in await self.db.noprefix_users.distinct('_id'):
            return [""]
            
        # Get guild prefix from database
        prefix = await self.db.guild_settings.find_one(
            {'_id': message.guild.id},
            {'prefix': 1}
        )
        
        # Cache the result
        result = prefix.get('prefix', PREFIX) if prefix else PREFIX
        self.prefix_cache[cache_key] = result
        return result

    async def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get guild settings with caching."""
        cache_key = f"settings:{guild_id}"
        
        # Check cache first
        if cache_key in self.settings_cache:
            return self.settings_cache[cache_key]
            
        # Get from database
        settings = await self.db.guild_settings.find_one({'_id': guild_id})
        if settings:
            self.settings_cache[cache_key] = settings
            return settings
            
        return {}

    async def process_commands(self, message):
        """Process commands with rate limiting and metrics."""
        if message.author.bot:
            return

        # Apply global rate limit
        bucket = self.global_rate_limit.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return
            
        # Measure command latency
        start_time = time.time()
        
        try:
            await super().process_commands(message)
            COMMAND_COUNTER.inc()
            
            # Record command latency
            latency = time.time() - start_time
            COMMAND_LATENCY.observe(latency)
            self.command_latency.append(latency)
            if len(self.command_latency) > 100:
                self.command_latency.pop(0)
                
        except Exception as e:
            ERROR_COUNTER.inc()
            get_logger().error(f"Error processing command: {str(e)}")
            await self.handle_error(message.channel, e)

    async def handle_error(self, channel, error):
        """Unified error handling."""
        try:
            if isinstance(error, commands.CommandOnCooldown):
                await channel.send(f"Please wait {error.retry_after:.1f}s before using this command again.")
            elif isinstance(error, commands.MissingPermissions):
                await channel.send("You don't have permission to use this command.")
            else:
                await channel.send("An error occurred. Please try again later.")
        except:
            pass  # Fail silently if we can't send error message

    @tasks.loop(minutes=5)
    async def maintenance_task(self):
        """Regular maintenance operations."""
        try:
            # Clear expired cache entries
            self.prefix_cache.expire()
            self.settings_cache.expire()
            self.cooldowns.expire()
            
            # Log performance metrics
            memory = psutil.Process().memory_info().rss / 1024 / 1024
            cpu = psutil.Process().cpu_percent()
            avg_latency = sum(self.command_latency) / len(self.command_latency) if self.command_latency else 0
            
            get_logger().info(f"Performance metrics: Memory: {memory:.1f}MB, CPU: {cpu}%, Latency: {avg_latency*1000:.1f}ms")
            
        except Exception as e:
            get_logger().error(f"Maintenance task error: {str(e)}")
            ERROR_COUNTER.inc()

    @tasks.loop(minutes=1)
    async def metrics_task(self):
        """Update Prometheus metrics."""
        if not self.is_ready():
            return
            
        try:
            # Get total guild count across all shards
            guild_count = len(self.guilds)
            GUILD_COUNTER.set(guild_count)  # Use set instead of inc to avoid cumulative counting
            
            # Update latency metrics
            if self.latency is not None:
                COMMAND_LATENCY.observe(self.latency)
                
            # Log metrics update
            get_logger().debug(
                "Updated metrics",
                extra={
                    'guilds': guild_count,
                    'latency': self.latency,
                    'commands': COMMAND_COUNTER._value.get()
                }
            )
                
        except Exception as e:
            get_logger().error(f"Metrics task error: {str(e)}")
            ERROR_COUNTER.inc()
    
    @metrics_task.before_loop
    async def before_metrics_task(self):
        """Wait until bot is ready before starting metrics."""
        await self.wait_until_ready()
    
    async def close(self):
        """Cleanup on shutdown."""
        # Stop background tasks
        self.maintenance_task.cancel()
        self.metrics_task.cancel()
        
        # Close database connection
        await self.db.close()
        
        # Clear caches
        self.prefix_cache.clear()
        self.settings_cache.clear()
        self.cooldowns.clear()
        
        await super().close()