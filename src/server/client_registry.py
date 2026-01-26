from server import max_connections
from server.client import Client
from server.exceptions import TooManyConnections

class ClientRegistry(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def first_available_client_id(self):
        client_id = 1

        while client_id in self and client_id <= max_connections:
            client_id += 1

        if client_id > max_connections:
            raise TooManyConnections()

        return client_id

    def add_client(self, client_socket, client_address):
        client_id = self.first_available_client_id()
        self[client_id] = Client(client_id, client_socket, client_address)
        return client_id

    def remove_client(self, client_id):
        if client_id in self:
            del self[client_id]
