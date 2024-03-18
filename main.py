import os
import platform
import time
import logging
import discord
from colorama import Fore, Style, Back
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

Token = os.getenv('DISCORD_API_TOKEN')
GUILD_ID = int(os.getenv('GUILD'))
allowed_role_id_1 = int(os.environ.get("ALLOWED_ROLE_ID_1"))
allowed_role_id_2 = int(os.environ.get("ALLOWED_ROLE_ID_2"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


@client.event
async def on_ready():
    prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC ",
                                                    time.localtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
    logger.info(f"Logged in as {client.user.name} (ID: {client.user.id})")
    print(prfx + "Logged as " + Fore.YELLOW + client.user.name)
    print(prfx + "BOT ID " + Fore.YELLOW + str(client.user.id))
    print(prfx + "Discord.py version " + Fore.YELLOW + str(discord.__version__))
    print(prfx + "Python version " + Fore.YELLOW + str(platform.python_version()))
    synced = await client.tree.sync()
    print(prfx + "Slash Command synced " + Fore.YELLOW + str(len(synced)) + " Commands")


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout or None)
        self.voted_users = {}
        self.upvote_count = 0
        self.downvote_count = 0
        self.novote_count = 0
        logger.info("Buttons view initialized.")

    async def handle_vote(self, user_id, new_vote):
        previous_vote = self.voted_users.get(user_id)
        if previous_vote:
            if previous_vote == "downvote":
                self.downvote_count -= 1
            elif previous_vote == "upvote":
                self.upvote_count -= 1
            elif previous_vote == "novote":
                self.novote_count -= 1
        self.voted_users[user_id] = new_vote

    @discord.ui.button(label="Pierwsza Lista", style=discord.ButtonStyle.primary, emoji="👍")
    async def upvote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            logger.info(f"Upvote button pressed by {interaction.user} (ID: {interaction.user.id})")

            if interaction.user.id in self.voted_users and self.voted_users[interaction.user.id] == "upvote":
                await interaction.response.send_message("You have already upvoted.", ephemeral=True)
                return

            await self.handle_vote(interaction.user.id, "upvote")
            self.upvote_count += 1

            await interaction.response.send_message("You have singup for Pierwsza Lista!", ephemeral=True)

            await self.update_embed(interaction)

        except Exception as e:
            logger.error(f"Error in upvote_button for user {interaction.user} (ID: {interaction.user.id}): {e}")
            await interaction.response.send_message("An error occurred while processing your vote.", ephemeral=True)

    @discord.ui.button(label="Trzecia Lista", style=discord.ButtonStyle.secondary, emoji="👎")
    async def downvote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info(f"Downvote button pressed by {interaction.user}")
        await self.handle_vote(interaction.user.id, "downvote")
        self.downvote_count += 1
        await interaction.response.send_message("You have singup for Trzecia Lista!", ephemeral=True)
        await self.update_embed(interaction)

    @discord.ui.button(label="Nie Będzie mnie", style=discord.ButtonStyle.blurple, emoji="❌")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info(f"No button pressed by {interaction.user}")
        await self.handle_vote(interaction.user.id, "novote")
        self.novote_count += 1
        await interaction.response.send_message("You have singup for Nie będzie mnie", ephemeral=True)
        await self.update_embed(interaction)

    @discord.ui.button(label="Delete Post", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info(f"Delete button pressed by {interaction.user}")
        try:
            if not interaction.message.embeds or not interaction.message.embeds[0].author:
                raise ValueError("Invalid message embeds")

            embed_author_id = interaction.message.embeds[0].author.icon_url.split("/")[-2]
            if str(interaction.user.id) == embed_author_id:
                await interaction.message.delete()
                await interaction.response.send_message("Post deleted!", ephemeral=True)
            else:
                await interaction.response.send_message("You are not authorized to delete this post.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in delete_button: {e}")
            await interaction.response.send_message("An error occurred.", ephemeral=True)

    async def update_embed(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]

        async def get_member_name(guild, user_id):
            try:
                member = await guild.fetch_member(user_id)
                return member.display_name if member else "Unknown Member"
            except discord.NotFound:
                return "Unknown Member"  # Member not found
            except discord.HTTPException:
                return "Member Fetch Error"  # API error

        upvote_names = ", ".join([await get_member_name(interaction.guild, user_id)
                                  for user_id in self.voted_users if self.voted_users[user_id] == 'upvote']) or 'None'
        downvote_names = ", ".join([await get_member_name(interaction.guild, user_id)
                                    for user_id in self.voted_users if
                                    self.voted_users[user_id] == 'downvote']) or 'None'
        novote_names = ", ".join([await get_member_name(interaction.guild, user_id)
                                  for user_id in self.voted_users if self.voted_users[user_id] == 'novote']) or 'None'

        embed.set_field_at(0, name="Pierwsza Lista", value=f"Votes: {self.upvote_count}\nVoted by: {upvote_names}",
                           inline=False)
        embed.set_field_at(1, name="Trzecia Lista", value=f"Votes: {self.downvote_count}\nVoted by: {downvote_names}",
                           inline=False)
        embed.set_field_at(2, name="Nie będzie mnie", value=f"Votes: {self.novote_count}\nVoted by: {novote_names}",
                           inline=False)

        await interaction.message.edit(embed=embed)


@client.tree.command(name="zapisy", description="Zapisy na mecz")
async def signup(interaction: discord.Interaction, title: str, start: str, map: str, odciecie: str, zbiorka: str,):
    logger.info(f"Signup command called by {interaction.user} (ID: {interaction.user.id}) with title '{title}'")

    try:
        if allowed_role_id_1 and allowed_role_id_2 not in [role.id for role in interaction.user.roles]:
            logger.warning(
                f"User {interaction.user} (ID: {interaction.user.id}) don t have permission to do it.")
            await interaction.response.send_message("You don't have the required role to use this command.",
                                                    ephemeral=True)
            return

        embed = discord.Embed(title=title, description="Zapisy na mecz", color=discord.Color.blue())
        embed.add_field(name="zbiórka", value=zbiorka, inline=False)
        embed.add_field(name="Odcięcie", value=odciecie, inline=False)
        embed.add_field(name="Start", value=start, inline=False)
        embed.add_field(name="Mapa", value=map, inline=False)

        footer_text = f"Zbiórka: {zbiorka} | Odcięcie: {odciecie} | Start: {start} | Mapa: {map}"
        embed.set_footer(text=footer_text)

        await interaction.response.send_message(embed=embed, view=Buttons())
        logger.info(f"Signup command executed successfully for user {interaction.user} (ID: {interaction.user.id})")

    except Exception as e:
        logger.error(f"Error in signup command for user {interaction.user} (ID: {interaction.user.id}): {e}")
        await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)


client.run(Token)
