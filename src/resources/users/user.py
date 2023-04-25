import dataclasses
import datetime


@dataclasses.dataclass
class UserRegistered:
    id: int
    cpf: str
    created_at: datetime.datetime
    email: str | None = None
    provider: str | None = None
    name: str | None = None


@dataclasses.dataclass
class UserRequestPayload:
    cpf: str
    email: str | None = None
    provider: str | None = None
    name: str | None = None
