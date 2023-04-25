import dataclasses


@dataclasses.dataclass
class UserActive:
    cpf: str
    email: str | None = None
    name: str | None = None
    phone: str | None = None
