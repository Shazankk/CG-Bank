import discord
from discord.ext import commands
from discord.ui import Select, View
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

# Load roles from a JSON file
def load_roles():
    if os.path.exists('data/roles.json'):
        with open('data/roles.json', 'r') as file:
            return json.load(file)
    return {"permissions": {}, "mod_roles": []}

# Save roles to a JSON file
def save_roles(roles):
    with open('data/roles.json', 'w') as file:
        json.dump(roles, file, indent=4)

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

# Load roles and inventories into memory
role_data = load_roles()
user_inventories = load_inventories()

# Path to the logo image
logo_path = os.path.join(os.getcwd(), 'assets', 'cgcg.png')

# Function to get the logo URL
def get_logo_url():
    return "attachment://cgcg.png"

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

# Check if a user has the necessary permissions
def has_permission(ctx, command_name):
    user_permissions = role_data["permissions"].get(str(ctx.author.id), [])
    if command_name in ["additem", "removeitem"]:
        return (
            command_name in user_permissions or
            any(role.id in role_data["mod_roles"] for role in ctx.author.roles) or
            any(role.name == "🏆 CG Dev" for role in ctx.author.roles) or
            ctx.author.guild_permissions.administrator
        )
    return True

# Get the role mentions
def get_role_mentions(ctx):
    mod_roles = [f"<@&{role_id}>" for role_id in role_data["mod_roles"]]
    return ", ".join(mod_roles) if mod_roles else "@MODERATOR"

# Command to list all commands with descriptions and examples
@bot.command(name="showhelp", description="List all commands with descriptions and examples.")
async def showhelp(ctx):
    embed = discord.Embed(title="CG Bank Commands", description="Here are all the available commands:", color=0x00ff00)

    # Group commands into categories
    categories = {
        "Inventory Commands": ["inv", "additem", "removeitem", "trade"],
        "Admin Commands": ["assignmodrole", "removemodrole", "giverole", "droprole"],
        "Other Commands": ["viewlogs", "showrole"]
    }

    colors = {
        "Inventory Commands": discord.Color.blue(),
        "Admin Commands": discord.Color.red(),
        "Other Commands": discord.Color.green()
    }

    # Format commands for each category
    for category, commands_list in categories.items():
        commands_description = ""
        for command_name in commands_list:
            command = bot.get_command(command_name)
            if command:
                description = command.description if command.description else "No description available"
                example = f"Example: `!{command.name} `"
                if command.name == "inv":
                    example += "@username or !inv"
                elif command.name == "additem":
                    example += "@username item_name"
                elif command.name == "removeitem":
                    example += "@username item_name"
                elif command.name == "trade":
                    example += "item_name @from_user @to_user"
                elif command.name == "viewlogs":
                    example += "@username"
                elif command.name == "assignmodrole":
                    example += "@role"
                elif command.name == "removemodrole":
                    example += "@role"
                elif command.name == "giverole":
                    example += "@username @command"
                elif command.name == "droprole":
                    example += "@username @command"
                elif command.name == "showrole":
                    example += ""
                commands_description += f"**!{command.name}**\n{description}\n{example}\n\n"
        embed.add_field(name=f"**{category}**", value=commands_description, inline=True)
        embed.color = colors[category]

    embed.set_thumbnail(url=get_logo_url())
    embed.set_author(name="CG Bank", icon_url=get_logo_url())

    view = View()
    select = Select(placeholder="Select a command to see example", min_values=1, max_values=1)
    
    for category, commands_list in categories.items():
        for command_name in commands_list:
            command = bot.get_command(command_name)
            if command:
                label = f"!{command.name}"
                description = command.description if command.description else "No description available"
                example = f"!{command.name} "
                if command.name == "inv":
                    example += "@username or !inv"
                elif command.name == "additem":
                    example += "@username item_name"
                elif command.name == "removeitem":
                    example += "@username item_name"
                elif command.name == "trade":
                    example += "item_name @from_user @to_user"
                elif command.name == "viewlogs":
                    example += "@username"
                elif command.name == "assignmodrole":
                    example += "@role"
                elif command.name == "removemodrole":
                    example += "@role"
                elif command.name == "giverole":
                    example += "@username @command"
                elif command.name == "droprole":
                    example += "@username @command"
                elif command.name == "showrole":
                    example += ""
                select.add_option(label=label, description=description, value=example)
    
    async def select_callback(interaction):
        selected_value = select.values[0]
        await interaction.response.send_message(f"`{selected_value}`", ephemeral=False)
    
    select.callback = select_callback
    view.add_item(select)

    await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed, view=view)

