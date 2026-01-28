from shared import project_root

class PacketLog:

    def __init__(self, config):
        self.config = config
        self.enabled = config['log']['enabled']
        self.logger = None
        if self.enabled:
            try:
                self.open_log()
            except Exception as err:
                self.enabled = False
                print(err)

    def open_log(self):
        filename = self.config['log']['filename']
        directory = self.config['log']['directory']
        path = project_root / 'logs' / directory / filename
        mode = self.config['log']['mode']

        id = 1
        stem = path.stem
        suffix = path.suffix

        while path.is_file() and id <= 100:
            filename = f'{stem}-{id}' + suffix
            path = project_root / 'logs' / directory / filename
            id += 1
   
        self.logger = open(path, mode)

    def write(self, message):
        if self.enabled:
            self.logger.write(message)

    def flush(self):
        if self.enabled:
            self.logger.flush()
