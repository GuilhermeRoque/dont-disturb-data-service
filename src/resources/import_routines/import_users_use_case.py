import datetime

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from resources.users.user import UserRegistered, UserRequestPayload
from resources.users.user_repository import UserRepository
from resources.utils.import_csv import get_csv_from_file, check_regex
from resources.utils.regex_common import CPF_REGEX, EMAIL_REGEX
from resources.utils.use_cases_execeptions import DataFrameColumnsValidationException, DataFrameRowsValidationException


class ImportUsersUseCase:
    @classmethod
    async def crate_users_import(cls,
                                 file_binary: bytes,
                                 async_session: AsyncSession,
                                 user_repository=UserRepository,
                                 ) -> list[UserRegistered]:

        df = get_csv_from_file(file_binary)
        df.columns = ('cpf', 'email', 'name', 'provider', )
        cls._validate_dataframe_users(df=df)
        users_already_registered = await user_repository.get_all_in_cpf(session=async_session, cpf_list=df['cpf'])

        if len(users_already_registered):
            df_users_already_registered = pd.DataFrame([{'cpf': user.cpf, 'id': user.id} for user in users_already_registered])

            df_to_update = pd.merge(df, df_users_already_registered, on='cpf')
            users_to_update = [
                UserRegistered(
                    cpf=row['cpf'],
                    provider=row['provider'],
                    email=row['email'],
                    name=row['name'],
                    id=row['id'],
                    created_at=datetime.datetime.now()
                ) for row in df_to_update.to_dict(orient='records')
            ]
            users_updated = await user_repository.update_many(users=users_to_update, session=async_session)

            df_to_register = df[~df['cpf'].isin(df_users_already_registered['cpf'])].copy()
        else:
            df_to_register = df.copy()
            users_updated = []
        users_to_register = [
            UserRequestPayload(
                cpf=row['cpf'],
                provider=row['provider'],
                email=row['email'],
                name=row['name']
            ) for row in df_to_register.to_dict(orient='records')
        ]
        users_created = await user_repository.create_many(users=users_to_register, session=async_session)

        await async_session.commit()

        users_added_or_updated = [*users_updated, *users_created]
        return users_added_or_updated

    @classmethod
    def _validate_dataframe_users(cls, df: pd.DataFrame):
        columns_size = len(df.columns)
        columns_size_expected = 4
        if columns_size != columns_size_expected:
            raise DataFrameColumnsValidationException(
                message=f"There is {columns_size} columns. It's expected to have {columns_size_expected} columns.")

        df = df.apply(lambda x: x.astype(str))

        cpf_column = df['cpf']
        cpf_errors = check_regex(cpf_column, CPF_REGEX)
        if len(cpf_errors):
            raise DataFrameRowsValidationException(
                message="It's expected to have CPFs with only numbers in the first column",
                indexes_errors=cpf_errors)

        email_column = df['email']
        email_errors = check_regex(email_column, EMAIL_REGEX)
        if len(email_errors):
            raise DataFrameRowsValidationException(
                message="It's expected to have only e-mails in the second column",
                indexes_errors=email_errors
            )

        column_str = df['name'].copy()
        cls._validate_str_column(column_str, 'name')

        column_str = df['provider'].copy()
        cls._validate_str_column(column_str, 'provider')

    @classmethod
    def _validate_str_column(cls, column_str, name):
        column_str_notna = column_str[column_str.notna()].copy()
        column_str_errors = column_str_notna[column_str_notna.str.len() > 255].to_dict()
        if len(column_str_errors):
            raise DataFrameRowsValidationException(
                message=f"It's expected to have text values only with max length of 255 characters in the {name} columnº",
                indexes_errors=column_str_errors
            )