# Command to give a user permission for a specific command
@bot.command(name="giverole", description="Give a user permission for a specific command.")
@commands.has_permissions(administrator=True)
async def giverole(ctx, user: discord.User, command_name: str):
    if command_name not in ["additem", "removeitem"]:
        await ctx.reply(f"Invalid command name: {command_name}")
        return

    if str(user.id) not in role_data["permissions"]:
        role_data["permissions"][str(user.id)] = []
    
    role_data["permissions"][str(user.id)].append(command_name)
    save_roles(role_data)
    await ctx.reply(f"User {user.mention} has been given permission to use `{command_name}`.")

# Command to remove a user's permission for a specific command
@bot.command(name="droprole", description="Remove a user's permission for a specific command.")
@commands.has_permissions(administrator=True)
async def droprole(ctx, user: discord.User, command_name: str):
    if command_name not in ["additem", "removeitem"]:
        await ctx.reply(f"Invalid command name: {command_name}")
        return

    if str(user.id) in role_data["permissions"] and command_name in role_data["permissions"][str(user.id)]:
        role_data["permissions"][str(user.id)].remove(command_name)
        save_roles(role_data)
        await ctx.reply(f"User {user.mention}'s permission to use `{command_name}` has been removed.")
    else:
        await ctx.reply(f"User {user.mention} does not have permission for `{command_name}`.")

# Command to assign a mod role
@bot.command(name="assignmodrole", description="Assign a custom mod role.")
@commands.has_permissions(administrator=True)
async def assignmodrole(ctx, role: discord.Role):
    if role.id not in role_data["mod_roles"]:
        role_data["mod_roles"].append(role.id)
        save_roles(role_data)
        await ctx.reply(f"Role {role.name} has been assigned as a mod role.")
    else:
        await ctx.reply(f"Role {role.name} is already a mod role.")

# Command to remove a mod role
@bot.command(name="removemodrole", description="Remove a custom mod role.")
@commands.has_permissions(administrator=True)
async def removemodrole(ctx, role: discord.Role):
    if role.id in role_data["mod_roles"]:
        role_data["mod_roles"].remove(role.id)
        save_roles(role_data)
        await ctx.reply(f"Role {role.name} has been removed from mod roles.")
    else:
        await ctx.reply(f"Role {role.name} is not a mod role.")

# Command to show inventory
@bot.command(name="inv", description="Peek into someone's inventory, or your own if you're feeling nosy!")
async def inv(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author  # Default to the command invoker if no user is specified
    user_id = str(user.id)
    inventory = user_inventories.get(user_id, [])
    description = "\n".join([f"{i+1}. {item}" for i, item in enumerate(inventory)]) if inventory else 'No items found.'
    embed = discord.Embed(
        title=f"{user.display_name}'s Inventory",
        description=description,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=get_logo_url())
    await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)

