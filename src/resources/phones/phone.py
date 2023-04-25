import dataclasses
import datetime


@dataclasses.dataclass
class PhoneRegistered:
    id: int
    phone: str
    id_user: int
    created_at: datetime.datetime


@dataclasses.dataclass
class PhoneRequestPayload:
    phone: str
    id_user: int
