import dataclasses
import io
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from resources.phones.phone import PhoneRequestPayload, PhoneRegistered
from resources.phones.phone_repository import PhonesRepository
from resources.users.user_repository import UserRepository
from resources.users_active.user_active_repository import UserActiveRepository
from resources.utils.regex_common import CPF_REGEX, PHONE_REGEX
from resources.utils.use_cases_execeptions import ParseFileException, DataFrameColumnsValidationException, \
    DataFrameRowsValidationException
import numpy


@dataclasses.dataclass
class ImportReportUpdated:
    cpf: str
    phone: str


class MailCleanupUseCases:

    @classmethod
    async def cleanup_by_phones(cls,
                                file_binary: bytes,
                                async_session: AsyncSession,
                                user_active_repository=UserActiveRepository,
                                phones_repository=PhonesRepository
                                ) -> list[ImportReportUpdated]:

        df = cls._get_csv_from_file(file_binary)
        cls._validate_dataframe(df=df)
        phone_rows = ("phone1", "phone2", "phone3", "phone4", "phone5")
        df.columns = ("cpf", *phone_rows)

        phones_to_remove_cpf = await cls._get_active_phones_to_remove(
            async_session=async_session,
            df=df,
            phone_rows=phone_rows,
            user_active_repository=user_active_repository
        )
        if len(phones_to_remove_cpf):
            df = pd.DataFrame(phones_to_remove_cpf)
            phones_to_remove_list = df['phone'].tolist()
            await phones_repository.delete_phones(phones=phones_to_remove_list, async_session=async_session)

        await async_session.commit()

        return [ImportReportUpdated(phone=phone_result['phone'], cpf=phone_result['cpf']) for phone_result in phones_to_remove_cpf]

    @classmethod
    async def update_by_phones(cls,
                               file_binary: bytes,
                               async_session: AsyncSession,
                               phones_repository=PhonesRepository,
                               user_repository=UserRepository,
                               ) -> list[PhoneRegistered]:

        df = cls._get_csv_from_file(file_binary)
        cls._validate_dataframe(df=df)
        phone_rows = ("phone1", "phone2", "phone3", "phone4", "phone5")
        df.columns = ("cpf", *phone_rows)
        all_phones = pd.Series(numpy.concatenate(df.set_index('cpf').values))
        all_phones = all_phones[all_phones.notna()].tolist()
        await phones_repository.delete_phones(phones=all_phones, async_session=async_session)
        cpf_id_data = await user_repository.get_all_in_cpf(session=async_session, cpf_list=df['cpf'])
        if not cpf_id_data:
            return []
        df_cpf = pd.DataFrame(cpf_id_data)
        df = pd.merge(df, df_cpf, on='cpf')
        phone_created_list = []
        for data_to_register in df.to_dict(orient='records'):
            for phone_row in phone_rows:
                phone_to_request = PhoneRequestPayload(phone=data_to_register[phone_row],
                                                       id_user=data_to_register['id'])
                phone_created = await phones_repository.create(phone=phone_to_request, session=async_session)
                phone_created_list.append(phone_created)

        await async_session.commit()
        return phone_created_list

    @classmethod
    async def _get_active_phones_to_remove(cls,
                                           async_session: AsyncSession,
                                           df: pd.DataFrame,
                                           phone_rows: tuple,
                                           user_active_repository=UserActiveRepository):
        phones_to_remove_cpf = list()
        for row in df.to_dict(orient='records'):
            phones_to_remove = await user_active_repository.get_all_phones_from_cpf(
                async_session=async_session,
                phones=[row[phone_row] for phone_row in phone_rows if not pd.isna(row[phone_row])],
                cpf=row['cpf']
            )
            if len(phones_to_remove):
                for phone in phones_to_remove:
                    phones_to_remove_cpf.append({'cpf': row['cpf'], 'phone': phone})
        return phones_to_remove_cpf

    @classmethod
    def _validate_dataframe(cls, df: pd.DataFrame):
        columns_size = len(df.columns)
        if columns_size != 6:
            raise DataFrameColumnsValidationException(
                message=f"There is {columns_size} columns. It's expected to have 6 columns.")

        df = df.apply(lambda x: x.astype(str))

        cpf_column = df[0]
        cpf_errors = cls._check_regex(cpf_column, CPF_REGEX)
        if len(cpf_errors):
            raise DataFrameRowsValidationException(
                message="It's expected to have CPFs with only numbers in the first column",
                indexes_errors=cpf_errors)
        for i in range(1, 6):
            phone_column = df[i].copy()
            phone_column = phone_column[phone_column != 'nan'].copy()
            phone_errors = cls._check_regex(phone_column, PHONE_REGEX)
            if len(phone_errors):
                raise DataFrameRowsValidationException(
                    message=f"It's expected to have phones with format 'DDD+Number' with only numbers in the {i + 1}º column",
                    indexes_errors=phone_errors)

    @classmethod
    def _get_csv_from_file(cls, file: bytes) -> pd.DataFrame:
        try:
            buffer = io.BytesIO(file)
            df = pd.read_csv(buffer, header=None, dtype={i: object for i in range(0, 6)})
        except Exception:
            raise ParseFileException(format_expected="csv")
        return df

    @classmethod
    def _check_regex(cls, column: pd.Series, regex: str) -> dict:
        match_regex = column.str.contains(regex)
        errors = column[~match_regex].to_dict()
        return errors
