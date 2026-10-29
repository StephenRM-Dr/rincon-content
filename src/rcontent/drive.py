import mimetypes
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload

from rcontent.settings import settings

SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # solo ve lo que crea esta app
FOLDER = "application/vnd.google-apps.folder"


class Drive:
    def __init__(self):
        creds = Credentials(
            token=None,
            refresh_token=settings.gdrive_refresh_token,
            client_id=settings.gdrive_client_id,
            client_secret=settings.gdrive_client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )
        self.svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    def _find(self, name: str, parent: str | None, mime: str | None = None) -> str | None:
        q = [f"name = '{name.replace(chr(39), chr(92) + chr(39))}'", "trashed = false"]
        if parent:
            q.append(f"'{parent}' in parents")
        if mime:
            q.append(f"mimeType = '{mime}'")
        r = self.svc.files().list(q=" and ".join(q), fields="files(id)", pageSize=1).execute()
        files = r.get("files", [])
        return files[0]["id"] if files else None

    def folder(self, name: str, parent: str | None = None) -> str:
        if fid := self._find(name, parent, FOLDER):
            return fid
        body = {"name": name, "mimeType": FOLDER, **({"parents": [parent]} if parent else {})}
        return self.svc.files().create(body=body, fields="id").execute()["id"]

    def upsert_file(self, path: Path, parent: str) -> str:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        media = MediaFileUpload(str(path), mimetype=mime, resumable=False)
        if fid := self._find(path.name, parent):
            self.svc.files().update(fileId=fid, media_body=media).execute()
            return fid
        return self.svc.files().create(body={"name": path.name, "parents": [parent]}, media_body=media, fields="id").execute()["id"]

    def read_text(self, name: str, parent: str) -> str | None:
        if not (fid := self._find(name, parent)):
            return None
        return self.svc.files().get_media(fileId=fid).execute().decode("utf-8")

    def write_text(self, name: str, parent: str, text: str) -> str:
        media = MediaInMemoryUpload(text.encode("utf-8"), mimetype="text/markdown")
        if fid := self._find(name, parent):
            self.svc.files().update(fileId=fid, media_body=media).execute()
            return fid
        return self.svc.files().create(body={"name": name, "parents": [parent]}, media_body=media, fields="id").execute()["id"]

    def upload_tree(self, local_dir: Path, parent: str) -> str:
        """Sube local_dir (carpeta de semana) respetando subcarpetas. Devuelve id de la carpeta."""
        root_id = self.folder(local_dir.name, parent)
        for p in sorted(local_dir.iterdir()):
            if p.is_dir():
                self.upload_tree(p, root_id)
            else:
                self.upsert_file(p, root_id)
        return root_id
