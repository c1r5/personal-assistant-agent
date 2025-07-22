from google.adk.sessions.session import Session
from agents.agent import root_agent


from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent
import logging


APP_NAME = "Personal Assistant"

logger = logging.getLogger(__name__)

class AgentClient:
    __sessions: dict[str, Session] = {}

    def __init__(self):
        self.__runner = InMemoryRunner(app_name=APP_NAME, agent=root_agent)

    async def create_session(self, user_id: str):
        logger.info("Starting session")
        session = await self.__runner.session_service.create_session(app_name=APP_NAME, user_id=user_id)
        self.__sessions[user_id] = session
        return session

    async def delete_session(self, user_id: str):
        logger.info("Stopping session")
        await self.__runner.session_service.delete_session(app_name=APP_NAME, session_id=self.__sessions[user_id].id, user_id=user_id)

    async def request(self, user_id: str, message: str):
        session = self.__sessions.get(user_id)

        if not session:
            logger.warning("Session not started")
            return

        try:
            logger.info("Requesting response")

            async for response in self.__runner.run_async(user_id=user_id, session_id=session.id, new_message=UserContent(message)):
                if not response.is_final_response():
                    continue

                if response.content is None:
                    logger.warning("Não foi possivel gerar a resposta")
                    continue

                if response.content.parts is None or []: # type: ignore
                    logger.warning("Não foi possivel obter o conteudo da resposta")
                    continue

                yield '\n'.join([part.text for part in response.content.parts])   # type: ignore
        except Exception as e:
            logger.error("Um erro ocorreu ao tentar gerar resposta", exc_info=e)
