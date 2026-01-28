from client import project_root
from shared.rsa import parser

class KeyManager(dict):
    
    def __init__(self, config):
        super().__init__()
        self.config = config

    def load(self):
        key_path = project_root / 'keys' / 'client' / self.config['rsa']['keyfile']
        key_pair = parser.parse_key(key_path)
        self['client'] = key_pair
        self['server'] = {'public': None}
