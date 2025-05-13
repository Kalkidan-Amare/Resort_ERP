from app.AI.chatbot import initialize_chat_session


class ChatService:
    async def new_chat(self):
        print("Initializing new chat session...")
        try:
            print("Starting the chatbot...")
            cs = await initialize_chat_session()  # Fixed typo and added await
            print(cs, "cs")
        except Exception as e:
            print(f"Error initializing chat session: {e}")
            raise Exception("Failed to initialize chat session.")
        return cs  # Return the initialized chat session
    
    async def get_response(self, chat_session, prompt: str):
        print("Starting the chatbot...")
        print("This may take a moment to initialize the servers...")
        print("Processing prompt...")

        response = await chat_session.process_message(prompt)
        return response


def get_chat_service():
    return ChatService()