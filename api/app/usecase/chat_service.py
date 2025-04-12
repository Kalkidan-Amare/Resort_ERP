from app.AI.chatbot import initialize_chat_session


class ChatService:
    def __init__(self):
        pass    
    
    def new_chat(self):
        return initialize_chat_session    
    
    def get_response(self, chat_session, prompt: str):
        print("Starting the chatbot...")
        print("This may take a moment to initialize the servers...")

       

        response = chat_session.process_message(prompt)
        return response



def get_chat_service():
    return ChatService