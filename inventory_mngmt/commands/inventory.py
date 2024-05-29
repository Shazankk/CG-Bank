import interactions
from config import user_inventories, get_user_logger, get_bot_logger, get_logo_url, save_inventories, has_permission, get_role_mentions

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
    embed.set_thumbnail(url="attachment://cgcg.png")
    await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)

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
        bot_logger = get_bot_logger(ctx.author.id)
        logger.info(f'Added {item} to {user.display_name}\'s inventory by {ctx.author.display_name}.')
        bot_logger.info(f'Added {item} to {user.display_name}\'s inventory by {ctx.author.display_name}.')
        embed = interactions.Embed(
            title="Item Added",
            description=f'{ctx.author.display_name} added {item} to {user.display_name}\'s inventory. Shiny!',
            color=0x00ff00
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)
    else:
        role_mentions = get_role_mentions(ctx.guild)
        embed = interactions.Embed(
            title="Permission Denied",
            description=f"Oops! You don't have the power to add items. Better talk to a mod! {role_mentions}",
            color=0xff0000
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)

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
            bot_logger = get_bot_logger(ctx.author.id)
            logger.info(f'{ctx.author.display_name} removed {item} from {user.display_name}\'s inventory.')
            bot_logger.info(f'{ctx.author.display_name} removed {item} from {user.display_name}\'s inventory.')
            embed = interactions.Embed(
                title="Item Removed",
                description=f'{ctx.author.display_name} removed {item} from {user.display_name}\'s inventory. Poof, it\'s gone!',
                color=0xff0000
            )
            embed.set_thumbnail(url="attachment://cgcg.png")
            await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)
        else:
            embed = interactions.Embed(
                title="Item Not Found",
                description=f'{item} not found in {user.display_name}\'s inventory. Oops!',
                color=0xffa500
            )
            embed.set_thumbnail(url="attachment://cgcg.png")
            await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)
    else:
        role_mentions = get_role_mentions(ctx.guild)
        embed = interactions.Embed(
            title="Permission Denied",
            description=f"Nope! You can't remove items. Ask a mod for help! {role_mentions}",
            color=0xff0000
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)

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
        bot_logger = get_bot_logger(ctx.author.id)
        from_logger.info(f'{ctx.author.display_name} traded {item} to {to_user.display_name}.')
        to_logger.info(f'{ctx.author.display_name} received {item} from {from_user.display_name}.')
        bot_logger.info(f'{ctx.author.display_name} traded {item} from {from_user.display_name} to {to_user.display_name}.')
        embed = interactions.Embed(
            title="Item Traded",
            description=f'{ctx.author.display_name} traded {item} from {from_user.display_name} to {to_user.display_name}. How generous!',
            color=0x800080
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)
    else:
        embed = interactions.Embed(
            title="Trade Failed",
            description=f'{item} not found in {from_user.display_name}\'s inventory. No can do!',
            color=0xff0000
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(fp=open(get_logo_url(), 'rb'), filename="cgcg.png")], ephemeral=True)
