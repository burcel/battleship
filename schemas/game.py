from typing import Optional, Tuple

from pydantic import BaseModel

from schemas.user import UserBaseDatabase


class GameBase(BaseModel):
    game_id: int
    users: Tuple[UserBaseDatabase, Optional[UserBaseDatabase]]
