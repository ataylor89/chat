class KeyFileError(Exception):

    def __init__(self, message='Invalid key file'):
        super().__init__(message)
