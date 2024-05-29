import interactions
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

# Initialize bot
bot = interactions.Client(token= os.getenv("bot_token"))

# Load roles and inventories into memory
role_data = load_roles()
user_inventories = load_inventories()

# Path to the logo image
logo_path = os.path.join(os.getcwd(), 'assets', 'cgcg.png')

# Function to get the logo URL
def get_logo_url():
    return "attachment://cgcg.png"

# Check if a user has the necessary permissions
def has_permission(ctx: interactions.SlashContext, command_name: str):
    user_permissions = role_data["permissions"].get(str(ctx.author.id), [])
    if command_name in ["additem", "removeitem"]:
        return (
            command_name in user_permissions or
            any(role.id in role_data["mod_roles"] for role in ctx.author.roles) or
            any(role.name == "🏆 CG Dev" for role in ctx.author.roles) or
            ctx.author.permissions.administrator
        )
    return True

# Get the role mentions
def get_role_mentions(guild):
    mod_roles = [f"<@&{role_id}>" for role_id in role_data["mod_roles"]]
    return ", ".join(mod_roles) if mod_roles else "@MODERATOR"

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

# Command to list all commands with descriptions and examples
@interactions.slash_command(
    name="showhelp",
    description="List all commands with descriptions and examples."
)
async def showhelp(ctx: interactions.SlashContext):
    embed = interactions.Embed(
        title="CG Bank Commands",
        description="Here are all the available commands:",
        color=0x00ff00
    )

    # Group commands into categories
    categories = {
        "Inventory Commands": {
            "inv": {
                "description": "Peek into someone's inventory, or your own if you're feeling nosy!",
                "example": "/inv @username or /inv"
            },
            "additem": {
                "description": "Add a shiny new item to someone's inventory.",
                "example": "/additem @username item_name"
            },
            "removeitem": {
                "description": "Remove an item from someone's inventory.",
                "example": "/removeitem @username item_name"
            },
            "trade": {
                "description": "Trade an item from one user to another. Sharing is caring!",
                "example": "/trade item_name @from_user @to_user"
            }
        },
        "Admin Commands": {
            "assignmodrole": {
                "description": "Assign a custom mod role.",
                "example": "/assignmodrole @role"
            },
            "removemodrole": {
                "description": "Remove a custom mod role.",
                "example": "/removemodrole @role"
            },
            "giverole": {
                "description": "Give a user permission for a specific command.",
                "example": "/giverole @username @command"
            },
            "droprole": {
                "description": "Remove a user's permission for a specific command.",
                "example": "/droprole @username @command"
            }
        },
        "Other Commands": {
            "viewlogs": {
                "description": "Sneak a peek at someone's activity logs. Shhh, it's a secret!",
                "example": "/viewlogs @username"
            },
            "showrole": {
                "description": "Show all mod roles and the users with those roles.",
                "example": "/showrole"
            }
        }
    }

    # Format commands for each category
    for category, commands_dict in categories.items():
        commands_description = ""
        for command_name, command_info in commands_dict.items():
            description = command_info["description"]
            example = command_info["example"]
            commands_description += f"**/{command_name}**\n{description}\n*Usage:* `{example}`\n\n"
        if commands_description.strip():  # Ensure the field is not empty
            embed.add_field(name=f"**{category}**", value=commands_description, inline=True)

    embed.set_thumbnail(url=get_logo_url())
    embed.set_author(name="CG Bank", icon_url=get_logo_url())

    await ctx.send(embeds=[embed], ephemeral=True)

