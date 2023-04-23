import dataclasses
import datetime


@dataclasses.dataclass
class UserActive:
    email: str
    cpf: str
    name: str | None = None
    phone: str | None = None
