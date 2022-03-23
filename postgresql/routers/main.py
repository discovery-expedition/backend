import sys
sys.path.append("..")
import models, datetime
from enum           import Enum
from typing         import Optional
from fastapi        import APIRouter, Depends
from database       import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy     import func, desc
from pydantic       import BaseModel, AnyUrl, Field
from typing         import List, Optional, Dict ,Union
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

class InfluencerBase(BaseModel):
    id            : str           = Field(None)
    full_name     : str           = Field(None)
    name          : str           = Field(None)
    profile_image : AnyUrl        = Field(None)
    company_id    : datetime.date = Field(None)
    created_at    : datetime.date = Field(None)
    updated_at    : datetime.date = Field(None)
 
    class Config:
        orm_mode = True

class InfluencerSchema(BaseModel):
    Influencer              : InfluencerBase = Field(None)
    average_like            : float          = Field(None)
    average_comment         : float          = Field(None)
    average_exposure        : float          = Field(None)
    average_female_follower : float          = Field(None)
    average_male_follower   : float          = Field(None)
    
    class Config:
        orm_mode = True

class CampaignBase(BaseModel):
    id          : int           = Field(None)
    name        : str           = Field(None) 
    tag         : str           = Field(None) 
    description : str           = Field(None) 
    end_at      : datetime.date = Field(None)         
    image       : AnyUrl        = Field(None)     
    budget      : int           = Field(None) 
    created_at  : datetime.date = Field(None)         
    updated_at  : datetime.date = Field(None)         

    class Config:
        orm_mode = True

class CampaignSchema(BaseModel):
    Campaign                : CampaignBase = Field(None)
    average_like            : float        = Field(None)
    average_comment         : float        = Field(None)
    average_exposure        : float        = Field(None)
    average_female_follower : float        = Field(None)
    average_male_follower   : float        = Field(None)

    class Config:
        orm_mode = True

@router.get("/influencer/{status_filter}", response_model = List[InfluencerSchema])
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
        group_by(models.Influencer.id)
    
    if status_filter == StatusFilter.completion:
        Influencers = Influencers.filter(datetime.datetime.utcnow() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        Influencers = Influencers.filter(datetime.datetime.utcnow() < models.Campaign.end_at)
    
    if search:
        Influencers = Influencers.filter(models.Campaign.name.contains(search))

    return Influencers.all()

@router.get("/campaign/{status_filter}", response_model = List[CampaignSchema])
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
