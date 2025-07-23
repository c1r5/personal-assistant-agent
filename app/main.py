import os

from pydantic import ValidationError
from uvicorn import Config, Server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import ConnectorRequest, AgentResponse
from session.repository import SessionEvent
from server.controllers import controller, session_repository
from agents.client import AgentClient

import signal
import asyncio
import logging

__import__("dotenv").load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI()
agent = AgentClient()


# Porta do servico
def get_service_port() -> int:
    return int(os.getenv("SERVICE_PORT", "8000"))


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(controller)


async def on_session_message(message: str, session_id: str):
    logger.info(f"Received message: {message}")

    session = await session_repository.get_session(session_id)

    if session is None:
        logger.error(f"Session not found: {session_id}")
        return

    try:
        client_message = ConnectorRequest.model_validate_json(message)
        async for raw_agent_response in agent.request(
            session_id, client_message.content
        ):
            parsed_agent_response = AgentResponse(content=raw_agent_response.strip())

            await session.send_message(parsed_agent_response.model_dump_json())

    except ValidationError as e:
        logger.error(f"Invalid message: {message}", exc_info=e)
        return


async def on_create_session(session_id: str):
    session = await session_repository.get_session(session_id)

    if session is None:
        logger.error(f"Session not found: {session_id}")
        return

    session.add_on_message_listener(on_session_message)


async def on_delete_session(session_id: str):
    await agent.delete_session(session_id)


async def session_event_listener(event: SessionEvent):
    match event.type:
        case "created":
            await on_create_session(event.session_id)
            await agent.create_session(event.session_id)

        case "deleted":
            await on_delete_session(event.session_id)
        case _:
            logger.warning(f"Unknown event type: {event.type}")


async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    server = None

    session_repository.add_listener(session_event_listener)

    async def shutdown():
        logger.info("Shutting down...")
        if server:
            logger.info("Stopping server...")
            await server.shutdown()
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    config = Config(
        app=app,
        host="0.0.0.0",
        port=get_service_port(),
        log_level="info",
        loop="asyncio",
    )
    server = Server(config)
    server_task = asyncio.create_task(server.serve())

    try:
        await stop_event.wait()
        logger.info("Stop event received")

        await asyncio.wait_for(server_task, timeout=5.0)
        logger.info("Server stopped gracefully")
    except asyncio.TimeoutError:
        logger.warning("Server shutdown timed out, forcing exit")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    finally:
        await asyncio.sleep(0.1)  # Give pending tasks a chance to complete
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="logs/app.log",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
