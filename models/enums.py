from enum import Enum


class RolesEnum(Enum):
    admin = "admin"
    chef = "chef"
    deliver = "deliver"
    customer = "customer"


class SizeEnum(Enum):
    s = "s"
    m = "m"
    l = "l"
    j = "j"


class StatusEnum(Enum):
    pending = "pending"
    in_transition = "in transition"
    delivered = "delivered"
