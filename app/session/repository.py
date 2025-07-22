from typing import Callable
from typing import Awaitable
from typing_extensions import Literal
from pydantic import BaseModel
from typing import Optional

SessionID = str
Data = str


class SessionEvent(BaseModel):
    type: Literal["created", "deleted"] = "created"
    session_id: SessionID
    data: Optional[Data] = None


SessionEventListener = Callable[[SessionEvent], Awaitable[None]]


class ClientSession:
    __on_reply: Optional[Callable[[Data], Awaitable[None]]] = None
    __on_message: Optional[Callable[[str, SessionID], Awaitable[None]]] = None

    def __init__(self, session_id: str):
        self.session_id = session_id

    def add_on_reply_listener(self, callback: Callable[[Data], Awaitable[None]]):
        self.__on_reply = callback

    def remove_on_reply_listener(self):
        self.__on_reply = None

    def add_on_message_listener(
        self, callback: Callable[[str, SessionID], Awaitable[None]]
    ):
        self.__on_message = callback

    async def __reply(self, data: Data):
        if self.__on_reply:
            await self.__on_reply(data)

    async def send_message(self, message: str):
        await self.__reply(message)

    async def on_message(self, message: str):
        if self.__on_message:
            await self.__on_message(message, self.session_id)


class SessionRepository:
    __listeners: list[SessionEventListener] = []

    def __init__(self):
        self.sessions = {}

    async def create_session(self, session_id: str) -> ClientSession:
        if self.sessions.get(session_id) is None:
            session = ClientSession(session_id)
            self.sessions[session_id] = session
            await self.notify_listeners(SessionEvent(session_id=session_id))
            return session
        else:
            return self.sessions[session_id]

    async def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            await self.notify_listeners(
                SessionEvent(session_id=session_id, type="deleted")
            )

    async def get_session(self, session_id: str) -> Optional[ClientSession]:
        return self.sessions.get(session_id)

    async def notify_listeners(self, event: SessionEvent):
        for listener in self.__listeners:
            await listener(event)

    def add_listener(self, listener: SessionEventListener):
        self.__listeners.append(listener)

    def remove_listener(self, listener: SessionEventListener):
        self.__listeners.remove(listener)
