import logging
import os
from pathlib import Path

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

# from ragtools import attach_rag_tools
from rtmt import RTMiddleTier
from pf_tool import attach_pf_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv(override=True)

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
#    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
#    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = "You are a helpful assistant. The user is listening to answers with audio. Use the following step-by-step instructions to respond: " + \
                          "Step 1 - Always use the 'prompt_flow' tool to execute commands and instructions from the user. " + \
                          "Step 2 - Respond back with the exact response received from the prompt_flow tool. " + \
                          "Only respond with the prompt flow response. Do not add any additional information. "

#    attach_rag_tools(rtmt,
#        credentials=search_credential,
#        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
#        search_index=os.environ.get("AZURE_SEARCH_INDEX"),
#        semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or "default",
#        identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
#        content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
#        embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
#        title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
#        use_vector_query=(os.environ.get("AZURE_SEARCH_USE_VECTOR_QUERY") == "true") or True)
    attach_pf_tool(rtmt, os.environ.get("PROMPT_FLOW_ENDPOINT"), os.environ.get("PROMPT_FLOW_API_KEY"))

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    app.router.add_static('/', path=current_directory / 'static', name='static')
    
    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)