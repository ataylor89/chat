from server import base_dir
from shared.rsa import parser

class KeyManager(dict):
    
    def __init__(self, config):
        super().__init__()
        self.config = config

    def load(self):
        public_key_path = base_dir + '/' + self.config['default']['public_key_path']
        private_key_path = base_dir + '/' + self.config['default']['private_key_path']
        self['public'] = parser.parse_key(public_key_path)
        self['private'] = parser.parse_key(private_key_path)
