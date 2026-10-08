"""Discord bot for The Daily Waddle.

- `!waddle`          -> today's Penguin of the Day
- `!waddle random`   -> random penguin fact
- Also posts the daily penguin automatically at DAILY_POST_HOUR_UTC:MINUTE.

Run (API must be up):  python -m bot.discord_bot
Requires the "Message Content Intent" enabled in the Discord Developer Portal.
"""
import datetime as dt
import logging
import os

import discord
import httpx
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("waddle")
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("DISCORD_TOKEN", "")
API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", "0"))
POST_TIME = dt.time(
    hour=int(os.environ.get("DAILY_POST_HOUR_UTC", "14")),
    minute=int(os.environ.get("DAILY_POST_MINUTE_UTC", "0")),
    tzinfo=dt.timezone.utc,
)

# Colour-code the embed by IUCN conservation status
STATUS_COLOURS = {
    "Least Concern": 0x2ECC71,
    "Near Threatened": 0xF1C40F,
    "Vulnerable": 0xE67E22,
    "Endangered": 0xE74C3C,
    "Critically Endangered": 0x992D22,
}


class WaddleBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True  # needed for "!" prefix commands
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.http_client: httpx.AsyncClient | None = None

    async def setup_hook(self) -> None:
        self.http_client = httpx.AsyncClient(base_url=f"{API_BASE}/api/v1", timeout=10.0)
        if CHANNEL_ID:
            daily_broadcast.start()

    async def close(self) -> None:
        if self.http_client:
            await self.http_client.aclose()
        await super().close()

    async def fetch(self, path: str) -> dict:
        resp = await self.http_client.get(path)
        resp.raise_for_status()
        return resp.json()


bot = WaddleBot()


def build_embed(payload: dict, title_prefix: str) -> discord.Embed:
    """Both /daily and /random return {"penguin": {...}, "fact": {...}}."""
    penguin, fact = payload["penguin"], payload.get("fact")
    embed = discord.Embed(
        title=f"{title_prefix} {penguin['common_name']}",
        description=fact["text"] if fact else "No fact today, but still adorable.",
        colour=STATUS_COLOURS.get(penguin["conservation_status"], 0x3498DB),
    )
    embed.set_image(url=penguin["image_url"])
    embed.add_field(name="Scientific name", value=f"*{penguin['scientific_name']}*", inline=True)
    embed.add_field(name="Status", value=penguin["conservation_status"], inline=True)
    # /daily includes full details; /random only has the summary
    if "habitat" in penguin:
        embed.add_field(name="Habitat", value=penguin["habitat"], inline=False)
        embed.add_field(name="Diet", value=penguin["diet"], inline=False)
    embed.set_footer(text="The Daily Waddle 🐧")
    return embed


@bot.command(name="waddle")
@commands.cooldown(1, 10, commands.BucketType.channel)  # basic spam protection
async def waddle(ctx: commands.Context, mode: str = "daily") -> None:
    mode = mode.lower()
    if mode not in {"daily", "random"}:
        await ctx.send("Usage: `!waddle` or `!waddle random`")
        return
    async with ctx.typing():
        data = await bot.fetch(f"/penguins/{mode}")
    prefix = "🐧 Penguin of the Day:" if mode == "daily" else "🎲 Random penguin:"
    await ctx.send(embed=build_embed(data, prefix))


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Slow down, penguin! Try again in {error.retry_after:.0f}s.")
    elif isinstance(error, commands.CommandInvokeError) and isinstance(
        error.original, httpx.HTTPError
    ):
        log.warning("API request failed: %s", error.original)
        await ctx.send("The penguin API is napping. Try again shortly.")
    elif not isinstance(error, commands.CommandNotFound):
        log.exception("Unhandled command error", exc_info=error)


@tasks.loop(time=POST_TIME)
async def daily_broadcast() -> None:
    try:
        data = await bot.fetch("/penguins/daily")
        channel = bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)
        await channel.send(embed=build_embed(data, "🐧 Penguin of the Day:"))
    except (httpx.HTTPError, discord.DiscordException):
        log.exception("Daily broadcast failed")


@daily_broadcast.before_loop
async def _wait_ready() -> None:
    await bot.wait_until_ready()


@bot.event
async def on_ready() -> None:
    log.info("Logged in as %s", bot.user)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    bot.run(TOKEN)
