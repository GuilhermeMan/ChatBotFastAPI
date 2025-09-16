from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import json
import os

app = FastAPI()

SIGNING_KEY = os.environ.get("GOOGLE_CHAT_SIGNING_KEY")

@app.post("/chat-bot")
async def chat_bot(request: Request):
    """
    Handles incoming messages from Google Chat with robust error handling.
    """
    if not SIGNING_KEY:
        raise HTTPException(status_code=500, detail="Google Chat signing key is not set.")

    timestamp = request.headers.get("X-Google-Signature-Timestamp")
    signature = request.headers.get("X-Google-Signature")

    body = await request.body()
    
    if not verify_signature(timestamp, signature, body, SIGNING_KEY):
        raise HTTPException(status_code=401, detail="Invalid signature.")

    try:
        data = json.loads(body)
        print(f"Received data: {data}")

        # The 'type' key might be nested, so we check for different event types.
        if data.get("type") == "ADDED_TO_SPACE":
            return {"text": "Thanks for adding me to this space! How can I help?"}

        # Check for message events, which are common payloads
        if 'message' in data:
            message_text = data.get("message", {}).get("text", "").lower()
            if "hello" in message_text:
                return {"text": "Hello there! 👋"}
            elif "help" in message_text:
                return {"text": "I am a simple bot. You can say 'hello'!"}
            else:
                return {"text": "I received your message."}

        # Handle events with a message payload, like from a bot-DM
        if 'messagePayload' in data and 'message' in data['messagePayload']:
            message_text = data['messagePayload']['message'].get('text', '').lower()
            if "hello" in message_text:
                return {"text": "Hello there! 👋"}
            elif "help" in message_text:
                return {"text": "I am a simple bot."}
            else:
                return {"text": "Thanks for the message!"}
        
        # Default response for unhandled events
        return {"text": "I'm a bot and can't process that event type yet."}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")

def verify_signature(timestamp: str, signature: str, body: bytes, signing_key: str) -> bool:
    """
    Verifies the request signature from Google Chat.
    """
    if not all([timestamp, signature, body, signing_key]):
        return False
    
    message = f"{timestamp}.{body.decode('utf-8')}"
    
    calculated_signature = hmac.new(
        key=signing_key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    provided_signature = bytes.fromhex(signature)

    return hmac.compare_digest(calculated_signature, provided_signature)
