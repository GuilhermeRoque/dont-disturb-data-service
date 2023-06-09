import dataclasses
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from resources.phones.phone import PhoneRequestPayload
from resources.phones.phone_repository import PhonesRepository
from resources.users.user import UserRequestPayload
from resources.users.user_repository import UserRepository
from resources.users_active.user_active_repository import UserActiveRepository
from resources.utils.import_csv import check_regex, get_csv_from_file
from resources.utils.regex_common import CPF_REGEX, PHONE_REGEX
from resources.utils.use_cases_execeptions import DataFrameColumnsValidationException, \
    DataFrameRowsValidationException, DuplicatedValuesException
import numpy


@dataclasses.dataclass
class ImportReportUpdated:
    cpf: str
    phone: str


class ImportPhonesUseCases:

    @classmethod
    async def cleanup_by_phones(cls,
                                file_binary: bytes,
                                async_session: AsyncSession,
                                user_active_repository=UserActiveRepository,
                                phones_repository=PhonesRepository
                                ) -> list[ImportReportUpdated]:

        df = get_csv_from_file(file_binary)
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

        return [ImportReportUpdated(phone=phone_result['phone'], cpf=phone_result['cpf']) for phone_result in
                phones_to_remove_cpf]

    @classmethod
    async def update_by_phones(cls,
                               file_binary: bytes,
                               async_session: AsyncSession,
                               phones_repository=PhonesRepository,
                               user_repository=UserRepository,
                               ) -> list[ImportReportUpdated]:

        df = get_csv_from_file(file_binary)
        cls._validate_dataframe(df=df)
        phone_rows = ("phone1", "phone2", "phone3", "phone4", "phone5")
        df.columns = ("cpf", *phone_rows)
        all_phones = pd.Series(numpy.concatenate(df.set_index('cpf').values))
        all_phones = all_phones[all_phones.notna()].copy()

        phones_duplicated = all_phones[all_phones.duplicated()].copy()
        if len(phones_duplicated):
            raise DuplicatedValuesException(unique_fields=('phone',), duplicated_values=phones_duplicated.tolist())

        all_phones = all_phones.tolist()
        await phones_repository.delete_phones(phones=all_phones, async_session=async_session)

        cpf_id_data = await user_repository.get_all_in_cpf(session=async_session, cpf_list=df['cpf'])
        if len(cpf_id_data):
            df_cpf = pd.DataFrame(cpf_id_data)
            df_not_registered = df[~df['cpf'].isin(df_cpf['cpf'])].copy()
            users_to_register = [UserRequestPayload(cpf=cpf) for cpf in df_not_registered['cpf'].tolist()]
            await user_repository.create_many(users=users_to_register, session=async_session)
        else:
            users_to_register = [UserRequestPayload(cpf=cpf) for cpf in df['cpf'].tolist()]
            await user_repository.create_many(users=users_to_register, session=async_session)

        cpf_id_data = await user_repository.get_all_in_cpf(session=async_session, cpf_list=df['cpf'])
        df_cpf = pd.DataFrame(cpf_id_data)

        df = pd.merge(df, df_cpf, on='cpf')

        phone_created_list = []
        for data_to_register in df.to_dict(orient='records'):
            for phone_row in phone_rows:
                phone_number = data_to_register[phone_row]
                if pd.isnull(phone_number):
                    continue
                phone_to_request = PhoneRequestPayload(phone=phone_number,
                                                       id_user=data_to_register['id'])
                phone_created = await phones_repository.create(phone=phone_to_request, session=async_session)
                phone_created_list.append(ImportReportUpdated(phone=phone_created.phone, cpf=data_to_register['cpf']))

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
        cpf_errors = check_regex(cpf_column, CPF_REGEX)
        if len(cpf_errors):
            raise DataFrameRowsValidationException(
                message="It's expected to have CPFs with only numbers in the first column",
                indexes_errors=cpf_errors)
        for i in range(1, 6):
            phone_column = df[i].copy()
            phone_column = phone_column[phone_column != 'nan'].copy()
            phone_errors = check_regex(phone_column, PHONE_REGEX)
            if len(phone_errors):
                raise DataFrameRowsValidationException(
                    message=f"It's expected to have phones with format 'DDD+Number' with only numbers in the {i + 1}º column",
                    indexes_errors=phone_errors)
