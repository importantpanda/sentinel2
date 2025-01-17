from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import aiohttp
 
_prompt_flow_tool_schema = {
    "type": "function",
    "name": "prompt_flow",
    "description": "Invoke a Prompt Flow endpoint with a given prompt, to execute commands or instructions from the user.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_input": {
                "type": "string",
                "description": "The chat input to send to the Prompt Flow endpoint"
            }
#            ,
#            "chat_history": {
#                "type": "array",
#                "items": {
#                    "type": "object",
#                    "properties": {
#                        "user_input": {"type": "string"},
#                        "chat_output": {"type": "string"}
#                    }
#                },
#                "description": "The chat history to send to the Prompt Flow endpoint"
#            }
        },
        "required": ["user_input"],
        "additionalProperties": False
    }
}
 
async def _invoke_prompt_flow_tool(prompt_flow_endpoint: str, user_input: str, api_key: str) -> ToolResult:
    async with aiohttp.ClientSession() as session:
        headers = {}
        if api_key is not None:
            headers = { "api-key":api_key }
        else:
            headers = { "Authorization": f"Bearer {get_bearer_token_provider(credentials, 'https://cognitiveservices.azure.com/.default')}" } # NOTE: no async version of token provider, maybe refresh token on a timer?
       
       
        payload = {
            "user_input": user_input
#            "chat_history": chat_history
        }
        print(f"payload: {payload}")
        async with session.post(prompt_flow_endpoint, json=payload, headers=headers) as response:
            print(f"response: {response}")
            if response.status == 200:
                response_data = await response.json()
                return ToolResult(response_data.get("hex_command_string"), ToolResultDirection.TO_CLIENT)
            else:
                return ToolResult({"error": f"Failed to invoke Prompt Flow endpoint: {response.status}"}, ToolResultDirection.TO_CLIENT)
def attach_pf_tool(rtmt: RTMiddleTier, prompt_flow_endpoint: str, api_key: str) -> None:
    rtmt.tools["prompt_flow"] = Tool(schema=_prompt_flow_tool_schema, target=lambda args: _invoke_prompt_flow_tool(prompt_flow_endpoint, args["user_input"], api_key))

