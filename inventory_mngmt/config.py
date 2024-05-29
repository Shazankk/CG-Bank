import os
import json
import logging

import interactions

# Initialize shared data
user_inventories = {}
role_data = {}

# Ensure necessary directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Path to the logo image
logo_path = os.path.join(os.getcwd(), 'assets', 'cgcg.png')

# Function to get the logo URL
def get_logo_url():
    return logo_path

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

# Function to get logger for bot actions by a specific user
def get_bot_logger(user_id):
    logger = logging.getLogger(f"bot_{user_id}")
    if not logger.hasHandlers():
        handler = logging.FileHandler(f'logs/bot_{user_id}.log')
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

# Load roles and inventories into memory
role_data = load_roles()
user_inventories = load_inventories()

# Check if a user has the necessary permissions
def has_permission(ctx, command_name):
    member = ctx.guild.get_member(ctx.author.id)
    if not member:
        return False
    user_permissions = role_data["permissions"].get(str(ctx.author.id), [])
    if command_name in ["additem", "removeitem"]:
        return (
            command_name in user_permissions or
            any(role.id in role_data["mod_roles"] for role in member.roles) or
            any(role.name == "🏆 CG Dev" for role in member.roles) or
            member.has_permission(interactions.Permissions.ADMINISTRATOR)
        )
    return True

# Get the role mentions
def get_role_mentions(guild):
    mod_roles = [f"<@&{role_id}>" for role_id in role_data["mod_roles"]]
    return ", ".join(mod_roles) if mod_roles else "@MODERATOR"
