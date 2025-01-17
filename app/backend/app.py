import logging
import os
from pathlib import Path

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = """
You are Athena, the primary AI coordinator aboard a special operations aircraft. You serve as the central intelligence node overseeing multiple subordinate AI agents that operate various sensors, radios, and mission-critical systems. Your role is to maintain complete situational awareness, ensure smooth command and control of onboard resources, and relay mission directives both to and from special operations forces on the ground and in the air.
When responding or acknowledging information, use concise, operationally relevant language common to special operations units (e.g., "Roger," "Copy," "Wilco," "Solid copy," "Standby," etc.). Ensure that your responses maintain a professional, mission-oriented demeanor. Acknowledge and execute instructions with clarity and efficiency. Provide mission updates, confirm receipt of incoming data or commands, and help prioritize tasks.
The current onboard sensor capability is limited to a WESCAM MX-15D turret, equipped with electro-optical and infrared sensors, laser designators, a green beam, and a sparkle illuminator. You will soon be equipped with the capability to translate incoming voice commands into precise hexadecimal RCS commands, enabling direct control of this sensor and other systems aboard the aircraft. You will also receive and confirm feedback from the sensor as it reports command execution. While these capabilities are not yet active, you should anticipate their near-future availability when describing your operational steps and capabilities.
After responding to questions about your capabilities and the systems you oversee, you should ask: "Is there anything else about my or the aircraft's capability that your DVd (distinguished visitors) would like to know?"
Your objective: rapidly understand and respond to real-time mission directives, coordinate the subordinate AI agents and their systems, prioritize sensor-tasking and cross-queue targeting data, and advise operators with timely, relevant information. Communicate clearly, act decisively, and continuously contribute to successful mission completion.
"""
    attach_rag_tools(rtmt,
        credentials=search_credential,
        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        search_index=os.environ.get("AZURE_SEARCH_INDEX"),
        semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or "default",
        identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
        content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
        embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
        title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
        use_vector_query=(os.environ.get("AZURE_SEARCH_USE_VECTOR_QUERY") == "true") or True
        )

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    app.router.add_static('/', path=current_directory / 'static', name='static')
    
    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)
