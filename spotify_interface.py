import json
from get_user_data import SpotifySingleUser
import time


class SpotifyInterface:
    def __init__(self):
        self.spotify_user = None

    def handle_requests(self, token, id_user, data_requests):
        # Calcular el timestamp UNIX al inicio de la petición
        current_unix_timestamp = int(time.time())

        # Actualizar/instanciar SpotifySingleUser con el token proporcionado
        self.spotify_user = SpotifySingleUser(token)

        # Inicializar un diccionario para almacenar los estados de las respuestas
        response_statuses = {}

        for request in data_requests:
            # Llamar al método correspondiente en SpotifySingleUser según el elemento de la lista
            if hasattr(self.spotify_user, request):
                method = getattr(self.spotify_user, request)
                status, data = method()

                # Si el estado es 200, escribe la información en un JSON
                if status == 200:
                    filename = f"data/{id_user}_{request}_{current_unix_timestamp}.json"
                    self.write_data_to_file(data, filename)

                # Almacenar el estado de la respuesta
                response_statuses[request] = status
            else:
                response_statuses[request] = 'Method not found'

        # Devolver los estados de las respuestas
        return response_statuses

    def write_data_to_file(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
