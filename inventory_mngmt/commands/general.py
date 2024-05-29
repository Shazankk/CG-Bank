import os
import interactions
from config import role_data, get_logo_url, get_user_logger, get_bot_logger

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
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=True)
    else:
        embed = interactions.Embed(
            title="No Logs Found",
            description=f'No logs found for {user.display_name}. Seems squeaky clean!',
            color=0xff0000
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=True)

# Command to show all actions taken by a specific user via the bot
@interactions.slash_command(
    name="viewbotlogs",
    description="View everything that happened via bot by a particular user.",
    options=[
        interactions.SlashCommandOption(
            name="user",
            description="User to view bot logs of",
            type=interactions.OptionType.USER,
            required=False
        )
    ]
)
async def viewbotlogs(ctx: interactions.SlashContext, user: interactions.User = None):
    if user is None:
        user = ctx.author  # Default to the command invoker if no user is specified
    user_id = str(user.id)
    log_file_path = f'logs/bot_{user_id}.log'
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            logs = log_file.read()
        embed = interactions.Embed(
            title=f"Bot Logs for {user.display_name}",
            description=f"```\n{logs}\n```",
            color=0xffd700
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=True)
    else:
        embed = interactions.Embed(
            title="No Bot Logs Found",
            description=f'No bot logs found for {user.display_name}.',
            color=0xff0000
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=True)

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

    roles_and_permissions = {}
    for role_id in mod_roles:
        role = guild.get_role(role_id)
        if role:
            members = [member.mention for member in role.members]
            if members:
                roles_and_permissions[role.name] = members

    specific_permissions = []
    for user_id, permissions in role_data["permissions"].items():
        if permissions:  # Only include users with existing permissions
            member = guild.get_member(int(user_id))
            if member:
                specific_permissions.append(member.mention)

    if not roles_and_permissions and not specific_permissions:
        embed.add_field(name="No Mod Roles", value="No mod roles have been assigned yet.", inline=False)
    else:
        for role, members in roles_and_permissions.items():
            member_list = "\n".join(set(members))  # Ensure no duplicates
            embed.add_field(name=role, value=member_list, inline=False)
        if specific_permissions:
            specific_member_list = "\n".join(set(specific_permissions))  # Ensure no duplicates
            embed.add_field(name="Specific Command Permissions", value=specific_member_list, inline=False)

    embed.set_thumbnail(url="attachment://cgcg.png")
    await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=True)

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
            },
            "viewbotlogs": {
                "description": "View everything that happened via bot by a particular user.",
                "example": "/viewbotlogs @username"
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

    embed.set_thumbnail(url="attachment://cgcg.png")
    embed.set_author(name="CG Bank", icon_url="attachment://cgcg.png")

    await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=True)
