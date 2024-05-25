import discord
from discord.ext import commands
import logging
import os
import json
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# Ensure necessary directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Function to get logger for a specific user
def get_user_logger(user_id):
    logger = logging.getLogger(user_id)
    if not logger.hasHandlers():
        handler = logging.FileHandler(f'logs/{user_id}.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# Load inventories from a JSON file
def load_inventories():
    if os.path.exists('data/inventories.json'):
        with open('data/inventories.json', 'r') as file:
            return json.load(file)
    return {}

# Save inventories to a JSON file
def save_inventories():
    with open('data/inventories.json', 'w') as file:
        json.dump(user_inventories, file, indent=4)

# Define the intents for the bot
intents = discord.Intents.all()
intents.message_content = True  # Enable message content intent

# Create a bot instance with the specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Load inventories into memory
user_inventories = load_inventories()

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

# Check if a user is a server moderator or owner
def is_moderator(ctx):
    return ctx.author.guild_permissions.manage_guild or ctx.author.guild_permissions.administrator

# Get the moderator role mention
def get_moderator_role(ctx):
    for role in ctx.guild.roles:
        if role.name == "🚦 | MODERATOR":
            return role.mention
    return "@MODERATOR"

# Command to list all commands with descriptions
@bot.command(name="showhelp", description="List all commands with descriptions.")
async def showhelp(ctx):
    embed = discord.Embed(title="Command List", description="Here are all the available commands:", color=0x00ff00)
    for command in bot.commands:
        embed.add_field(name=f"!{command}", value=command.description, inline=False)
    await ctx.reply(embed=embed)

# Command to show inventory
@bot.command(name="inv", description="Peek into someone's inventory, or your own if you're feeling nosy!")
async def inv(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author  # Default to the command invoker if no user is specified
    user_id = str(user.id)
    inventory = user_inventories.get(user_id, [])
    embed = discord.Embed(
        title=f"{user.display_name}'s Inventory",
        description=', '.join(inventory) if inventory else 'No items found.',
        color=discord.Color.blue()
    )
    await ctx.reply(embed=embed)

# Command to add an item to the inventory (only for moderators and server owner)
@bot.command(name="additem", description="Add a shiny new item to someone's inventory.")
async def add_item(ctx, user: discord.User, *, item: str):
    if is_moderator(ctx):
        try:
            user_id = str(user.id)
            if user_id not in user_inventories:
                user_inventories[user_id] = []
            user_inventories[user_id].append(item)
            save_inventories()
            logger = get_user_logger(user_id)
            logger.info(f'Added {item} to inventory.')
            embed = discord.Embed(
                title="Item Added",
                description=f'Added {item} to {user.display_name}\'s inventory. Shiny!',
                color=discord.Color.green()
            )
            await ctx.reply(embed=embed)
        except discord.ext.commands.errors.UserNotFound:
            embed = discord.Embed(
                title="User Not Found",
                description=f"Could not find the user '{user}'. Please check the username and try again.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
    else:
        moderator_role = get_moderator_role(ctx)
        embed = discord.Embed(
            title="Permission Denied",
            description=f"Oops! You don't have the power to add items. Better talk to a mod! {moderator_role}",
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)

# Command to remove an item from the inventory (only for moderators and server owner)
@bot.command(name="removeitem", description="Remove an item from someone's inventory.")
async def remove_item(ctx, user: discord.User, *, item: str):
    if is_moderator(ctx):
        try:
            user_id = str(user.id)
            if user_id in user_inventories and item in user_inventories[user_id]:
                user_inventories[user_id].remove(item)
                save_inventories()
                logger = get_user_logger(user_id)
                logger.info(f'Removed {item} from inventory.')
                embed = discord.Embed(
                    title="Item Removed",
                    description=f'Removed {item} from {user.display_name}\'s inventory. Poof, it\'s gone!',
                    color=discord.Color.red()
                )
                await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title="Item Not Found",
                    description=f'{item} not found in {user.display_name}\'s inventory. Oops!',
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed)
        except discord.ext.commands.errors.UserNotFound:
            embed = discord.Embed(
                title="User Not Found",
                description=f"Could not find the user '{user}'. Please check the username and try again.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
    else:
        moderator_role = get_moderator_role(ctx)
        embed = discord.Embed(
            title="Permission Denied",
            description=f"Nope! You can't remove items. Ask a mod for help! {moderator_role}",
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)

# Command to trade an item between two users (available to all users)
@bot.command(name="trade", description="Trade an item from one user to another. Sharing is caring!")
async def trade(ctx, item: str, from_user: discord.User, to_user: discord.User):
    from_user_id = str(from_user.id)
    to_user_id = str(to_user.id)
    if from_user_id in user_inventories and item in user_inventories[from_user_id]:
        user_inventories[from_user_id].remove(item)
        if to_user_id not in user_inventories:
            user_inventories[to_user_id] = []
        user_inventories[to_user_id].append(item)
        save_inventories()
        from_logger = get_user_logger(from_user_id)
        to_logger = get_user_logger(to_user_id)
        from_logger.info(f'Traded {item} to {to_user.name}.')
        to_logger.info(f'Received {item} from {from_user.name}.')
        embed = discord.Embed(
            title="Item Traded",
            description=f'Traded {item} from {from_user.display_name} to {to_user.display_name}. How generous!',
            color=discord.Color.purple()
        )
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(
            title="Trade Failed",
            description=f'{item} not found in {from_user.display_name}\'s inventory. No can do!',
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)

# Command to view logs of a specific user
@bot.command(name="viewlogs", description="Sneak a peek at someone's activity logs. Shhh, it's a secret!")
@commands.has_permissions(manage_guild=True)
async def viewlogs(ctx, user: discord.User):
    user_id = str(user.id)
    log_file_path = f'logs/{user_id}.log'
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            logs = log_file.read()
        embed = discord.Embed(
            title=f"Logs for {user.display_name}",
            description=f"```\n{logs}\n```",
            color=discord.Color.gold()
        )
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(
            title="No Logs Found",
            description=f'No logs found for {user.display_name}. Seems squeaky clean!',
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)

# Start the bot with your token
bot.run(os.getenv("bot_token"))