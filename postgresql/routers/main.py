import sys
from unittest import result
sys.path.append("..")
import models, datetime
from enum import Enum
from typing import Optional
from fastapi import APIRouter, Depends
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

router = APIRouter(
    prefix="/main",
    tags=["main"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class StatusFilter(str, Enum):
    all        = "all"
    proceeding = "proceeding"
    completion = "completion"

@router.get("/influencer/{status_filter}")
async def main_influencer(status_filter: StatusFilter, search: Optional[str] = None, db: Session = Depends(get_db)):
    Influencers = db.query(models.Influencer, \
        func.avg(models.Insight.like).label('average_like'), \
        func.avg(models.Insight.comment).label('average_comment'), \
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.female_follower).label('average_female_follower'),
        func.avg(models.Insight.male_follower).label('average_male_follower')). \
        select_from(models.Influencer). \
        join(models.InfluencerPost). \
        join(models.Insight). \
        join(models.Campaign). \
        group_by(models.Influencer). \
        group_by(models.Campaign.end_at). \
        order_by(desc(models.Campaign.end_at))
    
    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.utcnow() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.utcnow() < models.Campaign.end_at)
    
    if search:
        campaigns = campaigns.filter(models.Campaign.name.contains(search))

    return Influencers.all()

@router.get("/campagin/{status_filter}")
async def main_campaign(status_filter: StatusFilter, search: Optional[str] = None,  db: Session = Depends(get_db)):
    campaigns = db.query(models.Campaign, \
        func.avg(models.Insight.like).label('average_like'), \
        func.avg(models.Insight.comment).label('average_comment'), \
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.female_follower).label('average_female_follower'),
        func.avg(models.Insight.male_follower).label('average_male_follower')). \
        select_from(models.Campaign). \
        join(models.InfluencerPost). \
        join(models.Insight). \
        group_by(models.Campaign.id). \
        order_by(desc(models.Campaign.end_at))
        
    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.utcnow() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.utcnow() < models.Campaign.end_at)
    
    if search:
        campaigns = campaigns.filter(models.Campaign.name.contains(search))
    
    return campaigns.all()
