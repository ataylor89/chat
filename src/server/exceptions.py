class TooManyConnections(Exception):
    
    def __init__(self, message='Too many connections'):
        super().__init__(message)
