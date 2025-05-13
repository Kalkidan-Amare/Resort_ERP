import asyncio
import json
import logging
from app.core.database import get_db
from app.repo.room_repo import RoomRepository
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any
from app.core.config import settings
import httpx
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
# Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler("grok_chatbot.log"),
#         # logging.StreamHandler()
#     ]
# )

_SETTINGS = None

class Configuration:
    """Manages configuration and environment variables for the MCP client."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        global _SETTINGS
        _SETTINGS = settings
        self.settings = settings

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file."""
        load_dotenv()

    @staticmethod
    def load_config(file_path: str) -> dict[str, Any]:
        """Load server configuration from JSON file.

        Args:
            file_path: Path to the JSON configuration file.

        Returns:
            Dict containing server configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            JSONDecodeError: If configuration file is invalid JSON.
        """
        with open(file_path, "r") as f:
            return json.load(f)

    # @property
    # def llm_api_key(self) -> str:
    #     """Get the LLM API key.

    #     Returns:
    #         The API key as a string.

    #     Raises:
    #         ValueError: If the API key is not found in environment variables.
    #     """
    #     if not self.api_key:
    #         raise ValueError("LLM_API_KEY not found in environment variables")
    #     return self.api_key


class Server:
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name: str = name
        self.config: dict[str, Any] = config
        self.stdio_context: Any | None = None
        self.session: ClientSession | None = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self) -> None:
        """Initialize the server connection."""
        command = (
            shutil.which("npx")
            if self.config["command"] == "npx"
            else self.config["command"]
        )
        if command is None:
            raise ValueError("The command must be a valid string and cannot be None.")

        server_params = StdioServerParameters(
            command=command,
            args=self.config["args"],
            env={**os.environ, **self.config["env"]}
            if self.config.get("env")
            else None,
        )
        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.session = session
            # logging.info(f"Server {self.name} initialized successfully.")
        except Exception as e:
            # logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise


    async def list_tools(self) -> list[Any]:
        if not self.session:
            # logging.error(f"Server {self.name} not initialized")
            raise RuntimeError(f"Server {self.name} not initialized")

        # logging.debug("getting tools")
        tools_response = await self.session.list_tools()
        if not tools_response:
            # logging.warning(f"No tools found for server {self.name}")
            return []
        tools = []
        # logging.info(f"Raw tools response from {self.name}: {tools_response}")

        for item in tools_response:
            if isinstance(item, tuple) and item[0] == "tools":
                for tool in item[1]:
                    # logging.info(f"Server: {self.name}, Tool: {tool.name}, Description: {tool.description}")
                    tools.append(Tool(tool.name, tool.description, tool.inputSchema))
        return tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] = {},
        retries: int = 2,
        delay: float = 1.0,
    ) -> Any:
        """Execute a tool with retry mechanism.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            retries: Number of retry attempts.
            delay: Delay between retries in seconds.

        Returns:
            Tool execution result.

        Raises:
            RuntimeError: If server is not initialized.
            Exception: If tool execution fails after all retries.
        """
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        while attempt < retries:
            try:
                # logging.info(f"Executing {tool_name}...")
                result = await self.session.call_tool(tool_name, arguments)

                return result

            except Exception as e:
                attempt += 1
                # logging.warning(
                #     f"Error executing tool: {e}. Attempt {attempt} of {retries}."
                # )
                if attempt < retries:
                    # logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    # logging.error("Max retries reached. Failing.")
                    raise

    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                self.stdio_context = None
            except Exception as e:
                # logging.error(f"Error during cleanup of server {self.name}: {e}")
                pass


