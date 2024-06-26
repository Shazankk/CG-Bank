import interactions
from config import role_data, save_roles, get_logo_url

# Helper function to make announcements
async def announce_change(ctx, description):
    embed = interactions.Embed(
        title="Admin Update",
        description=description,
        color=0xffa500
    )
    await ctx.send(embeds=[embed])

# Command to give a user permission for a specific command
@interactions.slash_command(
    name="bankgiverole",
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
                interactions.SlashCommandChoice(name="bankadditem", value="bankadditem"),
                interactions.SlashCommandChoice(name="bankremoveitem", value="bankremoveitem")
            ]
        )
    ]
)
async def bankgiverole(ctx: interactions.SlashContext, user: interactions.User, command_name: str):
    member = ctx.guild.get_member(ctx.author.id)
    if not member:
        await ctx.send("You are not a member of this guild.", ephemeral=False)
        return

    # Check if the user has the necessary permissions
    if not (
        member.has_permission(interactions.Permissions.ADMINISTRATOR) or
        any(role.id in role_data["mod_roles"] for role in member.roles) or
        any(role.name == "🏆 CG Dev" for role in member.roles)
    ):
        await ctx.send("You are missing the necessary permissions to run this command.", ephemeral=False)
        return

    if str(user.id) not in role_data["permissions"]:
        role_data["permissions"][str(user.id)] = []
    
    role_data["permissions"][str(user.id)].append(command_name)
    save_roles(role_data)
    await ctx.send(f"User {user.mention} has been given permission to use `{command_name}`.", ephemeral=True)

    # Announce the change
    await announce_change(ctx, f"User {user.mention} has been given permission to use `{command_name}`.")

# Command to remove a user's permission for a specific command
@interactions.slash_command(
    name="bankdroprole",
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
                interactions.SlashCommandChoice(name="bankadditem", value="bankadditem"),
                interactions.SlashCommandChoice(name="bankremoveitem", value="bankremoveitem")
            ]
        )
    ]
)
async def bankdroprole(ctx: interactions.SlashContext, user: interactions.User, command_name: str):
    member = ctx.guild.get_member(ctx.author.id)
    if not member:
        await ctx.send("You are not a member of this guild.", ephemeral=False)
        return

    # Check if the user has the necessary permissions
    if not (
        member.has_permission(interactions.Permissions.ADMINISTRATOR) or
        any(role.id in role_data["mod_roles"] for role in member.roles) or
        any(role.name == "🏆 CG Dev" for role in member.roles)
    ):
        await ctx.send("You are missing the necessary permissions to run this command.", ephemeral=False)
        return

    if str(user.id) in role_data["permissions"] and command_name in role_data["permissions"][str(user.id)]:
        role_data["permissions"][str(user.id)].remove(command_name)
        save_roles(role_data)
        await ctx.send(f"User {user.mention}'s permission to use `{command_name}` has been removed.", ephemeral=True)
            # Announce the change
        await announce_change(ctx, f"User {user.mention}'s permission to use `{command_name}` has been removed.")

    else:
        await ctx.send(f"User {user.mention} does not have permission for `{command_name}`.", ephemeral=True)
