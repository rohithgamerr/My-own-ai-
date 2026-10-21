
import httpx
import os
import time
from datetime import datetime

TOKEN = os.environ.get('WHATSAPP_TOKEN')
PHONE_ID = os.environ.get('PHONE_NUMBER_ID')
USER_PHONE = os.environ.get('USER_PHONE')
ACK_FILE = "/root/lumina_bot/wake_up_ack.txt"

async def send_msg(text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": USER_PHONE,
        "type": "text",
        "text": {"body": text}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=data)

async def main():
    # 1. First Alert
    await send_msg("☀️ GOOD MORNING! It's 5:00 AM. Wake up! ☀️")
    
    # 2. Persistence Loop (Check every 2 mins for 10 mins)
    for i in range(1, 6):
        time.sleep(120) # Wait 2 minutes
        if os.path.exists(ACK_FILE):
            print("User acknowledged. Stopping alarm.")
            return
        
        messages = [
            "🚨 Still asleep? Get up!",
            "⏰ Wake up call #2! The world is waiting.",
            "⚠️ LUMINIA ALERT: You are still in bed!",
            "⚡️ WAKE UP! STOP IGNORING ME!",
            "🔥 FINAL WARNING: Time to start the day!"
        ]
        await send_msg(messages[i-1] if i-1 < len(messages) else "Wake up!")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
