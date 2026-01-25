from server import base_dir
from server.server import Server
from configparser import ConfigParser

def main():
    config = ConfigParser()
    config_path = base_dir + '/config/server_settings.ini'
    config.read(config_path)
    server = Server(config)
    server.listen()

if __name__ == '__main__':
    main()
