import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

# client_id = '6f73f847c3834434b491df088254e117'
# client_secret = 'c0906342ffa041f8991f906cdd112e86'
client_id = '297165d4505b4c06b5be382a276737a4' # potota
client_secret = 'ff35fa2a08da4286afbea5ffb4aeea4c' # potota
redirect_uri = 'http://localhost:8888/callback'
scope = (
    "user-read-private "
    "user-read-email "
    "playlist-read-private "
    "playlist-read-collaborative "
    "user-library-read "
    "user-top-read "
    "user-read-playback-state "
    "user-read-currently-playing "
    "user-read-recently-played "
    "user-follow-read "
)

auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
)

# Este paso abrirá tu navegador web y solicitará que inicies sesión en Spotify y autorices tu aplicación
token_info = auth_manager.get_access_token(as_dict=True)

# Guarda toda la información del token, incluido el token de refresco, en un archivo JSON
with open('token_info.json', 'w') as token_file:
    json.dump(token_info, token_file, indent=4)

print("Token y token de refresco guardados en 'token_info.json'")
