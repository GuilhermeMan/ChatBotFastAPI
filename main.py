from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/chat-bot")
async def chat_bot(request: Request):
    """
    Handles incoming messages from Google Chat without signature verification.
    
    WARNING: This is INSECURE and NOT recommended for production use.
    """
    try:
        body = await request.body()
        data = json.loads(body)
        print(f"Received data: {data}")

        # Process the message
        event_type = data.get("type")
        if event_type == "MESSAGE":
            message = data.get("message", {}).get("text", "").lower()
            response_text = "Thanks for the message!"
            
            # Simple keyword-based response
            if "hello" in message:
                response_text = "Hello there! 👋"
            elif "help" in message:
                response_text = "I am a simple bot."

            return {"text": response_text}
        
        return {"text": "I'm a bot and can't process that event type yet."}

    except json.JSONDecodeError:
        # It's still good practice to handle JSON errors
        return {"text": "Invalid JSON format."}