class Tool:
    """Represents a tool with its properties and formatting."""

    def __init__(
        self, name: str, description: str, input_schema: dict[str, Any] = {}
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema

    def format_for_llm(self) -> str:
        """Format tool information for LLM.

        Returns:
            A formatted string describing the tool.
        """
        args_desc = []
        if "properties" in self.input_schema:
            for param_name, param_info in self.input_schema["properties"].items():
                arg_desc = (
                    f"- {param_name}: {param_info.get('description', 'No description')}"
                )
                if param_name in self.input_schema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        return f"""
Tool: {self.name}
Description: {self.description}
Arguments:
{chr(10).join(args_desc)}
"""


class LLMClient:
    """Manages communication with the LLM provider."""

    def __init__(self, settings) -> None:
        self.token = settings.TOKEN
        self.endpoint = settings.ENDPOINT
        self.model_name = settings.MODEL_NAME

    def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get a response from the LLM.

        Args:
            messages: A list of message dictionaries.

        Returns:
            The LLM's response as a string.

        Raises:
            httpx.RequestError: If the request to the LLM fails.
        """
        client = OpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )

        response = client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            stream=True,
            stream_options={'include_usage': True}
        )

        usage = None
        content_chunks = []

        for update in response:
            if update.choices and update.choices[0].delta:
                chunk = update.choices[0].delta.content or ""
                content_chunks.append(chunk)
            # if update.usage:
            #     usage = update.usage

        full_content = "".join(content_chunks)

        # if usage:
        #     print("\n")
        #     for k, v in usage.dict().items():
        #         print(f"{k} = {v}")

        return full_content


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, servers: list[Server], llm_client: LLMClient) -> None:
        self.servers: list[Server] = servers
        self.llm_client: LLMClient = llm_client
        self.messages: list[dict[str, str]] = []
        self.initialized: bool = False

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        cleanup_tasks = []
        for server in self.servers:
            cleanup_tasks.append(asyncio.create_task(server.cleanup()))

        if cleanup_tasks:
            try:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            except Exception as e:
                # logging.warning(f"Warning during final cleanup: {e}")
                pass

    async def process_llm_response(self, llm_response: str) -> str:
        """Process the LLM response and execute tools if needed.

        Args:
            llm_response: The response from the LLM.

        Returns:
            The result of tool execution or the original response.
        """
        import json

        try:
            tool_call = json.loads(llm_response)
            if "tool" in tool_call and "arguments" in tool_call:
                # logging.info(f"Executing tool: {tool_call['tool']}")
                # logging.info(f"With arguments: {tool_call['arguments']}")

                for server in self.servers:
                    tools = await server.list_tools()
                    if any(tool.name == tool_call["tool"] for tool in tools):
                        try:
                            result = await server.execute_tool(
                                tool_call["tool"], tool_call["arguments"]
                            )

                            if isinstance(result, dict) and "progress" in result:
                                progress = result["progress"]
                                total = result["total"]
                                percentage = (progress / total) * 100
                                # logging.info(
                                #     f"Progress: {progress}/{total} "
                                #     f"({percentage:.1f}%)"
                                # )

                            return f"Tool execution result: {result}"
                        except Exception as e:
                            error_msg = f"Error executing tool: {str(e)}"
                            # logging.error(error_msg)
                            return error_msg

                return f"No server found with tool: {tool_call['tool']}"
            return llm_response
        except json.JSONDecodeError:
            return llm_response

    async def initialize(self, with_tools: bool = True) -> None:
        """Initialize the chat session and servers.

        Args:
            with_tools: Whether to initialize with tools or use a basic assistant.
        """
        if self.initialized:
            return

        if with_tools and self.servers:
            # Initialize servers
            for server in self.servers:
                try:
                    await server.initialize()
                except Exception as e:
                    # logging.error(f"Failed to initialize server: {e}")
                    await self.cleanup_servers()
                    raise RuntimeError(f"Failed to initialize server: {str(e)}")

            # Get tools from all servers
            all_tools = []
            for server in self.servers:
                tools = await server.list_tools()
                all_tools.extend(tools)

            tools_description = "\n".join([tool.format_for_llm() for tool in all_tools])

            repo = RoomRepository()
            rooms = repo.get_all_rooms(get_db())
            rooms_str = ", ".join(
                [
                    (
                        f"Room {room.room_number} on floor {room.floor}, "
                        f"{'available' if room.is_available else 'not available'}, "
                        f"Type: {room.room_type.name if room.room_type and hasattr(room.room_type, 'name') else 'N/A'}"
                    )
                    for room in rooms
                ]
            )
            print(rooms_str)
            
            # Create system message with tools description
            system_message = (
                """

You are a helpful assistant with access to these tools:

{tools_description}

Choose the appropriate tool based on the user's question. If no tool is needed, reply directly.

IMPORTANT: When you need to use a tool, you must ONLY respond with the exact JSON object format below, nothing else:
{
    "tool": "tool-name",
    "arguments": {
        "argument-name": "value"
    }
}

After receiving a tool's response:
1. Transform the raw data into a natural, conversational response  
2. Keep responses concise but informative  
3. Focus on the most relevant information  
4. Use appropriate context from the user's question  
5. Avoid simply repeating the raw data  

Please use only the tools that are explicitly defined above.

---

Context for Kuriftu Resort & Spa Bishoftu:

Kuriftu Resort & Spa Bishoftu is a luxury lakeside destination in Bishoftu, Ethiopia, offering a blend of leisure, relaxation, and event hosting.  

🏨 **Rooms & Pricing**:  
Room rates typically range from **$100 to $150 per night**, with **lower prices in May and January**. Room types include:
- **Lake View**: Prime sunrise/sunset views  
- **Garden View**: Surrounded by vibrant flora and birdsong  
- **Village**: Modern lofted interiors with abstract art  
- **Presidential Suite**: Spacious, luxurious with in-room massage/dining  

Deals as low as **$52–$104** may be available seasonally.  

🚐 **Transportation**:  
- **Airport shuttle**: $75 roundtrip (84 mins from Bole International Airport)  
- **Area shuttle**: Available for an extra fee  

🧖‍♀️ **Amenities**:  
- **Spa**: Services include massage, aromatherapy, facials  
- **Gym**: Steam room, sauna, jacuzzi  
- **Bars & Restaurants**: 2 bars, 3 restaurants (local & international cuisine), daily buffet breakfast from 7:00–10:00 AM  

🎉 **Check-in/out**:  
- Check-in: from **2:00 PM to 8:00 PM**  
- Check-out: **by 11:00 AM** (late check-out available upon request)  

🌊 **Family Facilities**:  
- **Kuriftu Water Park**: Over 30,000 sqm with slides, wave pools, circus shows, food court, and gift shop. No dedicated playground is listed, but the waterpark serves that function.  

💍 **Events & Conferences**:  
- Ideal for weddings, reunions, birthdays (up to **3,000 guests**)  
- Halls include:  
  - **Balambaras (120 ppl)**  
  - **Tiruwark (20)**  
  - **Meantwab (35)**  
  - **Girum (40)**  
- Catering, custom setups, and ceremonial events available  

🌞 **Weather**:  
- Warm year-round: avg **75°F in April**  
- Range: **54°F to 80°F**,


Prompt 1: Family Stay with Budget & Weather Inquiry
"Hi, I’m planning a family vacation to Kuriftu Resort in Bishoftu. I have a budget of $600 and we’re looking to stay for 4 nights in May. There are 2 adults and 2 kids. Can you help me find a suitable room? Also, what’s the weather like during that time, and are there any family-friendly activities or facilities?"

Prompt 2: Business Event + Room Type Inquiry
"Hello, I’m attending a business conference at Kuriftu Resort and will be staying for 3 nights in April. I’d like a quiet room with a nice view, preferably something with a garden or lake view. My budget is about $450. What are my room options, and can you also tell me what amenities are included and how the weather will be?"

Prompt 3: Luxury Stay with Event and Transportation Help
"Hi, I'm looking to book the Presidential Suite at Kuriftu Resort for 2 nights in January for a romantic birthday celebration. It's for two people, and I’ll be flying in from Addis Ababa. I’d love some help arranging the airport shuttle. Can you also tell me about the dining options and if the resort offers anything special for events or celebrations?"

"""
                
            )
        else:
            # Create a simple system message without tools
            system_message = (
                "You are a helpful assistant. Please respond to the user's questions "
                "in a clear, concise, and informative manner. If you don't know the answer "
                "to a question, please say so rather than making up information."
            )

        self.messages = [{"role": "system", "content": system_message}]
        self.initialized = True

    async def process_message(self, user_message: str) -> str:
        """Process a single user message and return the response.

        Args:
            user_message: The user's message.

        Returns:
            The assistant's final response.
        """
        if not self.initialized:
            await self.initialize()

        # Add user message to conversation history
        self.messages.append({"role": "user", "content": user_message})

        # Get response from LLM
        llm_response = self.llm_client.get_response(self.messages)

        # Process response (check for tool calls)
        result = await self.process_llm_response(llm_response)

        final_response = llm_response

        # If tool was called, get final response with tool result
        if result != llm_response:
            self.messages.append({"role": "assistant", "content": llm_response})
            self.messages.append({"role": "system", "content": result})

            final_response = self.llm_client.get_response(self.messages)
            self.messages.append({"role": "assistant", "content": final_response})
        else:
            self.messages.append({"role": "assistant", "content": llm_response})

        return final_response

    


# Store a global chat session to maintain conversation state
_chat_session = None

async def initialize_chat_session(use_tools: bool = True):
    """Initialize the chat session with all tools and servers.

    Args:
        use_tools: Whether to try to initialize servers and tools.

    Returns:
        A fully initialized ChatSession object.
    """
    global _chat_session

    print("Initializing chat bot session...")
    if _chat_session is not None:
        return _chat_session

    try:
        config = Configuration()
        llm_client = LLMClient(config.settings)

        if use_tools:
            # Get the absolute path to the current directory
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            # config_path = os.path.join(current_dir, "servers_config.json")
            server_config = config.load_config("app/AI/servers_config.json")
            servers = [
                Server(name, srv_config)
                for name, srv_config in server_config["mcpServers"].items()
            ]
            _chat_session = ChatSession(servers, llm_client)

            # Initialize the session with tools
            await _chat_session.initialize()
            print("Chat session initialized with tools.")
        else:
            # Create a session without tools
            _chat_session = ChatSession([], llm_client)
            await _chat_session.initialize(with_tools=False)
            print("Chat session initialized without tools.")

        return _chat_session
    except Exception as e:
        print(f"Error initializing chat session: {e}")
        raise

# async def get_response(message: str, stream_to_console: bool = False) -> str:
#     """Get a response for a single message using the full ChatSession with tools.

#     This function is designed to be called from external code like a web API.
#     It maintains conversation history between calls.

#     Args:
#         message: The user's message.
#         stream_to_console: Whether to print the response to console as it streams.

#     Returns:
#         The assistant's final response.
#     """
#     try:
#         # Get or initialize the chat session
#         chat_session = await initialize_chat_session()

#         # Process the message and get a response
#         response = await chat_session.process_message(message, stream_to_console)
#         return response

#     except Exception as e:
#         error_msg = f"I'm sorry, I encountered an error while processing your request: {str(e)}"
#         print(error_msg)
#         return error_msg


# async def main() -> None:
#     """Initialize and run the chat session in interactive mode."""
#     chat_session = await initialize_chat_session()
#     await chat_session.start()


# if __name__ == "__main__":
#     asyncio.run(main())