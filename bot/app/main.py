import os
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Environment Variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
LUMINA_AI_API_KEY = os.getenv("LUMINA_AI_API_KEY")
LUMINA_AI_URL = os.getenv("LUMINA_AI_URL")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

class WhatsAppMessage(BaseModel):
    from_: str
    body: str

async def get_lumina_response(user_text: str) -> str:
    """Routes the query to the Lumina AI Engine."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                LUMINA_AI_URL,
                headers={"Authorization": f"Bearer {LUMINA_AI_API_KEY}"},
                json={"message": user_text},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "I'm sorry, I couldn't process that request.")
        except Exception as e:
            print(f"Lumina AI Error: {e}")
            return "I'm having trouble connecting to my brain right now. Please try again later!"

async def send_whatsapp_message(to: str, text: str):
    """Sends the response back via the WhatsApp Business API."""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.status_code

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Handles the WhatsApp webhook verification process."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def handle_message(request: Request):
    """Receives and processes incoming WhatsApp messages."""
    data = await request.json()
    
    # WhatsApp sends notifications in a specific nested structure
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        if "messages" in value:
            message = value["messages"][0]
            sender_id = message["from"]
            text_body = message["text"]["body"]
            
            # 1. Route to Lumina AI
            ai_response = await get_lumina_response(text_body)
            
            # 2. Send back to WhatsApp
            await send_whatsapp_message(sender_id, ai_response)
            
        return Response(status_code=200)
    except (KeyError, IndexError) as e:
        print(f"Unexpected payload structure: {e}")
        return Response(status_code=200) # Always return 200 to avoid WhatsApp retries

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
