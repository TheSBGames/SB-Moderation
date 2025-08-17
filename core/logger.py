import logging
import os
import json
import asyncio
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import discord
from datetime import datetime
import traceback
from typing import Dict, Any, List
import aiohttp
from core.config import Config

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

class DiscordWebhookHandler(logging.Handler):
    def __init__(self, webhook_url: str):
        super().__init__()
        self.webhook_url = webhook_url
        self.queue: List[Dict[str, str]] = []
        self.max_queue = 10
        self.lock = asyncio.Lock()
        self.flush_task = None
        self.session = None

    async def ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def emit(self, record):
        if not self.webhook_url:
            return

        try:
            # Format the record
            msg = self.format(record)
            
            # Format with code block and add metadata
            content = f"```{msg}```"
            if hasattr(record, 'shard_id'):
                content = f"[Shard {record.shard_id}] {content}"
            
            # Add to queue
            self.queue.append({
                'content': content,
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname
            })
            
            # If queue is full or error level is high, send logs
            if len(self.queue) >= self.max_queue or record.levelno >= logging.ERROR:
                if self.flush_task is None or self.flush_task.done():
                    self.flush_task = asyncio.create_task(self.flush_queue())
                
        except Exception as e:
            print(f"Error in webhook handler: {str(e)}")
            traceback.print_exc()

    async def flush_queue(self):
        if not self.queue:
            return

        async with self.lock:
            try:
                session = await self.ensure_session()
                
                # Group messages by level
                levels = {'ERROR': [], 'WARNING': [], 'INFO': [], 'DEBUG': []}
                for msg in self.queue:
                    levels[msg['level']].append(msg['content'])
                
                # Send each level separately
                for level, messages in levels.items():
                    if not messages:
                        continue
                        
                    # Combine messages
                    combined = '\n'.join(messages)
                    
                    # Split into chunks if too long
                    chunks = [combined[i:i+1900] for i in range(0, len(combined), 1900)]
                    
                    for i, chunk in enumerate(chunks):
                        embed = {
                            'title': f'{level} Logs (Part {i+1}/{len(chunks)})' if len(chunks) > 1 else f'{level} Logs',
                            'description': chunk,
                            'color': {
                                'ERROR': 0xFF0000,
                                'WARNING': 0xFFAA00,
                                'INFO': 0x00AA00,
                                'DEBUG': 0x0000AA
                            }.get(level, 0x000000),
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        
                        await session.post(
                            self.webhook_url,
                            json={'embeds': [embed]},
                            timeout=aiohttp.ClientTimeout(total=10)
                        )
                        await asyncio.sleep(1)  # Rate limit protection
                        
                self.queue.clear()
                
            except Exception as e:
                print(f"Error flushing webhook queue: {str(e)}")
                traceback.print_exc()

    async def close(self):
        """Close the handler and its resources."""
        if self.session:
            await self.session.close()
            self.session = None

class JSONFormatter(logging.Formatter):
    def format(self, record):
        """Format the log record as JSON with enhanced metadata."""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'process_id': record.process,
                'thread_id': record.thread
            }
            
            # Add shard and guild context if available
            if hasattr(record, 'shard_id'):
                log_data['shard_id'] = record.shard_id
            if hasattr(record, 'guild_id'):
                log_data['guild_id'] = record.guild_id
            
            # Add user context if available
            if hasattr(record, 'user_id'):
                log_data['user_id'] = record.user_id
            if hasattr(record, 'channel_id'):
                log_data['channel_id'] = record.channel_id
            
            # Add command context if available
            if hasattr(record, 'command'):
                log_data['command'] = record.command
                
            # Add custom fields from extra
            if hasattr(record, 'extra'):
                log_data.update(record.extra)
            
            # Add exception information if available
            if record.exc_info:
                log_data['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': traceback.format_exception(*record.exc_info)
                }
            
            # Add stack info if available
            if record.stack_info:
                log_data['stack_info'] = record.stack_info
                
            return json.dumps(log_data, ensure_ascii=False)
            
        except Exception as e:
            # Fallback if JSON formatting fails
            return f"Error formatting log as JSON: {str(e)}\nOriginal message: {record.getMessage()}"

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("SB Moderation")
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate logs
        self.logger.propagate = False
        
        try:
            # Create formatters
            json_formatter = JSONFormatter()
            console_formatter = logging.Formatter(
                '%(asctime)s - [%(levelname)s] - %(message)s - {%(module)s:%(lineno)d}'
            )
            
            # Console handler with color support
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
            
            # Ensure logs directory exists
            os.makedirs("logs", exist_ok=True)
            
            # Rotating file handler for all logs
            if os.getenv("LOG_TO_FILE", "true").lower() == "true":
                file_handler = RotatingFileHandler(
                    "logs/sb_moderation.log",
                    maxBytes=50_000_000,  # 50MB
                    backupCount=10,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(json_formatter)
                self.logger.addHandler(file_handler)
                
            # Separate error log file
            error_handler = TimedRotatingFileHandler(
                "logs/error.log",
                when="midnight",
                interval=1,
                backupCount=30,  # Keep a month of error logs
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(json_formatter)
            self.logger.addHandler(error_handler)
            
            # Debug log file
            if os.getenv("DEBUG", "false").lower() == "true":
                debug_handler = RotatingFileHandler(
                    "logs/debug.log",
                    maxBytes=20_000_000,  # 20MB
                    backupCount=3,
                    encoding='utf-8'
                )
                debug_handler.setLevel(logging.DEBUG)
                debug_handler.setFormatter(json_formatter)
                self.logger.addHandler(debug_handler)
            
            # Discord webhook for critical errors
            if Config.ERROR_WEBHOOK_URL:
                webhook_handler = DiscordWebhookHandler(Config.ERROR_WEBHOOK_URL)
                webhook_handler.setLevel(logging.ERROR)
                webhook_handler.setFormatter(console_formatter)
                self.logger.addHandler(webhook_handler)
                
        except Exception as e:
            # Basic console output if setup fails
            print(f"Error setting up logger: {str(e)}")
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(console_handler)

    def get_logger(self):
        """Get the logger instance."""
        return self.logger

    def log_command(self, ctx: discord.ext.commands.Context, command_name: str, **kwargs):
        """Log command usage with enhanced context."""
        try:
            extra = {
                'shard_id': ctx.guild.shard_id if ctx.guild else 0,
                'guild_id': ctx.guild.id if ctx.guild else None,
                'channel_id': ctx.channel.id,
                'user_id': ctx.author.id,
                'user_name': str(ctx.author),
                'command': command_name,
                'command_type': ctx.command.cog_name if ctx.command else None,
                'is_slash_command': isinstance(ctx.interaction, discord.Interaction),
                'channel_type': str(ctx.channel.type),
                'permissions': str(ctx.channel.permissions_for(ctx.guild.me)) if ctx.guild else None
            }
            extra.update(kwargs)
            
            self.logger.info(
                f"Command {command_name} used by {ctx.author} in {ctx.guild or 'DM'}",
                extra=extra
            )
        except Exception as e:
            self.logger.error(f"Error in log_command: {str(e)}")

    def log_error(self, error: Exception, ctx: discord.ext.commands.Context = None, **kwargs):
        """Log errors with comprehensive context."""
        try:
            extra = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'error_traceback': ''.join(traceback.format_tb(error.__traceback__)),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if ctx:
                extra.update({
                    'shard_id': ctx.guild.shard_id if ctx.guild else 0,
                    'guild_id': ctx.guild.id if ctx.guild else None,
                    'channel_id': ctx.channel.id,
                    'user_id': ctx.author.id,
                    'user_name': str(ctx.author),
                    'command': ctx.command.name if ctx.command else None,
                    'command_type': ctx.command.cog_name if ctx.command else None,
                    'message_content': ctx.message.content if hasattr(ctx, 'message') else None,
                    'is_slash_command': isinstance(ctx.interaction, discord.Interaction)
                })
                
            extra.update(kwargs)
            
            self.logger.error(
                f"Error occurred: {str(error)}",
                exc_info=error,
                extra=extra,
                stack_info=True
            )
        except Exception as e:
            self.logger.error(f"Error in log_error: {str(e)}")

    def log_guild_event(self, guild: discord.Guild, event_type: str, **kwargs):
        """Log guild-related events with comprehensive metadata."""
        try:
            extra = {
                'shard_id': guild.shard_id,
                'guild_id': guild.id,
                'guild_name': guild.name,
                'guild_owner': str(guild.owner) if guild.owner else None,
                'guild_owner_id': guild.owner_id,
                'member_count': guild.member_count,
                'channel_count': len(guild.channels),
                'role_count': len(guild.roles),
                'event_type': event_type,
                'features': guild.features,
                'bot_permissions': str(guild.me.guild_permissions),
                'timestamp': datetime.utcnow().isoformat(),
                'premium_tier': guild.premium_tier,
                'premium_subscription_count': guild.premium_subscription_count
            }
            extra.update(kwargs)
            
            self.logger.info(
                f"Guild event {event_type} for {guild.name} (ID: {guild.id})",
                extra=extra
            )
        except Exception as e:
            self.logger.error(f"Error in log_guild_event: {str(e)}")

    def log_audit(self, guild: discord.Guild, action: str, target: Any, moderator: discord.Member, reason: str = None, **kwargs):
        """Log moderation actions for audit purposes."""
        try:
            extra = {
                'shard_id': guild.shard_id,
                'guild_id': guild.id,
                'guild_name': guild.name,
                'action': action,
                'target_id': getattr(target, 'id', str(target)),
                'target_name': str(target),
                'moderator_id': moderator.id,
                'moderator_name': str(moderator),
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
            extra.update(kwargs)
            
            self.logger.info(
                f"Audit: {action} performed by {moderator} on {target} in {guild.name}",
                extra=extra
            )
        except Exception as e:
            self.logger.error(f"Error in log_audit: {str(e)}")

logger = Logger()

def get_logger():
    """Get the global logger instance."""
    return logger.get_logger()

# Enhanced convenience functions
def log_command(ctx: discord.ext.commands.Context, command_name: str, **kwargs):
    """Log command usage with enhanced context."""
    logger.log_command(ctx, command_name, **kwargs)

def log_error(error: Exception, ctx: discord.ext.commands.Context = None, **kwargs):
    """Log errors with comprehensive context."""
    logger.log_error(error, ctx, **kwargs)

def log_guild_event(guild: discord.Guild, event_type: str, **kwargs):
    """Log guild-related events with comprehensive metadata."""
    logger.log_guild_event(guild, event_type, **kwargs)

def log_audit(guild: discord.Guild, action: str, target: Any, moderator: discord.Member, reason: str = None, **kwargs):
    """Log moderation actions for audit purposes."""
    logger.log_audit(guild, action, target, moderator, reason, **kwargs)