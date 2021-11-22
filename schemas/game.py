from typing import Optional

from pydantic import BaseModel, constr, conint


class GameBaseCreate(BaseModel):
    name: Optional[constr(min_length=1, max_length=200)] = None
    password: Optional[constr(min_length=1, max_length=200)] = None


class GameBaseCreateResponse(BaseModel):
    game_id: int


class GameBaseList(GameBaseCreate):
    page: conint(gt=0)
    username: Optional[constr(min_length=3, max_length=50)] = None
