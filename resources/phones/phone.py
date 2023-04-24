import dataclasses


@dataclasses.dataclass
class PhoneRegistered:
    id: int
    phone: str
    id_user: int


@dataclasses.dataclass
class PhoneRequestPayload:
    phone: str
    id_user: int
