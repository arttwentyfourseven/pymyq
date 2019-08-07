"""Define exceptions."""


class MyQError(Exception):
    """Define a base exception."""

    pass


class InvalidCredentialsError(MyQError):
    """Define an exception related to invalid credentials."""

    pass


class RequestError(MyQError):
    """Define an exception related to bad HTTP requests."""

    pass


class UnsupportedBrandError(MyQError):
    """Define an exception related to unsupported brands."""

    pass
