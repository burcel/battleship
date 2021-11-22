from typing import Optional

from pydantic import BaseModel, constr, conint


class GameBaseCreate(BaseModel):
    name: Optional[constr(min_length=1, max_length=200)] = None
    password: Optional[constr(min_length=1, max_length=200)] = None


class GameBaseCreateResponse(BaseModel):
    game_id: int


class GameBaseList(BaseModel):
    page: conint(ge=0)
    name: Optional[constr(min_length=1, max_length=200)] = None


class GameBaseResponse(BaseModel):
    id: int
    name: constr(min_length=1, max_length=200)

    class Config:
        orm_mode = True
