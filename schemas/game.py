from datetime import datetime
from typing import Optional

from pydantic import BaseModel, conint, constr


class GameBaseCreate(BaseModel):
    name: Optional[constr(min_length=1, max_length=200)] = None
    password: Optional[constr(min_length=1, max_length=200)] = None


class GameBaseCreateResponse(BaseModel):
    id: int


class GameBaseList(BaseModel):
    page: conint(ge=0)
    name: Optional[constr(min_length=1, max_length=200)] = None


class GameBaseResponse(BaseModel):
    id: int
    name: constr(min_length=1, max_length=200)
    with_password: bool = False

    class Config:
        orm_mode = True


class GameBaseJoin(BaseModel):
    id: conint(ge=0)
    password: Optional[constr(min_length=1, max_length=200)] = None


class GameBase(BaseModel):
    id: conint(ge=0)
    name: constr(min_length=1, max_length=200)
    create_date: datetime
    creator_username: constr(min_length=3, max_length=50)
    second_username: Optional[constr(min_length=3, max_length=50)]
