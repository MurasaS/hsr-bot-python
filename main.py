import os
import discord
import interactions
from discord.ui import Button, View
from discord.ext import commands
from colorama import Fore, Style, Back
from dotenv import load_dotenv
import time
import platform

load_dotenv()

Token = os.getenv('DISCORD_API_TOKEN')
GUILD_ID = int(os.getenv('GUILD'))
allowed_role_id = int(os.environ.get("ALLOWED_ROLE_ID"))

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout or 180)

        self.voted_users = {}
        self.upvote_count = 0
        self.downvote_count = 0
        self.novote_count = 0

    @discord.ui.button(label="Pierwsza Lista", style=discord.ButtonStyle.primary, emoji="👍")
    async def upvote_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id in self.voted_users:
            previous_vote = self.voted_users[interaction.user.id]
            if previous_vote == "downvote":
                self.downvote_count -= 1
            elif previous_vote == "upvote":
                self.upvote_count -= 1
            elif previous_vote == "novote":
                self.novote_count -= 1
            del self.voted_users[interaction.user.id]

        if (
            interaction.user.id not in self.voted_users
            or self.voted_users[interaction.user.id] == "downvote"
            or self.voted_users[interaction.user.id] == "novote"
        ):
            self.upvote_count += 1
            self.voted_users[interaction.user.id] = "upvote"
            await interaction.response.send_message("Upvoted!", ephemeral=True)

        await self.update_embed(interaction)

    @discord.ui.button(label="Trzecia Lista", style=discord.ButtonStyle.secondary, emoji="👎")
    async def downvote_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id in self.voted_users:
            previous_vote = self.voted_users[interaction.user.id]
            if previous_vote == "downvote":
                self.downvote_count -= 1
            elif previous_vote == "upvote":
                self.upvote_count -= 1
            elif previous_vote == "novote":
                self.novote_count -= 1
            del self.voted_users[interaction.user.id]

        if (
            interaction.user.id not in self.voted_users
            or self.voted_users[interaction.user.id] == "upvote"
            or self.voted_users[interaction.user.id] == "novote"
        ):
            self.downvote_count += 1
            self.voted_users[interaction.user.id] = "downvote"
            await interaction.response.send_message("Downvoted!", ephemeral=True)

        await self.update_embed(interaction)

    @discord.ui.button(label="Nie Będzie mnie", style=discord.ButtonStyle.blurple, emoji="❌")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted_users:
            previous_vote = self.voted_users[interaction.user.id]
            if previous_vote == "downvote":
                self.downvote_count -= 1
            elif previous_vote == "upvote":
                self.upvote_count -= 1
            elif previous_vote == "novote":
                self.novote_count -= 1
            del self.voted_users[interaction.user.id]

        if (
            interaction.user.id not in self.voted_users
            or self.voted_users[interaction.user.id] == "upvote"
            or self.voted_users[interaction.user.id] == "downvote"
        ):
            self.novote_count += 1
            self.voted_users[interaction.user.id] = "novote"
            await interaction.response.send_message("No vote recorded!", ephemeral=True)

        await self.update_embed(interaction)

    @discord.ui.button(label="Delete Post", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.message.embeds or not interaction.message.embeds[0].author:
            await interaction.response.send_message("Unable to delete the post.", ephemeral=True)
            return

        embed_author_id = interaction.message.embeds[0].author.icon_url.split("/")[-2]
        if str(interaction.user.id) == embed_author_id:
            await interaction.message.delete()
            await interaction.response.send_message("Post deleted!", ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to delete this post.", ephemeral=True)

    async def update_embed(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        upvote_value = f"Votes: {self.upvote_count}\nVoted by: {', '.join([str(interaction.guild.get_member(user_id)) for user_id, vote in self.voted_users.items() if vote == 'upvote'])}"
        downvote_value = f"Votes: {self.downvote_count}\nVoted by: {', '.join([str(interaction.guild.get_member(user_id)) for user_id, vote in self.voted_users.items() if vote == 'downvote'])}"
        novote_value = f"Votes: {self.novote_count}\nVoted by: {', '.join([str(interaction.guild.get_member(user_id)) for user_id, vote in self.voted_users.items() if vote == 'novote'])}"
        embed.set_field_at(0, name="Pierwsza Lista", value=upvote_value, inline=False)
        embed.set_field_at(1, name="Trzecia Lista", value=downvote_value, inline=False)
        embed.set_field_at(2, name="Nie będzie mnie", value=novote_value, inline=False)
        await interaction.message.edit(embed=embed)


@client.event
async def on_ready():
    prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC ",
                                                    time.localtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
    print(prfx + "Logged as " + Fore.YELLOW + client.user.name)
    print(prfx + "BOT ID " + Fore.YELLOW + str(client.user.id))
    print(prfx + "Discord.py version " + Fore.YELLOW + str(discord.__version__))
    print(prfx + "Python version " + Fore.YELLOW + str(platform.python_version()))
    synced = await client.tree.sync()
    print(prfx + "Slash Command synced " + Fore.YELLOW + str(len(synced)) + " Commands")


@client.tree.command(name="zapisy", description="Zapisy na mecz")
async def signup(interaction: discord.Interaction, title: str, start: str, map: str, odcięcie:str, zbiórka:str,
                 tactics_url: str):
    if allowed_role_id not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("You don't have the required role to use this command.", ephemeral=True)
        return
    embed = discord.Embed(title=title, description="Zapisy na mecz", color=discord.Color.blue())
    embed.add_field(name="zbiórka", value=zbiórka, inline=False)
    embed.add_field(name="Odcięcie", value=odcięcie, inline=False)
    embed.add_field(name="Start", value=start, inline=False)
    embed.add_field(name="Mapa", value=map, inline=False)

    await interaction.response.send_message(embed=embed, view=Buttons())


client.run(Token)
