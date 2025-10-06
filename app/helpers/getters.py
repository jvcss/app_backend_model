from app.core.config import settings

def isDebugMode() -> bool:
    return settings.MODE.lower() == "development"
