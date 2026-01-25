class Client:
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
