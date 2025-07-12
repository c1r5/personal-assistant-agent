import logging
import json
import asyncio
import random
import warnings

from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
)

from fastapi import FastAPI, WebSocket

from google.adk.runners import InMemoryRunner
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

from multi_tool_agent.agent import root_agent


warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

load_dotenv()

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="(%(asctime)s) %(levelname)s %(message)s",
    datefmt="%m/%d/%y - %H:%M:%S %Z",
)

logger = logging.getLogger(__name__)

APP_NAME = "Personal Assistant Agent"


async def start_agent_session(user_id):
    """Starts an agent session"""

    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # Replace with actual user ID
    )

    # Set response modality
    modality = "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    while True:
        async for event in live_events:
            # If the turn complete or interrupted, send it
            if event.turn_complete or event.interrupted:
                message = f"Turn complete: {event.turn_complete}, Interrupted: {event.interrupted}"
                logger.info(message)
                await websocket.send_text(message)
                continue

            # Read the Content and its first Part
            part: Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            
            if not part:
                continue
            
            if part.text and event.partial:
                await websocket.send_text(part.text)


async def client_to_agent_messaging(websocket, live_request_queue):
    """Client to agent communication"""
    while True:
        # Decode JSON message
        message = await websocket.receive_text()
        # Send the message to the agent
        content = Content(role="user", parts=[Part.from_text(text=message)])
        live_request_queue.send_content(content=content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    user_id = str(random.randint(1000000, 9999999))
    live_events, live_request_queue = await start_agent_session(user_id)

        # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # Wait until the websocket is disconnected or an error occurs
    tasks = [agent_to_client_task, client_to_agent_task]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # Close LiveRequestQueue
    live_request_queue.close()