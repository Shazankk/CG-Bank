import interactions
import logging
from collections import Counter
from config import user_inventories, get_user_logger, get_bot_logger, get_logo_url, save_inventories, has_permission, get_role_mentions

# Define the valid items
VALID_ITEMS = ["3h Mill", "3h Industry", "Half Cut trees"]


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
    try:
        logging.info(f"Received /inv command from user: {ctx.author.display_name}")

        user = user or ctx.author  # Default to the command invoker if no user is specified
        user_id = str(user.id)
        inventory = user_inventories.get(user_id, [])

        # Aggregate items and their counts
        inventory_counter = Counter(inventory)
        description = "\n".join([f"{count}x {item}" for item, count in inventory_counter.items()]) if inventory else 'No items found.'
        
        embed = interactions.Embed(
            title=f"{user.display_name}'s Inventory",
            description=description,
            color=0x0000ff
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        logging.info(f"Sending inventory for user: {user.display_name}")

        # Correct usage of interactions.File
        logo_file = interactions.File(get_logo_url(), file_name="cgcg.png")
        await ctx.send(embeds=[embed], files=[logo_file], ephemeral=False)
    except Exception as e:
        logging.error(f"Error in /inv command: {str(e)}")
        await ctx.send(f"Error: {str(e)}", ephemeral=True)


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
            required=True,
            choices=[interactions.SlashCommandChoice(name=item, value=item) for item in VALID_ITEMS]
        ),
        interactions.SlashCommandOption(
            name="quantity",
            description="Quantity of items to add",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def additem(ctx: interactions.SlashContext, user: interactions.User, item: str, quantity: int):
    if not has_permission(ctx, "additem"):
        await ctx.send("You don't have permission to use this command.", ephemeral=True)
        return

    try:
        user_id = str(user.id)
        if user_id not in user_inventories:
            user_inventories[user_id] = []
        user_inventories[user_id].extend([item] * quantity)
        save_inventories()

        logger = get_user_logger(user_id)
        bot_logger = get_bot_logger(ctx.author.id)
        logger.info(f'{ctx.author.display_name} added {quantity}x {item}.')
        bot_logger.info(f'{ctx.author.display_name} added {quantity}x {item} to {user.display_name}.')

        embed = interactions.Embed(
            title="Item Added",
            description=f'{ctx.author.display_name} added {quantity}x {item} to {user.display_name}\'s inventory.',
            color=0x00ff00
        )
        embed.set_thumbnail(url="attachment://cgcg.png")
        await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=False)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}", ephemeral=True)

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
            required=True,
            choices=[interactions.SlashCommandChoice(name=item, value=item) for item in VALID_ITEMS]
        ),
        interactions.SlashCommandOption(
            name="quantity",
            description="Quantity of items to remove",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def removeitem(ctx: interactions.SlashContext, user: interactions.User, item: str, quantity: int):
    if not has_permission(ctx, "removeitem"):
        await ctx.send("You don't have permission to use this command.", ephemeral=True)
        return

    try:
        user_id = str(user.id)
        if user_id in user_inventories and user_inventories[user_id].count(item) >= quantity:
            for _ in range(quantity):
                user_inventories[user_id].remove(item)
            save_inventories()

            logger = get_user_logger(user_id)
            bot_logger = get_bot_logger(ctx.author.id)
            logger.info(f'{ctx.author.display_name} removed {quantity}x {item}.')
            bot_logger.info(f'{ctx.author.display_name} removed {quantity}x {item} from {user.display_name}.')

            embed = interactions.Embed(
                title="Item Removed",
                description=f'{ctx.author.display_name} removed {quantity}x {item} from {user.display_name}\'s inventory.',
                color=0xff0000
            )
            embed.set_thumbnail(url="attachment://cgcg.png")
            await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=False)
        else:
            await ctx.send(f'{user.display_name} does not have {quantity}x {item}.', ephemeral=True)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}", ephemeral=True)

# Command to trade an item from one user to another
@interactions.slash_command(
    name="trade",
    description="Trade an item from one user's inventory to another.",
    options=[
        interactions.SlashCommandOption(
            name="item",
            description="Item to trade",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[interactions.SlashCommandChoice(name=item, value=item) for item in VALID_ITEMS]
        ),
        interactions.SlashCommandOption(
            name="quantity",
            description="Quantity of items to trade",
            type=interactions.OptionType.INTEGER,
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
async def trade(ctx: interactions.SlashContext, item: str, quantity: int, from_user: interactions.User, to_user: interactions.User):
    try:
        from_user_id = str(from_user.id)
        to_user_id = str(to_user.id)

        if from_user_id in user_inventories and user_inventories[from_user_id].count(item) >= quantity:
            for _ in range(quantity):
                user_inventories[from_user_id].remove(item)
            if to_user_id not in user_inventories:
                user_inventories[to_user_id] = []
            user_inventories[to_user_id].extend([item] * quantity)
            save_inventories()

            from_logger = get_user_logger(from_user_id)
            to_logger = get_user_logger(to_user_id)
            bot_logger = get_bot_logger(ctx.author.id)
            from_logger.info(f'{ctx.author.display_name} traded {quantity}x {item} to {to_user.display_name}.')
            to_logger.info(f'{ctx.author.display_name} received {quantity}x {item} from {from_user.display_name}.')
            bot_logger.info(f'{ctx.author.display_name} traded {quantity}x {item} from {from_user.display_name} to {to_user.display_name}.')

            embed = interactions.Embed(
                title="Item Traded",
                description=f'{ctx.author.display_name} traded {quantity}x {item} from {from_user.display_name} to {to_user.display_name}. How generous!',
                color=0x800080
            )
            embed.set_thumbnail(url="attachment://cgcg.png")
            await ctx.send(embeds=[embed], files=[interactions.File(file=open(get_logo_url(), 'rb'), file_name="cgcg.png")], ephemeral=False)
        else:
            await ctx.send(f'{item} not found in {from_user.display_name}\'s inventory or insufficient quantity.', ephemeral=True)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}", ephemeral=True)
