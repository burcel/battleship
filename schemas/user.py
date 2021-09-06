from pydantic import BaseModel, constr


class UserBaseLogin(BaseModel):
    username: constr(min_length=2, max_length=20)  # type: ignore 


class UserBaseLoginResponse(BaseModel):
    token: str


class UserBaseDatabase(BaseModel):
    id: int
    username: constr(min_length=2, max_length=20)  # type: ignore 


class Message(BaseModel):
    message: str
