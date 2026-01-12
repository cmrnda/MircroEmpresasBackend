from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CreateUserRequest:
    email: str
    password: str
    roles: List[str]

@dataclass
class UpdateUserRequest:
    email: Optional[str] = None
    activo: Optional[bool] = None

@dataclass
class UpdateRolesRequest:
    roles: List[str]

@dataclass
class ChangePasswordRequest:
    new_password: str
