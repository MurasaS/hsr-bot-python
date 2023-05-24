import settings
import discord
from discord.ext import commands

logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.default()

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        logger.info(f"Guild ID: {bot.guilds[0].id}")
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)\

    @bot.tree.command(name="zapisy", description="Zapisy na mecz")
    async def singup(ctx: commands.Context, title: str, date: str, time: str, vs: str, map: str):
        embed = discord.Embed(
            title=title,
            date=date,
            time=time,
            vs=vs,
            map=map,
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        await ctx.send("Zapisy na mecz zostały otwarte")

    bot.run(settings.Discord_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()
