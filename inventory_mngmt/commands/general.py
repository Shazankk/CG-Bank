import os
import interactions
from interactions import Embed, File
from config import role_data, get_logo_url, get_user_logger, get_bot_logger

# Command to view logs of a specific user (accessible by all users)
@interactions.slash_command(
    name="banklogs",
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
async def banklogs(ctx: interactions.SlashContext, user: interactions.User = None):
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
        await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=False)
    else:
        embed = interactions.Embed(
            title="No Logs Found",
            description=f'No logs found for {user.display_name}. Seems squeaky clean!',
            color=0xff0000
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=False)


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
            "bankinv": {
                "description": "Peek into someone's inventory, or your own if you're feeling nosy!",
                "example": "/inv @username or /inv"
            },
            "bankadditem": {
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
            embed.add_field(name=f"**{category}**", value=commands_description, inline=False)

    embed.set_thumbnail(url="attachment://cgcg.png")
    embed.set_author(name="CG Bank", icon_url="attachment://cgcg.png")

    await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=False)

@interactions.slash_command(
    name="cgpass",
    description="Get information about the CG Pass rewards."
)
async def cgpass(ctx: interactions.SlashContext):
    embed = interactions.Embed(
        title="CG Pass Rewards and Mods",
        description=(
            "Congratulations! With the CG Pass, you get the following rewards:\n\n"
            "**1. Access to [Giveaways](https://discord.com/channels/881509696882757643/961320997468926002) channel**\n\n"
            "**2. 8 Half-Cut Trees**\n"
            "🌳🌳🌳🌳🌳🌳🌳🌳\n\n"
            "**3. 8 3h Mill Boosts**\n"
            "⏳⏳⏳⏳⏳⏳⏳⏳\n\n"
            "**4. 8 3h Industry Boosts**\n"
            "🏭🏭🏭🏭🏭🏭🏭🏭\n\n"
            "**We are available on [OpenSea](https://opensea.io/assets/matic/0x1cd70c8c8bac5fb395f2c5dd5f25859ab9b446c0/1)**\n\n\n"
            "Here are all the mod roles and the users with those roles:"

        ),
        color=0x00ff00
    )

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
    await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=False)