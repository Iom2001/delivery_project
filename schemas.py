from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "username": "Islomjon",
                "email": "islomjonmeliboevwork@gmail.com",
                "password": "Qwerty1234",
                "is_staff": False,
                "is_active": True,
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str = "d3ced14b14c9f9e6749ec0bbde199afb6ac55681fa5143a77604204eea33191d"

class LoginModel(BaseModel):
    username_or_email: str
    password: str