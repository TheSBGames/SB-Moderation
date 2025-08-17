import pytest
from unittest.mock import AsyncMock, MagicMock
from sb_moderation.core.bot import Bot
from sb_moderation.utils.embeds import powered_embed

@pytest.fixture
def bot():
    bot_instance = Bot(command_prefix='&')
    bot_instance.db = AsyncMock()
    return bot_instance

@pytest.fixture
def noprefix_user(bot):
    return {
        "_id": 777888999000111222,
        "added_by": 1186506712040099850,
        "added_at": "2025-08-17T12:00:00Z",
        "expires_at": None
    }

@pytest.mark.asyncio
async def test_no_prefix_command_execution(bot, noprefix_user):
    bot.db.noprefix_users.find_one = AsyncMock(return_value=noprefix_user)
    bot.get_context = AsyncMock(return_value=MagicMock(valid=True))
    bot.invoke = AsyncMock()

    message = MagicMock(content='ping', author=MagicMock(id=noprefix_user["_id"]))
    await bot.on_message(message)

    bot.invoke.assert_called_once()

@pytest.mark.asyncio
async def test_no_prefix_command_not_triggered(bot):
    bot.db.noprefix_users.find_one = AsyncMock(return_value=None)
    bot.get_context = AsyncMock(return_value=MagicMock(valid=False))

    message = MagicMock(content='ping', author=MagicMock(id=123456789))
    await bot.on_message(message)

    bot.invoke.assert_not_called()

@pytest.mark.asyncio
async def test_no_prefix_command_with_invalid_length(bot, noprefix_user):
    bot.db.noprefix_users.find_one = AsyncMock(return_value=noprefix_user)
    bot.get_context = AsyncMock(return_value=MagicMock(valid=True))
    bot.invoke = AsyncMock()

    message = MagicMock(content='p', author=MagicMock(id=noprefix_user["_id"]))
    await bot.on_message(message)

    bot.invoke.assert_not_called()