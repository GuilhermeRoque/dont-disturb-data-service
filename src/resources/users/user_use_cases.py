import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from resources.utils.use_cases_execeptions import AlreadyExistsException, DuplicatedValuesException
from resources.users.user import UserRequestPayload
from resources.users.user_repository import UserRepository


class UserUseCases:

    @classmethod
    async def create_user(cls, user: UserRequestPayload, async_session: AsyncSession, repository=UserRepository):
        cpf_found = await repository.check_exists_cpf(
            cpf=user.cpf,
            session=async_session
        )
        email_found = await repository.check_exists_email(
            email=user.email,
            session=async_session
        )
        cls.check_cpf_and_email_constraints(cpf_found, email_found, AlreadyExistsException)

        result = await repository.create(user=user, session=async_session)
        await async_session.commit()
        return result

    @classmethod
    def check_cpf_and_email_constraints(cls, cpf: str | list[str], email: str | list[str], exception):
        if cpf and email:
            raise exception(("cpf", "email"), {"cpf": cpf, "email": email})
        elif cpf and not cpf:
            raise exception(("cpf", "email"), {"cpf": cpf})
        elif email:
            raise exception(("cpf", "email"), {"email": email})

    @classmethod
    async def get_users(cls, async_session: AsyncSession, repository=UserRepository):
        return await repository.get_all(session=async_session)

    @classmethod
    async def create_users_batch(cls, users: list[UserRequestPayload], async_session: AsyncSession,  repository=UserRepository):
        df_users = pd.DataFrame([user.__dict__ for user in users])
        email_series = df_users['email']
        cpf_series = df_users['cpf']
        cls.check_email_or_cpf_duplicated_batch(cpf_series, email_series)
        await cls.check_cpf_or_email_already_exists_batch(
            async_session=async_session,
            email_series=email_series,
            cpf_series=cpf_series
        )
        result = await repository.create_many(session=async_session, users=users)
        await async_session.commit()
        return result

    @classmethod
    def check_email_or_cpf_duplicated_batch(cls, cpf_series: pd.Series, email_series: pd.Series):
        email_series_duplicated = email_series[email_series.duplicated()].tolist()
        cpf_series_duplicated = cpf_series[cpf_series.duplicated()].tolist()
        cls.check_cpf_and_email_constraints(cpf_series_duplicated, email_series_duplicated, DuplicatedValuesException)

    @classmethod
    async def check_cpf_or_email_already_exists_batch(cls,
                                                      async_session: AsyncSession,
                                                      email_series: pd.Series,
                                                      cpf_series: pd.Series,
                                                      repository=UserRepository):

        email_list_registered = await repository.check_exists_email_batch(
            email_list=email_series.tolist(),
            session=async_session
        )
        cpf_list_registered = await repository.check_exists_cpf_batch(
            cpf_list=cpf_series.tolist(),
            session=async_session
        )
        cls.check_cpf_and_email_constraints(cpf_list_registered, email_list_registered, AlreadyExistsException)