class CLISyntaxError(RuntimeError):

    def __init__(self, msg):
        super(RuntimeError, self).__init__(msg)
