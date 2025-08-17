from telethon import TelegramClient, events, Button
import asyncio
import re

# =========================
# CONFIGURATION
# =========================
API_ID = 25937429            # Get from https://my.telegram.org
API_HASH = "308b277930442c31ef113d0759da03cb"
SESSION_FILE = "Ken"  # Your existing .session file name (without .session extension)
GROUP_CHAT_ID = -1002674798301  # Replace with your fishing group chat ID
YOUR_USER_ID = 7493651695       # Replace with your numeric Telegram user ID
FISHING_BOT_ID = 5284997893     # Replace with the fishing bot's user ID
# =========================

# Initialize the client with your session file
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Track rod percentage
rod_percentage = 100
is_recharging = False


async def start_fishing():
    """Send /fish to start fishing"""
    global rod_percentage, is_recharging
    if is_recharging:
        return
    print("🎣 Sending /fish...")
    await client.send_message(GROUP_CHAT_ID, "/fish")


@client.on(events.NewMessage(chats=GROUP_CHAT_ID, from_users=FISHING_BOT_ID))
async def bot_message_handler(event):
    """Handle fishing bot messages"""
    global rod_percentage, is_recharging

    text = event.raw_text

    # Detect "Start fishing" button
    if "Start fishing" in text:
        buttons = await event.get_buttons()
        for row in buttons:
            for btn in row:
                if isinstance(btn, Button.inline) and b"Start fishing" in btn.data:
                    print("🎯 Clicking Start fishing...")
                    await event.click(0)  # Click first button
                    return

    # Detect "Caught" (Fishing result)
    if "Caught" in text:
        print("🐟 Caught detected, checking rod percentage...")
        # Extract rod percentage
        match = re.search(r"\[(\d+)%\]", text)
        if match:
            rod_percentage = int(match.group(1))
            print(f"📊 Rod at {rod_percentage}%")

        if rod_percentage > 10:
            await asyncio.sleep(1)  # Small delay before next fishing
            await start_fishing()
        elif rod_percentage == 10:
            print("⚠️ Last fishing before recharge...")
            await asyncio.sleep(1)
            await start_fishing()
            print("⏳ Waiting 5 minutes for recharge...")
            is_recharging = True
            await asyncio.sleep(300)  # 5 min recharge
            is_recharging = False
            await start_fishing()


async def main():
    print("🚀 Fishing bot started!")
    await start_fishing()


with client:
    client.loop.run_until_complete(main())

    client.run_until_disconnected()
