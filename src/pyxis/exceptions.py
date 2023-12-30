class IllegalArgumentException(ValueError):
    """
    Thrown when a method is passed an illegal or inappropriate argument.
    """


class IllegalStateException(Exception):
    """
    Thrown when a method has been invoked at an inappropriate time or the state of an object
    is not appropriate for the requested operation.
    """
