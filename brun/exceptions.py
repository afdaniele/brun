class CLISyntaxError(RuntimeError):
    def __init__(self, msg):
        super(RuntimeError, self).__init__(msg)


class TaskFailureError(RuntimeError):
    def __init__(self, msg, result=None):
        self.result = result
        super(RuntimeError, self).__init__(msg)


class InvalidConfigurationError(RuntimeError):
    def __init__(self, msg, data=None):
        self.data = data
        super(RuntimeError, self).__init__(msg)
