import abc
import http


class UseCasesExceptions(Exception, abc.ABC):
    @abc.abstractmethod
    def get_message(self) -> str:
        pass

    @abc.abstractmethod
    def get_values(self) -> list | dict:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_error_code() -> http.HTTPStatus:
        pass


class UseCaseBadRequestException(UseCasesExceptions, abc.ABC):

    @staticmethod
    def get_error_code() -> http.HTTPStatus:
        return http.HTTPStatus.BAD_REQUEST


class AlreadyExistsException(UseCaseBadRequestException):
    """
    Raised when the unique constraint of a database table is violated
    """

    def __init__(self, unique_fields: tuple = None, duplicated_values: list = None):
        self.unique_fields = unique_fields
        self.duplicated_values = duplicated_values

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} unique_fields={self.unique_fields}"

    def get_message(self) -> str:
        unique_fields_msg = f" Check the unique fields: {self.unique_fields}" if self.unique_fields else ""
        duplicated_values_msg = f" Duplicated values: {self.duplicated_values}" if self.duplicated_values else ""

        return f"Already exists record with this configuration.{unique_fields_msg}{duplicated_values_msg}"

    def get_values(self) -> list | dict:
        return self.duplicated_values.copy()


class DuplicatedValuesException(UseCaseBadRequestException):
    """
    Raised in batch requests when there is duplicated data
    """

    def __init__(self, unique_fields: tuple = None, duplicated_values: list = None):
        self.unique_fields = unique_fields
        self.duplicated_values = duplicated_values

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} unique_fields={self.unique_fields}"

    def get_message(self) -> str:
        unique_fields_msg = f" Check the unique fields: {self.unique_fields}" if self.unique_fields else ""
        duplicated_values_msg = f" Duplicated values: {self.duplicated_values}" if self.duplicated_values else ""

        return f"There is duplicated data in the request.{unique_fields_msg}{duplicated_values_msg}"

    def get_values(self) -> list | dict:
        return self.duplicated_values.copy()


class ParseFileException(UseCaseBadRequestException):
    """
    Raised in file upload requests when the file format it's not the expected
    """

    def __init__(self, format_expected: str):
        self.format_expected = format_expected

    def get_message(self) -> str:
        return f"Was not possible to parse the file. Please check if the provided file is a {self.format_expected} file"

    def get_values(self) -> list | dict:
        return []

class DataFrameRowsValidationException(UseCaseBadRequestException):
    """
    Raised on dataframe rows validation when values differs from expected
    """

    def __init__(self, message: str, indexes_errors: list):
        self.message = message
        self.indexes_errors = indexes_errors

    def get_message(self) -> str:
        return f"Validation error. {self.message}. Fix the following values at indexes: {self.indexes_errors}"

    def get_values(self) -> list | dict:
        return self.indexes_errors.copy()

class DataFrameColumnsValidationException(UseCaseBadRequestException):
    """
    Raised on dataframe columns validation when values differs from expected
    """

    def __init__(self, message: str):
        self.message = message

    def get_message(self) -> str:
        return f"Validation error. {self.message}."

    def get_values(self) -> list | dict:
        return []