# Command to add an item to the inventory (only for authorized users)
@bot.command(name="additem", description="Add a shiny new item to someone's inventory.")
async def add_item(ctx, user: discord.User, *, item: str):
    if has_permission(ctx, "additem"):
        user_id = str(user.id)
        if user_id not in user_inventories:
            user_inventories[user_id] = []
        user_inventories[user_id].append(item)
        save_inventories()
        logger = get_user_logger(user_id)
        logger.info(f'Added {item} to {user.display_name}\'s inventory by {ctx.author.display_name}.')
        embed = discord.Embed(
            title="Item Added",
            description=f'{ctx.author.display_name} added {item} to {user.display_name}\'s inventory. Shiny!',
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)
    else:
        role_mentions = get_role_mentions(ctx)
        embed = discord.Embed(
            title="Permission Denied",
            description=f"Oops! You don't have the power to add items. Better talk to a mod! {role_mentions}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)

# Command to remove an item from the inventory (only for authorized users)
@bot.command(name="removeitem", description="Remove an item from someone's inventory.")
async def remove_item(ctx, user: discord.User, *, item: str):
    if has_permission(ctx, "removeitem"):
        user_id = str(user.id)
        if user_id in user_inventories and item in user_inventories[user_id]:
            user_inventories[user_id].remove(item)
            save_inventories()
            logger = get_user_logger(user_id)
            logger.info(f'{ctx.author.display_name} removed {item} from {user.display_name}\'s inventory.')
            embed = discord.Embed(
                title="Item Removed",
                description=f'{ctx.author.display_name} removed {item} from {user.display_name}\'s inventory. Poof, it\'s gone!',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=get_logo_url())
            await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)
        else:
            embed = discord.Embed(
                title="Item Not Found",
                description=f'{item} not found in {user.display_name}\'s inventory. Oops!',
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url=get_logo_url())
            await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)
    else:
        role_mentions = get_role_mentions(ctx)
        embed = discord.Embed(
            title="Permission Denied",
            description=f"Nope! You can't remove items. Ask a mod for help! {role_mentions}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)

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
        from_logger.info(f'{ctx.author.display_name} traded {item} to {to_user.name}.')
        to_logger.info(f'{ctx.author.display_name} received {item} from {from_user.name}.')
        embed = discord.Embed(
            title="Item Traded",
            description=f'{ctx.author.display_name} traded {item} from {from_user.display_name} to {to_user.display_name}. How generous!',
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)
    else:
        embed = discord.Embed(
            title="Trade Failed",
            description=f'{item} not found in {from_user.display_name}\'s inventory. No can do!',
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)

# Command to view logs of a specific user (accessible by all users)
@bot.command(name="viewlogs", description="Sneak a peek at someone's activity logs. Shhh, it's a secret!")
async def viewlogs(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author  # Default to the command invoker if no user is specified
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
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)
    else:
        embed = discord.Embed(
            title="No Logs Found",
            description=f'No logs found for {user.display_name}. Seems squeaky clean!',
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)

# Command to show mod roles and the users with those roles
@bot.command(name="showrole", description="Show all mod roles and the users with those roles.")
async def showrole(ctx):
    embed = discord.Embed(title="Mod Roles", description="Here are all the mod roles and the users with those roles:", color=0x00ff00)
    guild = ctx.guild
    mod_roles = list(set(role_data["mod_roles"]))  # Ensure no duplicates
    
    # Include CG Dev role explicitly if not already included
    cg_dev_role = discord.utils.get(guild.roles, name="🏆 CG Dev")
    if cg_dev_role and cg_dev_role.id not in mod_roles:
        mod_roles.append(cg_dev_role.id)
    
    if not mod_roles:
        embed.add_field(name="No Mod Roles", value="No mod roles have been assigned yet.", inline=False)
    else:
        for role_id in mod_roles:
            role = guild.get_role(role_id)
            if role:
                members = [member.mention for member in role.members]
                member_list = "\n".join(members) if members else "No members have this role."
                embed.add_field(name=role.name, value=member_list, inline=False)
            else:
                embed.add_field(name="Role Not Found", value=f"Role with ID {role_id} not found.", inline=False)
    embed.set_thumbnail(url=get_logo_url())
    await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)

# Error handler to show command usage when an error occurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
        command = ctx.command
        description = command.description if command.description else "No description available"
        example = f"Example: `!{command.name} `"
        if command.name == "inv":
            example += "@username or !inv"
        elif command.name == "additem":
            example += "@username item_name"
        elif command.name == "removeitem":
            example += "@username item_name"
        elif command.name == "trade":
            example += "item_name @from_user @to_user"
        elif command.name == "viewlogs":
            example += "@username"
        elif command.name == "giverole":
            example += "@username @command"
        elif command.name == "droprole":
            example += "@username @command"
        elif command.name == "assignmodrole":
            example += "@role"
        elif command.name == "removemodrole":
            example += "@role"
        elif command.name == "showrole":
            example += ""
        embed = discord.Embed(
            title=f"Usage: !{command.name}",
            description=f"{description}\n{example}",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description=f"You are missing the necessary permissions to run this command.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.reply(file=discord.File(logo_path, filename='cgcg.png'), embed=embed)
    else:
        await showhelp(ctx)

# Autocomplete functionality
@bot.event
async def on_message(message):
    if message.content.startswith('!'):
        context = await bot.get_context(message)
        if context.command is None:
            await showhelp(context)
    await bot.process_commands(message)

# Start the bot with your token
bot.run(os.getenv("bot_token"))