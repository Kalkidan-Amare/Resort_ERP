import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any
from app.config.env import get_settings
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


class Configuration:
    """Manages configuration and environment variables for the MCP client."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.settings = get_settings()

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
        try:
            # Get the command to execute
            command = (
                shutil.which("npx")
                if self.config["command"] == "npx"
                else self.config["command"]
            )
            if command is None:
                raise ValueError("The command must be a valid string and cannot be None.")

            # Check if the script exists if it's a path
            if "args" in self.config and len(self.config["args"]) > 0:
                script_path = self.config["args"][0]
                if script_path.endswith(".py") and not os.path.isfile(script_path):
                    # Try to find the script relative to the current directory
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                    alternative_path = os.path.join(project_root, script_path)

                    if os.path.isfile(alternative_path):
                        # Update the path to the absolute path
                        self.config["args"][0] = alternative_path
                    else:
                        print(f"Warning: Script not found at {script_path} or {alternative_path}")

            # Create server parameters
            server_params = StdioServerParameters(
                command=command,
                args=self.config["args"],
                env={**os.environ, **self.config["env"]}
                if self.config.get("env")
                else None,
            )

            # Initialize the server
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.session = session
            print(f"Server {self.name} initialized successfully.")
        except Exception as e:
            print(f"Error initializing server {self.name}: {e}")
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
        self.token = settings.token
        self.endpoint = settings.endpoint
        self.model_name = settings.model_name

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

            # Create system message with tools description
            system_message = (
                "You are a helpful assistant with access to these tools:\n\n"
                f"{tools_description}\n"
                "Choose the appropriate tool based on the user's question. "
                "If no tool is needed, reply directly.\n\n"
                "IMPORTANT: When you need to use a tool, you must ONLY respond with "
                "the exact JSON object format below, nothing else:\n"
                "{\n"
                '    "tool": "tool-name",\n'
                '    "arguments": {\n'
                '        "argument-name": "value"\n'
                "    }\n"
                "}\n\n"
                "After receiving a tool's response:\n"
                "1. Transform the raw data into a natural, conversational response\n"
                "2. Keep responses concise but informative\n"
                "3. Focus on the most relevant information\n"
                "4. Use appropriate context from the user's question\n"
                "5. Avoid simply repeating the raw data\n\n"
                "Please use only the tools that are explicitly defined above."
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

    async def start(self) -> None:
        """Main chat session handler for interactive mode."""
        # logging.info("Starting chat session...")
        try:
            await self.initialize()

            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() in ["quit", "exit"]:
                        # logging.info("\nExiting...")
                        break

                    response = await self.process_message(user_input)

                    # Response is already printed if stream_to_console=True
                    # If we didn't stream, print the response now
                    print(f"\nAssistant: {response}")

                except KeyboardInterrupt:
                    # logging.info("\nExiting...")
                    break

        finally:
            await self.cleanup_servers()


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

    if _chat_session is not None:
        return _chat_session

    try:
        config = Configuration()
        llm_client = LLMClient(config.settings)

        if use_tools:
            try:
                # Get the absolute path to the current directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(current_dir, "servers_config.json")
                server_config = config.load_config(config_path)
                servers = [
                    Server(name, srv_config)
                    for name, srv_config in server_config["mcpServers"].items()
                ]
                _chat_session = ChatSession(servers, llm_client)

                # Initialize the session with tools
                await _chat_session.initialize()
                print("Chat session initialized with tools.")
            except Exception as e:
                print(f"Warning: Could not initialize tools: {e}")
                print("Falling back to basic chat without tools.")
                _chat_session = ChatSession([], llm_client)
                await _chat_session.initialize(with_tools=False)
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


async def main() -> None:
    """Initialize and run the chat session in interactive mode."""
    chat_session = await initialize_chat_session()
    await chat_session.start()


if __name__ == "__main__":
    asyncio.run(main())