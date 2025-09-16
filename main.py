from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import json
import os

app = FastAPI()

# Get the signing key from an environment variable
# IMPORTANT: Store this securely.
# You can find this key in the Google Cloud Console under the Chat API configuration.
SIGNING_KEY = os.environ.get("GOOGLE_CHAT_SIGNING_KEY")

@app.post("/chat-bot")
async def chat_bot(request: Request):
    """
    Handles incoming messages from Google Chat.
    """
    if not SIGNING_KEY:
        raise HTTPException(status_code=500, detail="Google Chat signing key is not set.")

    # Get the timestamp and signature from the request headers
    timestamp = request.headers.get("X-Google-Signature-Timestamp")
    signature = request.headers.get("X-Google-Signature")

    # Read the request body
    body = await request.body()

    # Verify the request signature
    if not verify_signature(timestamp, signature, body, SIGNING_KEY):
        raise HTTPException(status_code=401, detail="Invalid signature.")

    try:
        data = json.loads(body)
        print(f"Received data: {data}")

        # Process the message
        event_type = data.get("type")
        if event_type == "MESSAGE":
            message = data.get("message", {}).get("text", "").lower()
            response_text = "Thanks for the message!"
            
            # Simple keyword-based response
            if "hello" in message:
                response_text = "Hello there! How can I help you today? 👋"
            elif "help" in message:
                response_text = "I am a simple bot. You can say 'hello' or 'help'!"

            return {"text": response_text}
        
        # You can handle other event types here like ADDED_TO_SPACE, REMOVED_FROM_SPACE, etc.
        return {"text": "I'm a bot and can't process that event type yet."}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")

def verify_signature(timestamp: str, signature: str, body: bytes, signing_key: str) -> bool:
    """
    Verifies the request signature from Google Chat.
    """
    if not all([timestamp, signature, body, signing_key]):
        return False
    
    # Concatenate the timestamp and the body
    message = f"{timestamp}.{body.decode('utf-8')}"
    
    # Calculate the HMAC-SHA256 hash
    calculated_signature = hmac.new(
        key=signing_key.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    # Decode the provided signature
    provided_signature = bytes.fromhex(signature)

    # Compare the signatures
    return hmac.compare_digest(calculated_signature, provided_signature)
