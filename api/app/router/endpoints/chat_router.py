from fastapi import APIRouter, Depends, HTTPException, status
from app.usecase.chat_service import ChatService, get_chat_service

chatRouter = APIRouter()
CHATSESSION = None

#end point that initiate the router 
@chatRouter.post("/chat/new")
async def initiate_chat(
    chatService: ChatService = Depends(get_chat_service)
):
    global CHATSESSION
    CHATSESSION = chatService.new_chat()

    return {"message": "Chat session initiated."}

@chatRouter.post("/chat")
async def respond(
    prompt: str,
    chatService: ChatService = Depends(get_chat_service)
):
    response = chatService.get_response(chat_session=CHATSESSION, prompt=prompt)

    return {"message": "Response received for chat.", "response": response}


