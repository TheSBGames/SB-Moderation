import pytest
from unittest.mock import AsyncMock, patch
from sb_moderation.core.bot import Bot
from sb_moderation.cogs.tickets.tickets import TicketCog

@pytest.fixture
def bot():
    bot_instance = Bot()
    bot_instance.add_cog(TicketCog(bot_instance))
    return bot_instance

@pytest.mark.asyncio
async def test_ticket_setup(bot):
    # Mock the necessary methods
    bot.send_message = AsyncMock()
    bot.wait_for = AsyncMock(return_value={"content": "Test Ticket"})
    
    # Simulate the ticket setup command
    await bot.get_command("ticket setup").callback(bot, "Test Channel")
    
    # Check if the ticket panel was created
    bot.send_message.assert_called_once_with("Test Channel", embed=Any)

@pytest.mark.asyncio
async def test_ticket_close(bot):
    # Mock the necessary methods
    bot.send_message = AsyncMock()
    bot.get_channel = AsyncMock(return_value=AsyncMock())
    
    # Simulate closing a ticket
    await bot.get_command("ticket close").callback(bot, "Test Ticket Channel")
    
    # Check if the ticket channel was deleted
    bot.get_channel().delete.assert_called_once()

@pytest.mark.asyncio
async def test_ticket_add_user(bot):
    # Mock the necessary methods
    bot.send_message = AsyncMock()
    bot.get_channel = AsyncMock(return_value=AsyncMock())
    
    # Simulate adding a user to a ticket
    await bot.get_command("ticket add").callback(bot, "Test Ticket Channel", "User")
    
    # Check if the user was added to the ticket channel
    bot.get_channel().set_permissions.assert_called_once_with("User", read_messages=True, send_messages=True)

@pytest.mark.asyncio
async def test_ticket_remove_user(bot):
    # Mock the necessary methods
    bot.send_message = AsyncMock()
    bot.get_channel = AsyncMock(return_value=AsyncMock())
    
    # Simulate removing a user from a ticket
    await bot.get_command("ticket remove").callback(bot, "Test Ticket Channel", "User")
    
    # Check if the user was removed from the ticket channel
    bot.get_channel().set_permissions.assert_called_once_with("User", read_messages=False, send_messages=False)