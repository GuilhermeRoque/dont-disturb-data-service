import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from resources.utils.use_cases_execeptions import AlreadyExistsException
from resources.users.user import User
from resources.users.user_repository import UserRepository


class UserUseCases:

    @classmethod
    async def create_user(cls, user: User, async_session: AsyncSession, repository=UserRepository):
        exists_cpf = await repository.check_exists_cpf(
            cpf=user.cpf,
            session=async_session
        )
        exists_email = await repository.check_exists_email(
            email=user.email,
            session=async_session
        )
        cls.check_cpf_and_email_constraints(exists_cpf, exists_email, user.cpf, user.email)

        return await repository.create(user=user, session=async_session)

    @classmethod
    def check_cpf_and_email_constraints(cls, exists_cpf, exists_email, cpf, email):
        if exists_cpf and exists_email:
            raise AlreadyExistsException(("cpf", "email"), {"cpf": cpf, "email": email})
        elif exists_cpf and not exists_email:
            raise AlreadyExistsException(("cpf", "email"), {"cpf": cpf})
        elif exists_email:
            raise AlreadyExistsException(("cpf", "email"), {"email": email})

    @classmethod
    async def get_users(cls, async_session: AsyncSession, repository=UserRepository):
        return await repository.get_all(session=async_session)

    @classmethod
    async def create_users_batch(cls, users: list[User], async_session: AsyncSession,  repository=UserRepository):
        df_users = pd.DataFrame([user.__dict__ for user in users])
        email_series = df_users['email']
        cpf_series = df_users['cpf']
        await cls.check_cpf_or_email_already_exists_batch(
            async_session=async_session,
            email_series=email_series,
            cpf_series=cpf_series
        )
        email_series_duplicated = email_series[email_series.duplicated()]
        cpf_series_duplicated = cpf_series[cpf_series.duplicated()]

        return await repository.create_many(session=async_session, users=users)

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
        cls.check_cpf_and_email_constraints(cpf_list_registered, email_list_registered, cpf_list_registered, email_list_registered)