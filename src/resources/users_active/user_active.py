import dataclasses


@dataclasses.dataclass
class UserActive:
    email: str
    cpf: str
    name: str
    phone: str
