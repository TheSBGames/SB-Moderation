# cogs/automod.py

import discord
from discord.ext import commands
import re
import json
import os

CONFIG_FILE = "automod_config.json"

DEFAULT_CONFIG = {
    "enabled": True,
    "rules": {
        "anti_spam": True,
        "anti_link": True,
        "anti_profanity": True
    },
    "max_mentions": 5,
    "bad_words": ["badword1", "badword2"],
    "punishment": "warn",  # or "mute", "kick", "ban"
    "whitelist": []
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.config["enabled"] or message.author.bot:
            return

        if message.author.id in self.config["whitelist"]:
            return

        content = message.content.lower()

        # Anti-spam (mentions)
        if self.config["rules"]["anti_spam"]:
            if message.mention_everyone or len(message.mentions) >= self.config["max_mentions"]:
                await self.take_action(message, reason="Mention spam")

        # Anti-link
        if self.config["rules"]["anti_link"]:
            if re.search(r"(https?://|www\.)", content):
                await self.take_action(message, reason="Link detected")

        # Anti-profanity
        if self.config["rules"]["anti_profanity"]:
            if any(bad in content for bad in self.config["bad_words"]):
                await self.take_action(message, reason="Profanity detected")

    async def take_action(self, message, reason="Violation"):
        await message.delete()
        punishment = self.config["punishment"]
        user = message.author
        guild = message.guild
        log = f"[AutoMod] {reason} - {user} ({user.id})"

        if punishment == "warn":
            await message.channel.send(f"{user.mention} has been warned for: **{reason}**", delete_after=5)
        elif punishment == "kick":
            await guild.kick(user, reason=f"AutoMod: {reason}")
        elif punishment == "ban":
            await guild.ban(user, reason=f"AutoMod: {reason}")
        elif punishment == "mute":
            mute_role = discord.utils.get(guild.roles, name="Muted")
            if mute_role:
                await user.add_roles(mute_role, reason=f"AutoMod: {reason}")
        print(log)

    @commands.group(name="automod", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx):
        """View automod status."""
        status = "Enabled" if self.config["enabled"] else "Disabled"
        await ctx.send(f"🔧 AutoMod is currently **{status}**")

    @automod.command()
    async def enable(self, ctx):
        self.config["enabled"] = True
        save_config(self.config)
        await ctx.send("✅ AutoMod enabled.")

    @automod.command()
    async def disable(self, ctx):
        self.config["enabled"] = False
        save_config(self.config)
        await ctx.send("❌ AutoMod disabled.")

    @automod.command()
    async def set(self, ctx, key: str, value: str):
        """Set automod settings like max_mentions or punishment."""
        if key in self.config:
            if key == "max_mentions":
                self.config[key] = int(value)
            elif key == "punishment":
                self.config[key] = value.lower()
            save_config(self.config)
            await ctx.send(f"⚙️ `{key}` set to `{value}`.")
        else:
            await ctx.send("❌ Invalid key.")

    @automod.command()
    async def whitelist(self, ctx, user: discord.Member):
        """Exempt a user from automod checks."""
        self.config["whitelist"].append(user.id)
        save_config(self.config)
        await ctx.send(f"✅ {user.mention} whitelisted.")

    @automod.command()
    async def rules(self, ctx):
        """Show current automod rule toggles."""
        rules = "\n".join([f"🔹 {k}: {v}" for k, v in self.config["rules"].items()])
        await ctx.send(f"**Current AutoMod Rules:**\n{rules}")

    @automod.command()
    async def toggle(self, ctx, rule: str):
        """Toggle a specific automod rule."""
        if rule in self.config["rules"]:
            self.config["rules"][rule] = not self.config["rules"][rule]
            save_config(self.config)
            status = "enabled" if self.config["rules"][rule] else "disabled"
            await ctx.send(f"🔁 `{rule}` is now {status}.")
        else:
            await ctx.send("❌ Invalid rule name.")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
