import dataclasses
import datetime


@dataclasses.dataclass
class User:
    email: str
    cpf: str
    provider: str
    name: str | None = None
    phone: str | None = None
    id: int | None = None
    created_at: datetime.datetime | None = None


