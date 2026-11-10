from fastapi import FastAPI

from .config import get_setting, Settings
from .dependencies import get_db
from .database import make_session_factory

def create_app(settings: Settings):
    app = FastAPI()
    app.state.settings = settings
    
    engine, session_factory = make_session_factory(settings.database_url)
    app.state.engine = engine
    app.state.session_factory = session_factory

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app(get_setting())