import interactions
import logging
import os
import json

from dotenv import load_dotenv, dotenv_values
from config import user_inventories, role_data, get_user_logger, load_roles, save_roles, load_inventories, save_inventories

load_dotenv()

# Initialize bot
bot = interactions.Client(token= os.getenv("token"))

# Event handler for bot ready
@bot.event
async def on_ready():
    for guild in bot.guilds:
        try:
            await bot.sync_guild(guild.id)
            print(f"Synced commands for guild: {guild.name} ({guild.id})")
        except Exception as e:
            print(f"Failed to sync commands for guild: {guild.name} ({guild.id}). Error: {e}")
    print(f"Logged in as {bot.user}")

# Import commands after bot initialization
from commands.inventory import inv, add_item, remove_item, trade
from commands.admin import giverole, droprole
from commands.general import viewlogs, showrole, showhelp, viewbotlogs

# Register commands (decorators handle this part automatically)

# Run the bot
bot.start()