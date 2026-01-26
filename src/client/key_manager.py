from client import base_dir
from shared.rsa import parser

class KeyManager(dict):
    
    def __init__(self, config):
        super().__init__()
        self.config = config

    def load(self):
        key_path = base_dir + '/' + self.config['rsa']['keypath']
        key_pair = parser.parse_key(key_path)
        self['client'] = key_pair
        self['server'] = {'public': None}
