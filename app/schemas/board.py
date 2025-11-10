from pydantic import BaseModel, Field

class BoardMapIn(BaseModel):
    mid: str = Field(..., description="Rhymix 게시판 mid (예: group_42_board)")

class BoardMapOut(BaseModel):
    groupId: int
    mid: str
    url: str
    exists: bool
