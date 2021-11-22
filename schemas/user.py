from pydantic import BaseModel, constr, EmailStr


class UserBaseSession(BaseModel):
    id: int
    username: constr(min_length=3, max_length=50)


class UserBaseLogin(BaseModel):
    username: constr(min_length=3, max_length=50)  # type: ignore
    password: str


class UserBaseLoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class UserBaseCreate(UserBaseLogin):
    email: EmailStr


class UserBaseResponse(BaseModel):
    username: constr(min_length=3, max_length=50)  # type: ignore
    email: EmailStr

    class Config:
        orm_mode = True