# Command to give a user permission for a specific command
@interactions.slash_command(
    name="giverole",
    description="Give a user permission for a specific command.",
    options=[
        interactions.SlashCommandOption(
            name="user",
            description="User to give permission to",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.SlashCommandOption(
            name="command_name",
            description="Command to give permission for",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[
                interactions.SlashCommandChoice(name="additem", value="additem"),
                interactions.SlashCommandChoice(name="removeitem", value="removeitem")
            ]
        )
    ]
)
async def giverole(ctx: interactions.SlashContext, user: interactions.User, command_name: str):
    if not ctx.author.permissions.administrator:
        await ctx.send("You are missing the necessary permissions to run this command.", ephemeral=True)
        return

    if str(user.id) not in role_data["permissions"]:
        role_data["permissions"][str(user.id)] = []
    
    role_data["permissions"][str(user.id)].append(command_name)
    save_roles(role_data)
    await ctx.send(f"User {user.mention} has been given permission to use `{command_name}`.", ephemeral=True)

# Command to remove a user's permission for a specific command
@interactions.slash_command(
    name="droprole",
    description="Remove a user's permission for a specific command.",
    options=[
        interactions.SlashCommandOption(
            name="user",
            description="User to remove permission from",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.SlashCommandOption(
            name="command_name",
            description="Command to remove permission for",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[
                interactions.SlashCommandChoice(name="additem", value="additem"),
                interactions.SlashCommandChoice(name="removeitem", value="removeitem")
            ]
        )
    ]
)
async def droprole(ctx: interactions.SlashContext, user: interactions.User, command_name: str):
    if not ctx.author.permissions.administrator:
        await ctx.send("You are missing the necessary permissions to run this command.", ephemeral=True)
        return

    if str(user.id) in role_data["permissions"] and command_name in role_data["permissions"][str(user.id)]:
        role_data["permissions"][str(user.id)].remove(command_name)
        save_roles(role_data)
        await ctx.send(f"User {user.mention}'s permission to use `{command_name}` has been removed.", ephemeral=True)
    else:
        await ctx.send(f"User {user.mention} does not have permission for `{command_name}`.", ephemeral=True)

# Command to assign a mod role
@interactions.slash_command(
    name="assignmodrole",
    description="Assign a custom mod role.",
    options=[
        interactions.SlashCommandOption(
            name="role",
            description="Role to assign as mod",
            type=interactions.OptionType.ROLE,
            required=True
        )
    ]
)
async def assignmodrole(ctx: interactions.SlashContext, role: interactions.Role):
    if not ctx.author.permissions.administrator:
        await ctx.send("You are missing the necessary permissions to run this command.", ephemeral=True)
        return

    if role.id not in role_data["mod_roles"]:
        role_data["mod_roles"].append(role.id)
        save_roles(role_data)
        await ctx.send(f"Role {role.name} has been assigned as a mod role.", ephemeral=True)
    else:
        await ctx.send(f"Role {role.name} is already a mod role.", ephemeral=True)

# Command to remove a mod role
@interactions.slash_command(
    name="removemodrole",
    description="Remove a custom mod role.",
    options=[
        interactions.SlashCommandOption(
            name="role",
            description="Role to remove from mod",
            type=interactions.OptionType.ROLE,
            required=True
        )
    ]
)
async def removemodrole(ctx: interactions.SlashContext, role: interactions.Role):
    if not ctx.author.permissions.administrator:
        await ctx.send("You are missing the necessary permissions to run this command.", ephemeral=True)
        return

    if role.id in role_data["mod_roles"]:
        role_data["mod_roles"].remove(role.id)
        save_roles(role_data)
        await ctx.send(f"Role {role.name} has been removed from mod roles.", ephemeral=True)
    else:
        await ctx.send(f"Role {role.name} is not a mod role.", ephemeral=True)

# Command to show inventory
@interactions.slash_command(
    name="inv",
    description="Peek into someone's inventory, or your own if you're feeling nosy!",
    options=[
        interactions.SlashCommandOption(
            name="user",
            description="User to view inventory of",
            type=interactions.OptionType.USER,
            required=False
        )
    ]
)
async def inv(ctx: interactions.SlashContext, user: interactions.User = None):
    if user is None:
        user = ctx.author  # Default to the command invoker if no user is specified
    user_id = str(user.id)
    inventory = user_inventories.get(user_id, [])
    description = "\n".join([f"{i+1}. {item}" for i, item in enumerate(inventory)]) if inventory else 'No items found.'
    embed = interactions.Embed(
        title=f"{user.display_name}'s Inventory",
        description=description,
        color=0x0000ff
    )
    embed.set_thumbnail(url=get_logo_url())
    await ctx.send(embeds=[embed], ephemeral=True)

# Command to add an item to the inventory (only for authorized users)
@interactions.slash_command(
    name="additem",
    description="Add a shiny new item to someone's inventory.",
    options=[
        interactions.SlashCommandOption(
            name="user",
            description="User to add item to",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.SlashCommandOption(
            name="item",
            description="Item to add",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def add_item(ctx: interactions.SlashContext, user: interactions.User, item: str):
    if has_permission(ctx, "additem"):
        user_id = str(user.id)
        if user_id not in user_inventories:
            user_inventories[user_id] = []
        user_inventories[user_id].append(item)
        save_inventories()
        logger = get_user_logger(user_id)
        logger.info(f'Added {item} to {user.display_name}\'s inventory by {ctx.author.display_name}.')
        embed = interactions.Embed(
            title="Item Added",
            description=f'{ctx.author.display_name} added {item} to {user.display_name}\'s inventory. Shiny!',
            color=0x00ff00
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.send(embeds=[embed], ephemeral=True)
    else:
        role_mentions = get_role_mentions(ctx.guild)
        embed = interactions.Embed(
            title="Permission Denied",
            description=f"Oops! You don't have the power to add items. Better talk to a mod! {role_mentions}",
            color=0xff0000
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.send(embeds=[embed], ephemeral=True)

# Command to remove an item from the inventory (only for authorized users)
@interactions.slash_command(
    name="removeitem",
    description="Remove an item from someone's inventory.",
    options=[
        interactions.SlashCommandOption(
            name="user",
            description="User to remove item from",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.SlashCommandOption(
            name="item",
            description="Item to remove",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def remove_item(ctx: interactions.SlashContext, user: interactions.User, item: str):
    if has_permission(ctx, "removeitem"):
        user_id = str(user.id)
        if user_id in user_inventories and item in user_inventories[user_id]:
            user_inventories[user_id].remove(item)
            save_inventories()
            logger = get_user_logger(user_id)
            logger.info(f'{ctx.author.display_name} removed {item} from {user.display_name}\'s inventory.')
            embed = interactions.Embed(
                title="Item Removed",
                description=f'{ctx.author.display_name} removed {item} from {user.display_name}\'s inventory. Poof, it\'s gone!',
                color=0xff0000
            )
            embed.set_thumbnail(url=get_logo_url())
            await ctx.send(embeds=[embed], ephemeral=True)
        else:
            embed = interactions.Embed(
                title="Item Not Found",
                description=f'{item} not found in {user.display_name}\'s inventory. Oops!',
                color=0xffa500
            )
            embed.set_thumbnail(url=get_logo_url())
            await ctx.send(embeds=[embed], ephemeral=True)
    else:
        role_mentions = get_role_mentions(ctx.guild)
        embed = interactions.Embed(
            title="Permission Denied",
            description=f"Nope! You can't remove items. Ask a mod for help! {role_mentions}",
            color=0xff0000
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.send(embeds=[embed], ephemeral=True)

# Command to trade an item between two users (available to all users)
@interactions.slash_command(
    name="trade",
    description="Trade an item from one user to another. Sharing is caring!",
    options=[
        interactions.SlashCommandOption(
            name="item",
            description="Item to trade",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.SlashCommandOption(
            name="from_user",
            description="User to trade from",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.SlashCommandOption(
            name="to_user",
            description="User to trade to",
            type=interactions.OptionType.USER,
            required=True
        )
    ]
)
async def trade(ctx: interactions.SlashContext, item: str, from_user: interactions.User, to_user: interactions.User):
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
        embed = interactions.Embed(
            title="Item Traded",
            description=f'{ctx.author.display_name} traded {item} from {from_user.display_name} to {to_user.display_name}. How generous!',
            color=0x800080
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.send(embeds=[embed], ephemeral=True)
    else:
        embed = interactions.Embed(
            title="Trade Failed",
            description=f'{item} not found in {from_user.display_name}\'s inventory. No can do!',
            color=0xff0000
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.send(embeds=[embed], ephemeral=True)

# Command to view logs of a specific user (accessible by all users)
@interactions.slash_command(
    name="viewlogs",
    description="Sneak a peek at someone's activity logs. Shhh, it's a secret!",
    options=[
        interactions.SlashCommandOption(
            name="user",
            description="User to view logs of",
            type=interactions.OptionType.USER,
            required=False
        )
    ]
)
async def viewlogs(ctx: interactions.SlashContext, user: interactions.User = None):
    if user is None:
        user = ctx.author  # Default to the command invoker if no user is specified
    user_id = str(user.id)
    log_file_path = f'logs/{user_id}.log'
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            logs = log_file.read()
        embed = interactions.Embed(
            title=f"Logs for {user.display_name}",
            description=f"```\n{logs}\n```",
            color=0xffd700
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.send(embeds=[embed], ephemeral=True)
    else:
        embed = interactions.Embed(
            title="No Logs Found",
            description=f'No logs found for {user.display_name}. Seems squeaky clean!',
            color=0xff0000
        )
        embed.set_thumbnail(url=get_logo_url())
        await ctx.send(embeds=[embed], ephemeral=True)

# Command to show mod roles and the users with those roles
@interactions.slash_command(
    name="showrole",
    description="Show all mod roles and the users with those roles."
)
async def showrole(ctx: interactions.SlashContext):
    embed = interactions.Embed(title="Mod Roles", description="Here are all the mod roles and the users with those roles:", color=0x00ff00)
    guild = ctx.guild
    mod_roles = list(set(role_data["mod_roles"]))  # Ensure no duplicates
    
    # Include CG Dev role explicitly if not already included
    cg_dev_role = next((role for role in guild.roles if role.name == "🏆 CG Dev"), None)
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
    await ctx.send(embeds=[embed], ephemeral=True)

# Run the bot
bot.start()