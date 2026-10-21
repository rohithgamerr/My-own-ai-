
import httpx
import os
async def send_reminder():
    TOKEN = os.environ.get('WHATSAPP_TOKEN')
    PHONE_ID = os.environ.get('PHONE_NUMBER_ID')
    USER_PHONE = os.environ.get('USER_PHONE')
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": USER_PHONE,
        "type": "text",
        "text": {"body": "🔔 REMINDER: It's 10:50 AM! Your scheduled task is due. - Lumina Core"}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=data)

if __name__ == '__main__':
    import asyncio
    asyncio.run(send_reminder())
