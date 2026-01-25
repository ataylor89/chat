from client import base_dir
from client.client import Client
from client.gui import GUI
from configparser import ConfigParser

def main():
    config = ConfigParser()
    config_path = base_dir + '/client/config/client_settings.ini'
    config.read(config_path)
    cli = Client(config)
    gui = GUI(config)
    gui.set_client(cli)
    cli.set_gui(gui)
    gui.mainloop()

if __name__ == '__main__':
    main()
