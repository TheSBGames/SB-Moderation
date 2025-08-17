import pytest
from unittest.mock import AsyncMock, MagicMock
from core.bot import MyBot  # Adjust the import based on your actual bot class name
from cogs.automod.automod import AutomodCog

@pytest.fixture
def bot():
    bot_instance = MyBot()
    bot_instance.db = AsyncMock()
    return bot_instance

@pytest.fixture
def automod_cog(bot):
    cog = AutomodCog(bot)
    bot.add_cog(cog)
    return cog

@pytest.mark.asyncio
async def test_automod_edit_detection(automod_cog):
    # Mock the necessary components
    before_message = MagicMock()
    after_message = MagicMock()
    before_message.content = "This is a test message."
    after_message.content = "This is a test message with a link: http://example.com"
    after_message.guild.id = 123456789
    after_message.author.id = 987654321

    # Set up the automod settings for the guild
    automod_cog.bot.db.automod_settings.find_one = AsyncMock(return_value={
        "_id": 123456789,
        "enabled": True,
        "anti_links": True,
        "bypass_roles": [],
        "action": {"type": "timeout", "duration_minutes": 30},
        "log_channel": None
    })

    # Simulate the edit event
    await automod_cog.on_message_edit(before_message, after_message)

    # Check that the user was timed out
    assert after_message.author.timeout is not None
    assert after_message.author.timeout.duration == 30 * 60  # 30 minutes in seconds

@pytest.mark.asyncio
async def test_automod_edit_no_link(automod_cog):
    before_message = MagicMock()
    after_message = MagicMock()
    before_message.content = "This is a test message."
    after_message.content = "This is another test message."
    after_message.guild.id = 123456789
    after_message.author.id = 987654321

    # Set up the automod settings for the guild
    automod_cog.bot.db.automod_settings.find_one = AsyncMock(return_value={
        "_id": 123456789,
        "enabled": True,
        "anti_links": True,
        "bypass_roles": [],
        "action": {"type": "timeout", "duration_minutes": 30},
        "log_channel": None
    })

    # Simulate the edit event
    await automod_cog.on_message_edit(before_message, after_message)

    # Check that no action was taken
    assert after_message.author.timeout is None

@pytest.mark.asyncio
async def test_automod_edit_bypass_role(automod_cog):
    before_message = MagicMock()
    after_message = MagicMock()
    before_message.content = "This is a test message."
    after_message.content = "This is a test message with a link: http://example.com"
    after_message.guild.id = 123456789
    after_message.author.id = 987654321

    # Set up the automod settings for the guild with a bypass role
    automod_cog.bot.db.automod_settings.find_one = AsyncMock(return_value={
        "_id": 123456789,
        "enabled": True,
        "anti_links": True,
        "bypass_roles": [111111111],  # Assume this is the role ID of the bypass role
        "action": {"type": "timeout", "duration_minutes": 30},
        "log_channel": None
    })

    # Simulate the edit event
    await automod_cog.on_message_edit(before_message, after_message)

    # Check that no action was taken
    assert after_message.author.timeout is None