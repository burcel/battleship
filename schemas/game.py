from typing import Optional, Tuple

from pydantic import BaseModel

from schemas.user import UserBaseDatabase


class GameBase(BaseModel):
    users: Tuple[UserBaseDatabase, Optional[UserBaseDatabase]]
