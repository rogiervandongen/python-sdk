
class ErrorException(Exception):
    def __init__(self, error):
      self.error = error
      message = error.message
      super(ErrorException, self).__init__(message)


class SchemaException(Exception):
    def __init__(self, error_dict):
      self.errors = error_dict
      message = '\n'.join(['{}: {}'.format(str(k), ', '.join(str(e) for e in v)) for k, v in self.errors.items()])
      super(SchemaException, self).__init__(message)


class TransactionNotAuthorizedException(Exception):
    def __init__(self, message):
      super(TransactionNotAuthorizedException, self).__init__(message)


class TransactionStatusException(Exception):
    def __init__(self, message):
        super(TransactionStatusException, self).__init__(message)

