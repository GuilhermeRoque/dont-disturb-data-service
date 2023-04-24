import dataclasses
import datetime


@dataclasses.dataclass
class UserRegistered:
    email: str
    cpf: str
    provider: str
    name: str
    id: int
    created_at: datetime.datetime


@dataclasses.dataclass
class UserRequestPayload:
    email: str
    cpf: str
    provider: str
    name: str
