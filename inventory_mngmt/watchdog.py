import time
import subprocess
from discord_webhook import DiscordWebhook
import random

# Define your webhook URL
WEBHOOK_URL = 'YOUR_DISCORD_WEBHOOK_URL'

# List of funny messages
funny_messages = [
    "Oh no! I'm melting! 🥶",
    "BRB, grabbing a coffee. ☕",
    "Who unplugged me? 😵",
    "I'll be back! 💪",
    "Zzz... need a nap. 😴",
    "Out of service, be back soon! 🚧",
]

def send_discord_message(message):
    webhook = DiscordWebhook(url=WEBHOOK_URL, content=message)
    webhook.execute()

# Function to start the bot
def start_bot():
    return subprocess.Popen(['python', 'inventory_bot.py'])

# Monitor the bot
def monitor_bot():
    bot_process = start_bot()
    try:
        while True:
            time.sleep(5)  # Check every 5 seconds
            if bot_process.poll() is not None:  # Bot has stopped
                message = random.choice(funny_messages)
                send_discord_message(message)
                bot_process = start_bot()
    except KeyboardInterrupt:
        bot_process.terminate()

if __name__ == '__main__':
    monitor_bot()
