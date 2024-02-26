from get_user_data import SpotifySingleUser
import time
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

import time
from spotify_interface import SpotifyInterface  # Asegúrate de importar correctamente SpotifyInterface


class SpotifyProxy:
    def __init__(self, client_id, client_secret, redirect_uri, cache_path):
        self.interface = SpotifyInterface()
        self.auth_manager = spotipy.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=(
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
            ),
            cache_handler=CacheFileHandler(cache_path=cache_path)
        )

    def _retry_with_backoff(self, token, id_user):
        backoff_time = 1  # Comienza con 1 segundo
        max_backoff_time = 60  # Máximo tiempo de espera

        while True:
            status = self.interface.handle_request(token, id_user)
            if status == 200:
                return "Ejecutado correctamente"
            elif status == 429:
                # Rate limit error, espera y reintenta
                time.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, max_backoff_time)
            elif status == 401:
                # Token caducado, renueva y reintenta
                token_info = self.auth_manager.refresh_access_token(
                    self.auth_manager.get_cached_token()['refresh_token'])
                token = token_info['access_token']  # Actualiza el token
                self.auth_manager.cache_handler.save_token_to_cache(token_info)  # Guarda el nuevo token
                # No es necesario esperar después de refrescar el token, ya que se supone que el nuevo token es válido inmediatamente
                # Sin embargo, se recomienda añadir un pequeño delay si se encuentra con problemas de sincronización
                time.sleep(1)
                # Vuelve a intentar la petición con el nuevo token
                continue  # Esto hace que el bucle vuelva a empezar, reintentando la petición con el nuevo token
            else:
                return f"Error: {status}"

    def handle_requests(self, token, id_user, requests):
        # Envuelve la llamada al interfaz con la lógica de reintento
        return self.interface.handle_requests(token, id_user, requests)


if __name__ == '__main__':
    import json

    # Ruta del archivo JSON que contiene el token y el token de refresco
    token_file = './tokens/spotify_tokens.json'
    client_id = '6f73f847c3834434b491df088254e117'
    client_secret = 'c0906342ffa041f8991f906cdd112e86'
    redirect_uri = 'http://localhost:8888/callback'
    token_file = './tokens/spotify_tokens.json'
    cache_path = token_file
    requests = ["get_user_profile", "get_recently_played_tracks", "get_top_artists"]


    def leer_token(archivo_token):
        with open(archivo_token, 'r') as archivo:
            token_info = json.load(archivo)
        return token_info['access_token'], token_info['refresh_token']

    with open(token_file, 'r') as file:
        token_info = json.load(file)
    token = token_info['access_token']
    id_user = 'un_user_molon'

    # Instanciar SpotifyProxy
    spotify_proxy = SpotifyProxy(client_id, client_secret, redirect_uri, cache_path)

    # Llamar al método handle_request del proxy con el token y el id_user
    results = spotify_proxy.handle_requests(token, id_user, requests)

    print(results)