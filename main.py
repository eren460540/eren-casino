import discord
from discord import app_commands

TOKEN = "YOUR_BOT_TOKEN_HERE"

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync slash commands to Discord
        await self.tree.sync()

client = MyClient()

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.tree.command(
    name="hello",
    description="👋 Say hello and receive a friendly greeting from the bot"
)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Hello there! 👋 I'm happy to see you!"
    )

client.run(TOKEN)
