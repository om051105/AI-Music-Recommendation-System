from dotenv import load_dotenv
import os

load_dotenv(override=True)

cid = os.getenv("SPOTIFY_CLIENT_ID")
secret = os.getenv("SPOTIFY_CLIENT_SECRET")

print(f"Loaded Client ID: '{cid}'")
print(f"Loaded Secret Length: {len(secret) if secret else 0}")
print(f"First 4 chars of Secret: {secret[:4] if secret else 'None'}")
