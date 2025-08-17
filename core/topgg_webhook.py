from aiohttp import web
import discord
from core.logger import get_logger
from core.config import Config

logger = get_logger()

class TopGGWebhook:
    """Handles Top.gg webhook requests for vote notifications"""
    def __init__(self, bot, auth_token: str):
        self.bot = bot
        self.auth_token = auth_token
        self.app = web.Application()
        self.app.router.add_post("/dblwebhook", self.handle_webhook)
        self.webhook_task = None
        self.logger = logger

    async def handle_webhook(self, request):
        """Handle incoming webhook requests from Top.gg"""
        try:
            # Verify authorization
            auth = request.headers.get('Authorization')
            if not auth or auth != self.auth_token:
                self.logger.warning(
                    "Unauthorized Top.gg webhook request",
                    extra={'ip': request.remote}
                )
                return web.Response(status=401)

            data = await request.json()
            
            # Log the webhook data
            self.logger.info(
                "Received Top.gg webhook",
                extra={
                    'user_id': data.get('user'),
                    'is_weekend': data.get('isWeekend', False),
                    'type': data.get('type')
                }
            )

            # Process the vote
            if data.get('type') == 'upvote':
                user_id = int(data['user'])
                is_weekend = data.get('isWeekend', False)
                
                # Get the TopGG cog and process the vote
                if topgg_cog := self.bot.get_cog('TopGG'):
                    await topgg_cog.process_vote(user_id, is_weekend)
                
                return web.Response(status=200)
            
            return web.Response(status=400)

        except Exception as e:
            self.logger.error(f"Error handling Top.gg webhook: {str(e)}")
            return web.Response(status=500)

    async def start(self):
        """Start the webhook server"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            # Get port from config or use default
            port = getattr(Config, 'TOPGG_WEBHOOK_PORT', 8080)
            
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            self.logger.info(
                f"Top.gg webhook server started on port {port}",
                extra={'port': port}
            )
            
        except Exception as e:
            self.logger.error(f"Error starting Top.gg webhook server: {str(e)}")

    async def stop(self):
        """Stop the webhook server"""
        try:
            await self.app.shutdown()
            self.logger.info("Top.gg webhook server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping Top.gg webhook server: {str(e)}")
