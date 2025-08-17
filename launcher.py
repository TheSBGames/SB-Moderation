import os
import sys
import asyncio
import logging
from core.bot import Bot
from core.config import Config
from core.logger import get_logger
import discord
from prometheus_client import start_http_server
import uvloop
import signal
import psutil

# Use uvloop for better performance
if sys.platform != 'win32':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Launcher:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.bots = []
        self.shutting_down = False
        
        # Set up signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            self.loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self.handle_signal(s)))

    async def handle_signal(self, sig):
        """Handle shutdown signals gracefully."""
        if self.shutting_down:
            return
            
        self.shutting_down = True
        get_logger().info(f"Received signal {sig.name}, initiating graceful shutdown...")
        
        # Stop accepting new commands
        for bot in self.bots:
            bot.maintenance_mode = True
        
        # Wait for ongoing commands to finish (max 10 seconds)
        await asyncio.sleep(10)
        
        # Close all bots
        await asyncio.gather(*[bot.close() for bot in self.bots])
        
        # Stop the event loop
        self.loop.stop()

    async def launch(self):
        """Launch bot shards."""
        # Start Prometheus metrics server
        if Config.PROMETHEUS_PORT:
            start_http_server(Config.PROMETHEUS_PORT)
            get_logger().info(f"Prometheus metrics server started on port {Config.PROMETHEUS_PORT}")
        
        try:
            # Calculate shard distribution
            shard_count = Config.SHARD_COUNT
            get_logger().info(f"Launching bot with {shard_count} shards")
            
            # Launch shards
            for shard_id in range(shard_count):
                Config.SHARD_IDS = [shard_id]
                
                # Create bot instance
                bot = Bot()
                
                self.bots.append(bot)
                
                # Start bot in background
                self.loop.create_task(self.start_bot(bot, shard_id))
                
                # Wait between shard launches to prevent rate limiting
                await asyncio.sleep(5)
            
            # Keep the loop running
            await asyncio.gather(*[asyncio.Event().wait() for _ in range(shard_count)])
            
        except Exception as e:
            get_logger().error(f"Error in launcher: {str(e)}")
            raise

    async def start_bot(self, bot, shard_id):
        """Start a bot instance with error handling and auto-restart."""
        retries = 0
        max_retries = 5
        
        while retries < max_retries and not self.shutting_down:
            try:
                get_logger().info(f"Starting shard {shard_id}")
                await bot.start(Config.BOT_TOKEN)
                break
                
            except discord.errors.LoginFailure:
                get_logger().error("Invalid token, cannot continue")
                return
                
            except Exception as e:
                retries += 1
                get_logger().error(f"Error in shard {shard_id}: {str(e)}")
                
                if retries < max_retries:
                    wait_time = 2 ** retries  # Exponential backoff
                    get_logger().info(f"Retrying shard {shard_id} in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    get_logger().error(f"Shard {shard_id} failed to start after {max_retries} attempts")

    def run(self):
        """Run the launcher."""
        try:
            # Check system resources
            memory = psutil.virtual_memory()
            cpu_count = psutil.cpu_count()
            
            get_logger().info(f"System info: {cpu_count} CPUs, {memory.total / (1024**3):.1f}GB RAM")
            
            # Set resource limits
            if sys.platform != 'win32':
                import resource
                resource.setrlimit(resource.RLIMIT_NOFILE, (50000, 50000))
            
            # Run the bot
            self.loop.run_until_complete(self.launch())
            
        except KeyboardInterrupt:
            get_logger().info("Received keyboard interrupt")
        except Exception as e:
            get_logger().error(f"Launcher error: {str(e)}")
        finally:
            # Cleanup
            self.loop.run_until_complete(self.cleanup())
            self.loop.close()

    async def cleanup(self):
        """Clean up resources."""
        if not self.shutting_down:
            self.shutting_down = True
            
            # Close all bot instances
            for bot in self.bots:
                await bot.close()
            
            # Clear any remaining tasks
            pending = asyncio.all_tasks(self.loop)
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()
