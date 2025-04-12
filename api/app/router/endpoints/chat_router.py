from fastapi import APIRouter, Depends, HTTPException, status
from app.usecase.chat_service import ChatService, get_chat_service

chatRouter = APIRouter()
CHATSESSION = None
print("Chat router initialized.")
#end point that initiate the router 
@chatRouter.post("/chat/new")
async def initiate_chat(
    chatService: ChatService = Depends(get_chat_service)
):
    
    global CHATSESSION
    try:
        CHATSESSION = await chatService.new_chat()  # Await the asynchronous method
    except Exception as e:
        print(f"Error initializing chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize chat session.")

    print("Initiating new chat session...")
    return {"message": "Chat session initiated." }

@chatRouter.post("/chat")
async def respond(
    prompt: str,
    chatService: ChatService = Depends(get_chat_service)
):
    response = await chatService.get_response(chat_session=CHATSESSION, prompt=prompt)

    return {"message": "Response received for chat.", "response": response}


