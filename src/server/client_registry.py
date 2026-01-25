from server.client import Client

class ClientRegistry(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_client(self, client):
        client_id = client.client_id
        if not client_id:
            raise ValueError('Attempted to add a null client ID to the registry')
        if client_id in self:
            raise ValueError(f'Client ID {client_id} is already in the registry')
        self[client_id] = client

    def remove_client(self, client_id):
        if client_id in self:
            del self[client_id]
