# Deployment & Setup Guide: Lumina WhatsApp Bot

This guide provides step-by-step instructions to set up and deploy the Lumina WhatsApp Bot, from configuring your provider accounts to production deployment using Docker.

---

## 1. Provider Account Setup

The Lumina Bot utilizes the **WhatsApp Business API** (via Meta/Facebook).

### Setting up a Meta for Developers Account
1. **Create a Developer Account**: Go to [developers.facebook.com](https://developers.facebook.com/) and log in with your Facebook account.
2. **Create an App**:
   - Click **My Apps** $\rightarrow$ **Create App**.
   - Select **Other** $\rightarrow$ **Next**.
   - Select **Business** as the app type.
   - Give your app a name (e.g., `LuminaBot`) and connect it to your Business Account.
3. **Add WhatsApp to Your App**:
   - From the App Dashboard, find **WhatsApp** and click **Set up**.
   - Follow the prompts to add a phone number or use the provided test number for development.
4. **Get Your Credentials**:
   - In the WhatsApp $\rightarrow$ **Getting Started** section, you will find:
     - **Temporary Access Token**: (Used for `WHATSAPP_TOKEN` in `.env`). *Note: Temporary tokens expire in 24 hours. For production, create a Permanent System User Token in the Business Manager.*
     - **Phone Number ID**: (Used for `WHATSAPP_PHONE_NUMBER_ID` in `.env`).
     - **WhatsApp Business Account ID**.

---

## 2. Webhook Configuration

The bot needs a public URL to receive messages from WhatsApp in real-time.

### Configuring the Webhook in Meta Dashboard
1. **Navigate to Webhooks**: In the Meta App Dashboard, go to **WhatsApp** $\rightarrow$ **Configuration**.
2. **Set Callback URL**:
   - **Callback URL**: Enter your production URL followed by `/webhook` (e.g., `https://api.luminabot.com/webhook`).
   - **Verify Token**: Enter a random string of your choice. This must match the `VERIFY_TOKEN` in your `.env` file.
3. **Verify and Save**:
   - Click **Verify and Save**. Meta will send a GET request to your server to verify the token.
4. **Subscribe to Fields**:
   - Once verified, click **Manage** next to Webhook fields.
   - Subscribe to **messages**. This ensures your server is notified whenever a user sends a message.

---

## 3. Production Deployment

We use Docker for a consistent environment across development and production.

### Prerequisites
- A server with Docker and Docker Compose installed.
- A public IP or domain with SSL (WhatsApp requires HTTPS).
- A reverse proxy (e.g., Nginx, Caddy, or Traefik) to handle SSL termination.

### Step-by-Step Deployment

#### 1. Prepare the Environment
Create a `.env` file in the root directory of the bot:
```env
WHATSAPP_TOKEN=your_meta_permanent_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_chosen_verification_token
LUMINA_AI_API_KEY=your_lumina_ai_api_key
LUMINA_AI_URL=https://api.lumina.ai/v1/chat
```

#### 2. Dockerize the Application
Create a `Dockerfile` in `/root/lumina_bot/`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Build and Run
Run the following commands on your production server:

```bash
# Build the image
docker build -t lumina-whatsapp-bot .

# Run the container in detached mode
docker run -d \
  --name lumina-bot \
  -p 8000:8000 \
  --env-file .env \
  --restart always \
  lumina-whatsapp-bot
```

### Summary of Production Architecture
- **WhatsApp Business API** $\rightarrow$ **Reverse Proxy (SSL)** $\rightarrow$ **Docker Container (FastAPI)** $\rightarrow$ **Lumina AI Engine**.
