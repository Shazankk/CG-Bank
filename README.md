# CG Bank Bot

![CG Bank](assets/cgcg.png)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Commands](#commands)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Developer](#developer)
- [Support](#support)

## Introduction

CG Bank Bot is a feature-rich Discord bot designed to manage inventories, assign roles, and provide a seamless trading experience. The bot includes functionalities for adding, removing, and viewing items in user inventories, trading items between users, and managing roles with ease. 

## Features

- **Inventory Management**: Add, remove, and view items in user inventories.
- **Role Management**: Assign and remove permissions for specific commands.
- **Trading System**: Trade items between users with logging for transparency.
- **Logs**: View detailed logs of user activities.
- **Interactive Help Command**: An interactive help command with dropdowns to show examples of how to use each command.

## Commands

### Inventory Commands

- `!inv [@username]`: Peek into someone's inventory, or your own if you're feeling nosy! 
  - Example: `!inv @user` or `!inv`

- `!additem @username item_name`: Add a shiny new item to someone's inventory.
  - Example: `!additem @user CoolItem`

- `!removeitem @username item_name`: Remove an item from someone's inventory.
  - Example: `!removeitem @user CoolItem`

- `!trade item_name @from_user @to_user`: Trade an item from one user to another. Sharing is caring!
  - Example: `!trade CoolItem @user1 @user2`

### Admin Commands

- `!giverole @username @command`: Give a user permission for a specific command.
  - Example: `!giverole @user additem`

- `!droprole @username @command`: Remove a user's permission for a specific command.
  - Example: `!droprole @user additem`

### Other Commands

- `!viewlogs [@username]`: Sneak a peek at someone's activity logs. Shhh, it's a secret!
  - Example: `!viewlogs @user`

- `!showhelp`: List all commands with descriptions and examples. Includes an interactive dropdown menu for selecting commands.
  
## Inviting the Bot
To invite the bot to your server, use the following URL: [CG Bank Bot](https://discord.com/api/oauth2/authorize?client_id=1242981337342677003&permissions=[532576418880]&scope=bot%20applications.commands)


## Installation

To install the CG Bank Bot, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/cgbank-bot.git
    ```

2. Navigate to the project directory:
    ```bash
    cd cgbank-bot
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the project root directory and add your Discord bot token:
    ```
    DISCORD_BOT_TOKEN=your_discord_bot_token
    ```

2. Ensure the `assets` directory contains the `cgcg.png` image for the bot logo.

## Running the Bot

To run the bot, simply execute the following command:
```bash
python inventory_bot.py
```

## Developer
```
This bot was developed by Shashank Goud.
Email: shashaankgoud@gmail.com
Ethereum Wallet: 0xf50fBB149Dccfcf1a57A516cCdfC663B6B4D5381
Ronin Wallet: 0xf9efaba8813f228ea40f24dc8b143b82bc8e0b5a
```
If you like the bot and would like to support the development or just want to buy me a coffee, feel free to send some ETH or NFTs to the above wallet address. Your support is greatly appreciated!

## Support

If you encounter any issues or have any questions, feel free to reach out via email. Contributions to the project are also welcome!

Enjoy using CG Bank Bot!