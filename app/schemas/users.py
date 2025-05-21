from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"
