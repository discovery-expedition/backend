import sys
sys.path.append("..")
import models, datetime
import pandas as pd
from enum           import Enum
from pymysql        import NULL, Date
from fastapi        import APIRouter, Depends, HTTPException
from database       import engine, SessionLocal
from sqlalchemy.orm import Session, contains_eager, joinedload, raiseload
from sqlalchemy     import distinct, func, desc, cast, Date, and_, or_
from pydantic       import BaseModel, AnyUrl, Field
from typing         import List, Optional, Dict ,Union

router = APIRouter(
    prefix="/influencer",
    tags=["influencer"],
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
    all         = "all"
    one_weeks   = "first_week"
    two_weeks   = "two_weeks"
    three_weeks = "three_weeks"
    four_weeks  = "four_weeks"

class InfluencerBase(BaseModel):
    id            : int               = Field(None)                
    full_name     : str               = Field(None)
    created_at    : datetime.datetime = Field(None)     
    company_id    : int               = Field(None) 
    name          : str               = Field(None)
    profile_image : AnyUrl            = Field(None)    
    updated_at    : datetime.datetime = Field(None)

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

class InfluencerSchema(BaseModel):
    Influencer              : InfluencerBase = Field(None)
    average_like            : int            = Field(None)
    average_comment         : int            = Field(None)  
    average_hashtag         : int            = Field(None)  
    average_exposure        : int            = Field(None)
    average_female_follower : int            = Field(None)
    average_male_follower   : int            = Field(None)
    official_visit          : int            = Field(None)
    official_referrer       : int            = Field(None)

    class Config:
        orm_mode = True

class InfluencerHashtagPerformanceBase(BaseModel):
    tags     : List[str] = Field(None)
    likes    : List[int] = Field(None)
    comments : List[int] = Field(None)

class InfluencerExposurePerformanceBase(BaseModel):
    tags     : List[str] = Field(None)
    exposure : List[int] = Field(None)
    hashtag  : List[int] = Field(None)

class InfluencerReactionConversionPerformanceBase(BaseModel):
    tags              : List[str] = Field(None)
    official_visit    : List[int] = Field(None)
    official_referrer : List[int] = Field(None)

class InfluencerCampaignExposurePerformanceBase(BaseModel):
    created_at : List[datetime.datetime] = Field(None)
    hashtag    : List[int] = Field(None)

class InfluencerOfficialReferrerPerformanceBase(BaseModel):
    created_at        : List[datetime.datetime] = Field(None)
    official_referrer : List[int] = Field(None)

class GraphSchema(BaseModel):
    influencer_hashtag_performance             : InfluencerHashtagPerformanceBase
    influencer_exposure_performance            : InfluencerExposurePerformanceBase
    influencer_reaction_conversion_performance : InfluencerReactionConversionPerformanceBase
    influencer_campaign_exposure_performance   : InfluencerCampaignExposurePerformanceBase
    influencer_official_referrer_performance   : InfluencerOfficialReferrerPerformanceBase


@router.get("/", response_model = List[InfluencerSchema])
async def influencer_performance(status_filter: StatusFilter, influencer_id: int = None, db: Session = Depends(get_db)):
    influencers = db.query(models.Influencer, 
        func.avg(models.Insight.like).label('average_like'), 
        func.avg(models.Insight.comment).label('average_comment'), 
        func.avg(models.Insight.hashtag).label('average_hashtag'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.female_follower).label('average_female_follower'),
        func.avg(models.Insight.male_follower).label('average_male_follower'),
        func.avg(models.Insight.official_visit).label('official_visit'),
        func.avg(models.Insight.official_referrer).label('official_referrer')). \
        group_by(models.Influencer). \
        filter(and_(models.InfluencerPost.campaign_id != None, 
                    models.Insight.influencer_id == models.Influencer.id))
    campaigns = db.query(models.Campaign)

    if influencer_id:
        influencers = influencers.filter(models.Influencer.id == influencer_id)

    if status_filter == StatusFilter.one_weeks:
        influencers = influencers.join(models.Insight).join(models.InfluencerPost).filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=6))))
        
    if status_filter == StatusFilter.two_weeks:
        influencers = influencers.join(models.Insight).join(models.InfluencerPost).filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=13))))
        
    if status_filter == StatusFilter.three_weeks:
        influencers = influencers.join(models.Insight).join(models.InfluencerPost).filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=20))))
        
    if status_filter == StatusFilter.four_weeks:
        influencers = influencers.join(models.Insight).join(models.InfluencerPost).filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=27))))
        
    return influencers.all()

