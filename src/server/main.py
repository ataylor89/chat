from server import config_path
from server.server import Server
from configparser import ConfigParser

def main():
    config = ConfigParser()
    config.read(config_path)
    server = Server(config)
    server.listen()

if __name__ == '__main__':
    main()
