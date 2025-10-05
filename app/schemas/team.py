from pydantic import BaseModel

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    personal_team: bool = False

class TeamOut(TeamBase):
    id: int
    personal_team: bool

    class Config:
        from_attributes = True