@router.get("/campaign", response_model=List[CampaignBase])
async def influencer_performance(influencer_id: int = None, db: Session = Depends(get_db)):
    campagins = db.query(models.Campaign). \
        filter(and_(models.Influencer.id == influencer_id, 
                    models.InfluencerPost.influencer_id == models.Influencer.id, 
                    models.InfluencerPost.campaign_id == models.Campaign.id))

    return campagins.all()

@router.get("/campaign_completion", response_model=List[CampaignBase])
async def influencer_performance(influencer_id: int = None, db: Session = Depends(get_db)):
    campagins = db.query(models.Campaign). \
        filter(and_(models.Influencer.id == influencer_id, 
                    models.InfluencerPost.influencer_id == models.Influencer.id, 
                    models.InfluencerPost.campaign_id == models.Campaign.id),
                    models.Campaign.end_at <= cast(datetime.datetime.now(), Date))

    return campagins.all()

@router.get("/graph", response_model=List[GraphSchema])
async def influencer_graph(status_filter: StatusFilter, influencer_id: int = None, db: Session = Depends(get_db)):
    try: 
        influencer_posts = db.query(models.InfluencerPost,
            func.avg(models.Insight.like).label('average_like'),
            func.avg(models.Insight.comment).label('average_comment'),
            func.avg(models.Insight.hashtag).label('average_hashtag'),
            func.avg(models.Insight.exposure).label('average_exposure'),
            func.avg(models.Insight.official_visit).label('official_visit'),
            func.avg(models.Insight.official_referrer).label('official_referrer')). \
            group_by(models.InfluencerPost.id). \
            filter(models.Insight.influencer_post_id == models.InfluencerPost.id)

        insights = db.query(models.Insight). \
            join(models.InfluencerPost). \
            filter(and_(models.Insight.influencer_post_id == models.InfluencerPost.id, models.InfluencerPost.campaign_id != None))
        
        campaigns = db.query(models.Campaign)

        if influencer_id:
            influencer_posts = influencer_posts.filter(models.InfluencerPost.influencer_id == influencer_id)
            insights         = insights.filter(models.Insight.influencer_id == influencer_id)
        
        if status_filter == StatusFilter.one_weeks:
            influencer_posts = influencer_posts.filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=6))))
            insights         = insights.filter(models.Insight.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=6))))

        if status_filter == StatusFilter.two_weeks:
            influencer_posts = influencer_posts.filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=13))))
            insights         = insights.filter(models.Insight.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=13))))
        
        if status_filter == StatusFilter.three_weeks:
            influencer_posts = influencer_posts.filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=20))))
            insights         = insights.filter(models.Insight.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=20))))

        if status_filter == StatusFilter.four_weeks:
            influencer_posts = influencer_posts.filter(models.InfluencerPost.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=27))))
            insights         = insights.filter(models.Insight.created_at.between(campaigns[0].created_at, (campaigns[0].created_at + datetime.timedelta(days=27))))
        
        df_campaign_tag_post_insight = pd.read_sql(insights.statement, engine)
        df_influencer_post           = pd.read_sql(influencer_posts.statement, engine)

        average_campaign_tag_post_insight = df_campaign_tag_post_insight. \
            groupby(df_campaign_tag_post_insight['created_at'], as_index=False).mean()
        average_influencer_post           = df_influencer_post. \
            groupby(df_influencer_post['tag'], as_index=False).mean().head(4)

        graph = [
                    {
                        "influencer_hashtag_performance" : {
                        "tags"     : average_influencer_post['tag'].tolist(),
                        "likes"    : average_influencer_post['average_like'].tolist(),
                        "comments" : average_influencer_post['average_comment'].tolist(),
                        },
                        "influencer_exposure_performance" : {
                        "tags"     : average_influencer_post['tag'].tolist(),
                        "exposure" : average_influencer_post['average_exposure'].tolist(),
                        "hashtag"  : average_influencer_post['average_hashtag'].tolist(),
                        },
                        "influencer_reaction_conversion_performance" : {
                        "tags"              : average_influencer_post['tag'].tolist(),
                        "official_visit"    : average_influencer_post['official_visit'].tolist(),
                        "official_referrer" : average_influencer_post['official_referrer'].tolist(),
                        },
                        "influencer_campaign_exposure_performance" : {
                        'created_at' : average_campaign_tag_post_insight['created_at'].tolist(),
                        'hashtag'    : average_campaign_tag_post_insight['hashtag'].tolist(),
                        },
                        "influencer_official_referrer_performance" : {
                        'created_at' : average_campaign_tag_post_insight['created_at'].tolist(),
                        'official_referrer': average_campaign_tag_post_insight['official_referrer'].tolist()
                        }
                    }
                ]
        
        return graph
    except KeyError:
        raise HTTPException(status_code=400, detail="Key not found")
