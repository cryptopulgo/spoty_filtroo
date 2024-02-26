import json
import spotipy
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


class SpotifySingleUser:
    """
    Clase para interactuar con la API de Spotify utilizando el módulo spotipy.
    Permite obtener varios datos del usuario de Spotify, como perfil, playlists,
    artistas seguidos, pistas guardadas y más.
    """

    def __init__(self, access_token):
        self.sp = spotipy.Spotify(auth=access_token)

    def get_user_profile(self):
        try:
            data = self.sp.current_user()  # Obtiene los datos del perfil del usuario
            return 200, data  # Devuelve el estado 200 y los datos si la llamada es exitosa
        except spotipy.SpotifyException as e:
            return e.http_status, {}  # Devuelve el código de estado HTTP del error y un diccionario vacío

    def get_followed_artists(self, limit=None):
        """
        Obtiene los artistas seguidos por el usuario.

        Args:
            limit: Opcional; el número máximo de artistas a retornar. Si no se especifica, se intentará obtener todos.

        Returns:
            status: Estado HTTP de la respuesta.
            data: Una lista de diccionarios, cada uno representando un artista seguido.
        """
        followed_artists = []
        after = None  # Cursor para la paginación

        try:
            while True:
                batch_limit = min(limit, 50) if limit else 50
                results = self.sp.current_user_followed_artists(limit=batch_limit, after=after)
                followed_artists.extend(results['artists']['items'])

                if limit:
                    limit -= len(results['artists']['items'])

                if not results['artists']['next'] or (limit is not None and limit <= 0):
                    break

                after = results['artists']['items'][-1]['id']

            return 200, followed_artists  # Devuelve estado 200 y los artistas seguidos

        except spotipy.SpotifyException as e:
            return e.http_status, []  # Devuelve el código de estado HTTP del error y una lista vacía

    def get_user_playlists(self, limit=None):
        """
        Obtiene las playlists del usuario.

        Args:
            limit: Opcional; el número máximo de playlists a retornar. Si no se especifica, se intentará obtener todas.

        Returns:
            status: Estado HTTP de la respuesta.
            data: Una lista de diccionarios, cada uno representando una playlist del usuario.
        """
        user_playlists = []
        offset = 0  # Desplazamiento para la paginación

        try:
            while True:
                batch_limit = min(limit, 50) if limit else 50
                results = self.sp.current_user_playlists(limit=batch_limit, offset=offset)
                user_playlists.extend(results['items'])
                offset += len(results['items'])

                if limit:
                    limit -= len(results['items'])

                if len(results['items']) < batch_limit or (limit is not None and limit <= 0):
                    break

            return 200, user_playlists  # Devuelve estado 200 y la lista de playlists si la llamada es exitosa

        except spotipy.SpotifyException as e:
            return e.http_status, []  # Devuelve el código de estado HTTP del error y una lista vacía

    def get_recently_played_tracks(self, limit=50, after=None, before=None):
        """
        Obtiene las pistas reproducidas recientemente por el usuario.

        Args:
            limit: El número máximo de pistas a retornar.
            after: Opcional; timestamp de Unix en milisegundos para obtener pistas reproducidas después de esta fecha.
            before: Opcional; timestamp de Unix en milisegundos para obtener pistas reproducidas antes de esta fecha.

        Returns:
            status: Estado HTTP de la respuesta.
            data: Una lista de pistas reproducidas recientemente.
        """
        try:
            data = self.sp.current_user_recently_played(limit=limit, after=after, before=before)
            return 200, data['items'] if 'items' in data else []  # Devuelve estado 200 y los datos si la llamada es exitosa

        except spotipy.SpotifyException as e:
            return e.http_status, []  # Devuelve el código de estado HTTP del error y una lista vacía

    def get_currently_playing(self, market=None, additional_types=None):
        """
        Obtiene información sobre la pista o episodio que se está reproduciendo actualmente en el dispositivo activo del usuario.

        Args:
            market: Opcional; un código de país ISO 3166-1 alpha-2 para garantizar que la pista esté disponible en ese mercado.
            additional_types: Opcional; una lista de tipos de contenido adicionales para incluir en la respuesta, como 'episode'.

        Returns:
            status: Estado HTTP de la respuesta.
            data: Un diccionario con información sobre el contenido actualmente en reproducción.
        """
        try:
            data = self.sp.currently_playing(market=market, additional_types=additional_types)
            if data:  # Verifica si se obtuvieron datos
                return 200, data  # Devuelve estado 200 y los datos si la llamada es exitosa
            else:
                return 204, {}  # Devuelve estado 204 (No Content) y un diccionario vacío si no hay contenido en reproducción
        except spotipy.SpotifyException as e:
            return e.http_status, {}  # Devuelve el código de estado HTTP del error y un diccionario vacío

    def get_saved_albums(self, limit=20, offset=0, market=None):
        """
        Obtiene los álbumes guardados en la biblioteca del usuario.

        Args:
            limit: El número máximo de álbumes a retornar.
            offset: El índice del primer álbum a retornar.
            market: Opcional; un código de país ISO 3166-1 alpha-2 para garantizar que el álbum esté disponible en ese mercado.

        Returns:
            status: Estado HTTP de la respuesta.
            data: Una lista de álbumes guardados en la biblioteca del usuario.
        """
        try:
            data = self.sp.current_user_saved_albums(limit=limit, offset=offset, market=market)
            return 200, data['items'] if 'items' in data else []  # Devuelve estado 200 y los datos si la llamada es exitosa
        except spotipy.SpotifyException as e:
            return e.http_status, []  # Devuelve el código de estado HTTP del error y una lista vacía

    def get_saved_tracks(self, limit=20, offset=0, market=None):
        """
        Obtiene las pistas guardadas en la biblioteca del usuario.

        Args:
            limit: El número máximo de pistas a retornar.
            offset: El índice de la primera pista a retornar.
            market: Opcional; un código de país ISO 3166-1 alpha-2 para garantizar que la pista esté disponible en ese mercado.

        Returns:
            status: Estado HTTP de la respuesta.
            data: Una lista de pistas guardadas en la biblioteca del usuario.
        """
        try:
            data = self.sp.current_user_saved_tracks(limit=limit, offset=offset, market=market)
            return 200, data['items'] if 'items' in data else []  # Devuelve estado 200 y los datos si la llamada es exitosa
        except spotipy.SpotifyException as e:
            return e.http_status, []  # Devuelve el código de estado HTTP del error y una lista vacía

    def get_top_artists(self, limit=20, offset=0, time_range='medium_term'):
        """
        Obtiene los artistas más escuchados por el usuario en un rango de tiempo determinado.

        Args:
            limit: El número máximo de artistas a retornar.
            offset: El índice del primer artista a retornar.
            time_range: El rango de tiempo para los datos ('short_term', 'medium_term', 'long_term').

        Returns:
            status: Estado HTTP de la respuesta.
            data: Una lista de los artistas más escuchados por el usuario.
        """
        try:
            data = self.sp.current_user_top_artists(limit=limit, offset=offset, time_range=time_range)
            return 200, data['items'] if 'items' in data else []  # Devuelve estado 200 y los datos si la llamada es exitosa
        except spotipy.SpotifyException as e:
            return e.http_status, []  # Devuelve el código de estado HTTP del error y una lista vacía

    def get_top_tracks(self, limit=20, offset=0, time_range='medium_term'):
        """
        Obtiene las pistas más escuchadas por el usuario en un rango de tiempo determinado.

        Args:
            limit: El número máximo de pistas a retornar.
            offset: El índice de la primera pista a retornar.
            time_range: El rango de tiempo para los datos ('short_term', 'medium_term', 'long_term').

        Returns:
            status: Estado HTTP de la respuesta.
            data: Una lista de las pistas más escuchadas por el usuario.
        """
        try:
            data = self.sp.current_user_top_tracks(limit=limit, offset=offset, time_range=time_range)
            return 200, data['items'] if 'items' in data else []  # Devuelve estado 200 y los datos si la llamada es exitosa
        except spotipy.SpotifyException as e:
            return e.http_status, []  # Devuelve el código de estado HTTP del error y una lista vacía


if __name__ == '__main__':
    # Ruta del archivo JSON que contiene el token de acceso
    token_file = 'token_info.json'

    with open(token_file, 'r') as file:
        token_info = json.load(file)
    token = token_info['access_token']

    specific_date = '2024-02-20'
    # Convierte la fecha a un objeto datetime
    date_obj = datetime.now().strptime(specific_date, '%Y-%m-%d')
    # Convierte el objeto datetime a un timestamp de Unix en milisegundos
    after_timestamp = int(date_obj.timestamp() * 1000)
    # 1708609730211
    print(after_timestamp)

    # Crea una instancia de la clase SpotifyData usando el token almacenado
    spotify_data = SpotifySingleUser(token)
    # recent_tracks = spotify_data.get_recently_played_tracks()
    # user_profile = spotify_data.get_user_profile()
    # followed_artists = spotify_data.get_followed_artists()
    # user_playlists = spotify_data.get_user_playlists()
    # user_top_artists = spotify_data.get_top_artists()
    # user_top_tracks = spotify_data.get_top_tracks()
    all_data = spotify_data.get_all_data()

    # file_name = 'recent_tracks.json'
    for data_type, data in all_data.items():
        filename = data_type + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Datos guardados en {filename}")

