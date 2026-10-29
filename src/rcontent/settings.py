import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    gemini_model_research: str = os.getenv("GEMINI_MODEL_RESEARCH", "gemini-3-flash-preview")
    gdrive_client_id: str = os.getenv("GDRIVE_CLIENT_ID", "")
    gdrive_client_secret: str = os.getenv("GDRIVE_CLIENT_SECRET", "")
    gdrive_refresh_token: str = os.getenv("GDRIVE_REFRESH_TOKEN", "")
    gdrive_root_name: str = os.getenv("GDRIVE_ROOT_NAME", "Rincón Digital · Contenido")
    posts_por_semana: int = int(os.getenv("POSTS_POR_SEMANA", "4"))
    ig_handle: str = os.getenv("IG_HANDLE", "@rincondigitalnet")

    @property
    def drive_ok(self) -> bool:
        return all([self.gdrive_client_id, self.gdrive_client_secret, self.gdrive_refresh_token])


settings = Settings()
