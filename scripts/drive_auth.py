"""Obtiene el GDRIVE_REFRESH_TOKEN una sola vez (correr en tu PC).

1. Google Cloud Console → APIs & Services → habilita "Google Drive API".
2. OAuth consent screen: External, agrega tu correo como test user y luego "Publish app"
   (en modo Testing el refresh token caduca a los 7 días; drive.file no requiere verificación).
3. Credentials → Create OAuth client ID → Desktop app → descarga como client_secret.json.
4. python scripts/drive_auth.py client_secret.json
"""
import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

path = sys.argv[1] if len(sys.argv) > 1 else "client_secret.json"
flow = InstalledAppFlow.from_client_secrets_file(path, SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
cfg = json.load(open(path))["installed"]

print("\nAgrega esto a .env y a los secrets del repo:\n")
print(f"GDRIVE_CLIENT_ID={cfg['client_id']}")
print(f"GDRIVE_CLIENT_SECRET={cfg['client_secret']}")
print(f"GDRIVE_REFRESH_TOKEN={creds.refresh_token}")
