import os
import discord
from discord.ext import commands
from colorama import Fore, Style, Back
from dotenv import load_dotenv
import time
import platform


load_dotenv()

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())\




@client.event
async def on_ready():
    prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC", time.localtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
    print(prfx + "Logged as " + Fore.YELLOW + client.user.name)
    print(prfx + "BOT ID " + Fore.YELLOW + str(client.user.id))
    print(prfx + "Discord.py version " + Fore.YELLOW + str(discord.__version__))
    print(prfx + "Python version " + Fore.YELLOW + str(platform.python_version()))
    synced = await client.tree.sync()
    print(prfx + "Slash Command synced " + Fore.YELLOW + str(len(synced))+" Commands")


@client.tree.command(name="zapisy", description="Zapisy na mecz")
async def signup(interaction: discord.Interaction, title: str, date: str, time: str, vs: str, map: str, tactics_url:str):
    embed = discord.Embed(title=title, description="Zapisy na mecz", color=discord.Color.blue())
    embed.add_field(name="Date", value=date, inline=False)
    embed.add_field(name="Time", value=time, inline=False)
    embed.add_field(name="Versus", value=vs, inline=False)
    embed.add_field(name="Map", value=map, inline=False)
    embed.add_field(name="Taktyka", value=f"[Link]({tactics_url})",inline=False)
    await interaction.message.add_reaction("👍")
    await interaction.message.add_reaction("👎")
    await interaction.message.add_reaction("✋")

    await interaction.response.send(embed=embed, ephemeral=True)

client.run(os.getenv('DISCORD_API_TOKEN'))


