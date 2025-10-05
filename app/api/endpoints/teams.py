from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamOut
from app.api.dependencies import get_current_user, get_db_sync, get_db

router = APIRouter()

@router.get("/", response_model=list[TeamOut])
def read_teams(skip: int = 0, limit: int = 10, db: Session = Depends(get_db_sync), current_user = Depends(get_current_user)):
    teams = db.query(Team).filter(Team.user_id == current_user.id).offset(skip).limit(limit).all()
    return teams

@router.post("/", response_model=TeamOut)
def create_team(team: TeamCreate, db: Session = Depends(get_db_sync), current_user = Depends(get_current_user)):
    db_team = Team(name=team.name, user_id=current_user.id, personal_team=team.personal_team)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db_sync), current_user = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id, Team.user_id == current_user.id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return team
