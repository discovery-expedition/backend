import sys
from unittest import result
sys.path.append("..")
import models, datetime
from enum import Enum
from typing import Optional
from fastapi import APIRouter, Depends
from database import engine, SessionLocal
from sqlalchemy.orm import Session, contains_eager, joinedload, aliased
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
async def abc(status_filter: StatusFilter, search: Optional[str] = None, db: Session = Depends(get_db)):
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
    
    results = [{
        "id"                    : Influencer[0].id,
        "profile_image"         : Influencer[0].profile_image,
        "updated_at"            : Influencer[0].updated_at,
        "full_name"             : Influencer[0].full_name,
        "name"                  : Influencer[0].name,
        "created_at"            : Influencer[0].created_at,
        "updated_at"            : Influencer[0].updated_at,
        "average_like"          : int(Influencer.average_like),
        "average_comment"       : int(Influencer.average_comment),
        "average_exposure"      : int(Influencer.average_exposure),
        "average_participation" : int(Influencer.average_like) + int(Influencer.average_comment),
        "average_rate"          : round((Influencer.average_like + Influencer.average_comment) / \
                                 (Influencer.average_female_follower + Influencer.average_male_follower) * 100, 3),
        "follower"              : int(Influencer.average_female_follower + Influencer.average_male_follower),
        "campaign_status" : "완료" if datetime.datetime.utcnow() >= Influencer[0].influencer_posts[0].campaign.end_at else "진행 중",
    } for Influencer in Influencers]

    return results

@router.get("/campagin/{status_filter}")
async def abc(status_filter: StatusFilter, search: Optional[str] = None,  db: Session = Depends(get_db)):
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
    
    results = [{
        "id"              : campaign[0].id,
        "name"            : campaign[0].name,
        "tag"             : campaign[0].tag,
        "description"     : campaign[0].description,
        "end_at"          : campaign[0].end_at,
        "image"           : campaign[0].image,
        "created_at"      : campaign[0].created_at,
        "updated_at"      : campaign[0].updated_at,
        "average_like"    : int(campaign.average_like),
        "average_comment" : int(campaign.average_comment),
        "average_exposure": int(campaign.average_exposure),
        "average_participation": int(campaign.average_like) + int(campaign.average_comment),
        "average_rate"         : round((campaign.average_like + campaign.average_comment) / \
                                 (campaign.average_female_follower + campaign.average_male_follower) * 100, 3),
        "campaign_status" : "완료" if datetime.datetime.utcnow() >= campaign[0].end_at else "진행 중"
    } for campaign in campaigns]

    return results
