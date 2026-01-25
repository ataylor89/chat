class ClientData:
    def __init__(self, client_id, client_socket, client_address):
        self.client_id = client_id
        self.client_socket = client_socket
        self.client_address = client_address
        self.client_name = format('Client-%d' %client_id)
        self.public_key = None
        self.encryption = False
        self.logged_in = False
        self.username = None

    def get_display_name(self):
        return self.username if self.username else self.client_name

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
