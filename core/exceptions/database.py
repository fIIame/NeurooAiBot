class DatabaseExceptions(Exception):
    """Базовое исключение для ошибок работы с базой данных."""
    pass


class InitializationError(DatabaseExceptions):
    """Ошибка инициализации базы данных (например, при подключении)."""

    def __init__(self, message: str = "Ошибка: база данных не инициализирована"):
        super().__init__(message)