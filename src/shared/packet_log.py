from shared import project_root

class PacketLog:

    def __init__(self, config):
        self.config = config
        self.enabled = config['log']['enabled']
        if self.enabled:
            self.open_log()

    def open_log(self):
        filename = self.config['log']['logfile']
        path = project_root / 'logs' / filename
        mode = self.config['log']['logmode']

        id = 2
        stem = path.stem
        suffix = path.suffix

        while path.is_file():
            filename = f'{stem}-{id}' + suffix
            path = project_root / 'logs' / filename
            id += 1
   
        try:
            self.logger = open(path, mode)
        except Exception as err:
            self.enabled = False
            print(err)

    def write(self, message):
        if self.enabled:
            self.logger.write(message)

    def flush(self):
        if self.enabled:
            self.logger.flush()
