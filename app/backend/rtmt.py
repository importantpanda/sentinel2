import asyncio
import json
import logging
import os
from enum import Enum
from typing import Any, Callable, Optional

import aiohttp
from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, AzureDeveloperCliCredential
from dotenv import load_dotenv

logger = logging.getLogger("voicerag")

# Load environment variables from .env file
load_dotenv()

class ToolResultDirection(Enum):
    TO_SERVER = 1
    TO_CLIENT = 2

class ToolResult:
    text: str
    destination: ToolResultDirection

    def __init__(self, text: str, destination: ToolResultDirection):
        self.text = text
        self.destination = destination

    def to_text(self) -> str:
        return self.text

class RTMiddleTier:
    def __init__(self, credentials: AzureKeyCredential, endpoint: str, deployment: str, voice_choice: str):
        self.credentials = credentials
        self.endpoint = endpoint
        self.deployment = deployment
        self.voice_choice = voice_choice
        self.system_message = ""

    async def handle_request(self, request: web.Request) -> web.Response:
        data = await request.json()
        logger.info("Received request: %s", data)
        # Process the request and return a response
        response_data = {"message": "Request processed"}
        return web.json_response(response_data)

    def attach_to_app(self, app: web.Application, path: str):
        app.router.add_post(path, self.handle_request)

# Load Azure resources from environment variables
llm_key = os.getenv("AZURE_OPENAI_API_KEY")
search_key = os.getenv("AZURE_SEARCH_API_KEY")

credential = None
if not llm_key or not search_key:
    if tenant_id := os.getenv("AZURE_TENANT_ID"):
        credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
    else:
        credential = DefaultAzureCredential()
llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
search_credential = AzureKeyCredential(search_key) if search_key else credential

# Example usage of RTMiddleTier
rtmt = RTMiddleTier(
    credentials=llm_credential,
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment=os.getenv("AZURE_OPENAI_REALTIME_DEPLOYMENT"),
    voice_choice=os.getenv("AZURE_OPENAI_REALTIME_VOICE_CHOICE", "alloy")
)