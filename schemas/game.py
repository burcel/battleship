from typing import Optional, Tuple
from pydantic import BaseModel


class GameBase(BaseModel):
    users: Tuple[str, Optional[str]]
