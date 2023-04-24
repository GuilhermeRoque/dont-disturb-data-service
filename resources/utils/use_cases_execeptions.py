import abc
import http


class UseCasesExceptions(Exception, abc.ABC):
    @abc.abstractmethod
    def get_message(self) -> str:
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

    def __init__(self, unique_fields: tuple = None, duplicated_values: dict = None):
        self.unique_fields = unique_fields
        self.duplicated_values = duplicated_values

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} unique_fields={self.unique_fields}"


    def get_message(self) -> str:
        unique_fields_msg = f" Check the unique fields: {self.unique_fields}" if self.unique_fields else ""
        duplicated_values_msg = f" Duplicated values: {self.duplicated_values}" if self.duplicated_values else ""

        return f"Already exists record with this configuration.{unique_fields_msg}{duplicated_values_msg}"


class DuplicatedValues(UseCaseBadRequestException):
    """
    Raised in batch requests when there is duplicated data
    """

    def __init__(self, unique_fields: tuple = None, duplicated_values: dict = None):
        self.unique_fields = unique_fields
        self.duplicated_values = duplicated_values

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name} unique_fields={self.unique_fields}"

    def get_message(self) -> str:
        unique_fields_msg = f" Check the unique fields: {self.unique_fields}" if self.unique_fields else ""
        duplicated_values_msg = f" Duplicated values: {self.duplicated_values}" if self.duplicated_values else ""

        return f"There is duplicated data in the request.{unique_fields_msg}{duplicated_values_msg}"
