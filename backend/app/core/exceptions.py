class AppException(Exception):
    """Base exception for application-level errors."""


class DuplicateEmailError(AppException):
    """Raised when a user attempts to register an existing email."""

    def __init__(self, email: str):
        self.email = email
        super().__init__("Email already registered")