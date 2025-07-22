import os
import sys
from importlib import reload
from types import ModuleType
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def test_service_port_env_var_is_used(monkeypatch):
    accessed = {}

    def fake_getenv(name, default=None):
        accessed['name'] = name
        return '1234'

    monkeypatch.setattr(os, 'getenv', fake_getenv)
    stub = ModuleType('stub')
    stub.load_dotenv = lambda: None
    sys.modules['dotenv'] = stub
    sys.modules['pydantic'] = ModuleType('pydantic')
    sys.modules['pydantic'].ValidationError = Exception
    sys.modules['uvicorn'] = ModuleType('uvicorn')
    sys.modules['uvicorn'].Config = object
    sys.modules['uvicorn'].Server = object
    fastapi_stub = ModuleType('fastapi')
    class _FastAPI:
        def add_middleware(self, *a, **k):
            pass
        def include_router(self, *a, **k):
            pass
    fastapi_stub.FastAPI = _FastAPI
    sys.modules['fastapi'] = fastapi_stub
    middleware_module = ModuleType('fastapi.middleware.cors')
    middleware_module.CORSMiddleware = object
    sys.modules['fastapi.middleware'] = ModuleType('fastapi.middleware')
    sys.modules['fastapi.middleware.cors'] = middleware_module
    sys.modules['models'] = ModuleType('models')
    sys.modules['models'].ConnectorRequest = object
    sys.modules['models'].AgentResponse = object
    sys.modules['session.repository'] = ModuleType('session.repository')
    sys.modules['session.repository'].SessionEvent = object
    sys.modules['server.controllers'] = ModuleType('server.controllers')
    sys.modules['server.controllers'].controller = object
    sys.modules['server.controllers'].session_repository = object
    sys.modules['agents.client'] = ModuleType('agents.client')
    sys.modules['agents.client'].AgentClient = object
    from app import main
    reload(main)
    assert main.get_service_port() == 1234
    assert accessed.get('name') == 'SERVICE_PORT'
