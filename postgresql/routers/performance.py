import sys
sys.path.append("..")
import models, datetime
import pandas as pd
from enum           import Enum
from pymysql        import Date
from fastapi        import APIRouter, Depends
from database       import engine, SessionLocal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy     import distinct, func, desc, cast, Date, and_
from pydantic       import BaseModel, AnyUrl, Field
from typing         import List, Optional, Dict ,Union

router = APIRouter(
    prefix="/performance",
    tags=["performance"],
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

class ProceedingGraph(BaseModel):
    date_graph              : List[datetime.datetime] = Field(None)                
    hashtag_graph           : List[int]               = Field(None)
    post_date               : List[datetime.datetime] = Field(None)
    count_post              : List[int]               = Field(None)
    daily_official_visit    : List[int]               = Field(None)  
    daily_official_follower : List[int]               = Field(None)  
    daily_official_referrer : List[int]               = Field(None)  
    sales_graph             : List[int]               = Field(None)

class CompletionGraph(BaseModel):
    date_graph              : List[datetime.datetime] = Field(None)                
    hashtag_graph           : List[int]               = Field(None)
    count_post              : List[int]               = Field(None)
    total_official_visit    : List[int]               = Field(None)  
    total_official_follower : List[int]               = Field(None)  
    total_official_referrer : List[int]               = Field(None)  
    sales_graph             : List[int]               = Field(None)   
    campaign_name           : List[str]               = Field(None)

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

class TodayPostCountSchema(BaseModel):
    count_post : int = Field(None)
    class Config:
        orm_mode = True

class CampaignSchema(BaseModel):
    Campaign         : CampaignBase = Field(None)
    average_hashtag  : int          = Field(None)
    average_like     : int          = Field(None)
    average_exposure : int          = Field(None)
    average_comment  : int          = Field(None)

    class Config:
        orm_mode = True

class ProceedingSchema(CampaignSchema):
    daily_official_visit    : int = Field(None)
    daily_official_follower : int = Field(None)
    daily_official_referrer : int = Field(None)

class CompletionSchema(CampaignSchema):
    total_official_visit    : int = Field(None)
    total_official_follower : int = Field(None)
    total_official_referrer : int = Field(None)

@router.get("/post_count", response_model=List[TodayPostCountSchema])
async def post_count(status_filter: StatusFilter, campaign_id: int = None, db: Session = Depends(get_db)):
    campaigns = db.query(models.Campaign, func.count(models.InfluencerPost.id).label("count_post")).\
        group_by(models.Campaign.id). \
        filter(and_(models.InfluencerPost.campaign_id != None), cast(models.InfluencerPost.created_at, Date) == cast(datetime.datetime.now(), Date) - datetime.timedelta(days=1)).distinct(func.count(models.InfluencerPost.id).label("count_post"))

    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.now() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.now() < models.Campaign.end_at)

    if campaign_id:
        campaigns = campaigns.filter(and_(models.Campaign.id == campaign_id, models.Campaign.id == models.InfluencerPost.campaign_id))

    return campaigns.all() if campaigns.all() != [] else [{"count_post" : 0}]

@router.get("/proceeding_graph", response_model = List[ProceedingGraph])
async def campaign_proceeding_graph(campaign_id: int = None, db: Session = Depends(get_db)):
    campaigns    = db.query(models.Campaign)
    insights     = db.query(models.Insight). \
            filter(and_(models.Insight.influencer_post_id == models.InfluencerPost.id, models.InfluencerPost.campaign_id != None))
    performances = db.query(models.Performance). \
        filter(models.Performance.created_at.between(campaigns[0].created_at, (datetime.datetime.now() - datetime.timedelta(days=1))))

    if campaign_id:
        insights  = insights.filter(models.InfluencerPost.campaign_id == campaign_id)
        campaigns = campaigns.filter(models.Campaign.id == campaign_id)
    
    influencer_posts = campaigns[0].influencer_posts

    df_campaign_tag_post_insight = pd.read_sql(insights.statement, engine)
    df_performances              = pd.read_sql(performances.statement, engine)
    df_influencer_post           = pd.DataFrame(i.__dict__ for i in influencer_posts)
    
    df_campaign_tag_post_insight = df_campaign_tag_post_insight. \
        loc[(df_campaign_tag_post_insight['created_at'] >= campaigns[0].created_at) & 
            (df_campaign_tag_post_insight['created_at'] < (datetime.datetime.now() - datetime.timedelta(days=1)))]

    sum_campaign_tag_post_insight = df_campaign_tag_post_insight. \
        groupby(df_campaign_tag_post_insight['created_at'], as_index=False).mean()
    count_post_date = df_influencer_post. \
        groupby(df_influencer_post['created_at'], as_index=False).count()
    count_post      = df_influencer_post. \
        groupby(df_influencer_post['created_at'].dt.date).count()
    
    graph = [{
        "date_graph"              : sum_campaign_tag_post_insight['created_at'].tolist(),
        "hashtag_graph"           : sum_campaign_tag_post_insight['hashtag'].tolist(),
        "post_date"               : count_post_date['created_at'].tolist(),
        "count_post"              : count_post['created_at'].tolist(),
        "daily_official_visit"    : sum_campaign_tag_post_insight['official_visit'].tolist(),
        "daily_official_follower" : sum_campaign_tag_post_insight['official_follower'].tolist(),
        "daily_official_referrer" : sum_campaign_tag_post_insight['official_referrer'].tolist(),
        "sales_graph"             : df_performances['sale'].tolist(),
    }]

    return graph

@router.get("/completion_graph", response_model=CompletionGraph)
async def campaign_completion_graph(campaign_id: int = None, db: Session = Depends(get_db)):
    campaigns = db.query(models.Campaign, 
        func.count(distinct(models.InfluencerPost.id)).label('count_post'), 
        func.count(distinct(models.InfluencerPost.influencer_id)).label('count_influencer'),
        func.avg(models.Insight.hashtag).label('average_hashtag'),
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment'),
        func.avg(models.Insight.official_visit).label('total_official_visit'),
        func.avg(models.Insight.official_follower).label('total_official_follower'),
        func.avg(models.Insight.official_referrer).label('total_official_referrer')). \
        select_from(models.Campaign). \
        join(models.InfluencerPost). \
        join(models.Insight). \
        group_by(models.Campaign.id)

    if campaign_id:
        campaigns = campaigns.filter(models.Campaign.id == campaign_id)
    
    performances = db.query(models.Campaign,
                func.sum(models.Performance.sale).label('total_sales')). \
                group_by(models.Campaign.id). \
                filter(and_(datetime.datetime.now() >= models.Campaign.end_at, 
                    models.Performance.created_at.between(models.Campaign.created_at, models.Campaign.end_at)))

    campaigns_graph = campaigns.filter(datetime.datetime.now() >= models.Campaign.end_at).order_by(desc(models.Campaign.end_at)).limit(5)

    df_performances = pd.read_sql(performances.statement, engine)
    df_campaign     = pd.read_sql(campaigns_graph.statement, engine)

    graph = {
        "date_graph"              : df_campaign['created_at'].tolist(),
        "hashtag_graph"           : df_campaign['average_hashtag'].tolist(),
        "count_post"              : df_campaign['count_post'].tolist(),
        "total_official_visit"    : df_campaign['total_official_visit'].tolist(),
        "total_official_follower" : df_campaign['total_official_follower'].tolist(),
        "total_official_referrer" : df_campaign['total_official_referrer'].tolist(),
        "sales_graph"             : df_performances['total_sales'].tolist(),
        "campaign_name"           : df_campaign['name'].tolist()
    }

    return graph
    
@router.get("/completion", response_model=List[CompletionSchema])
async def campaign_completion(status_filter: StatusFilter, campaign_id: int = None, db: Session = Depends(get_db)):
    campaigns = db.query(models.Campaign,
        func.count(distinct(models.InfluencerPost.id)).label('count_post'), 
        func.count(distinct(models.InfluencerPost.influencer_id)).label('count_influencer'),
        func.avg(models.Insight.hashtag).label('average_hashtag'),
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment'),
        func.avg(models.Insight.official_visit).label('total_official_visit'),
        func.avg(models.Insight.official_follower).label('total_official_follower'),
        func.avg(models.Insight.official_referrer).label('total_official_referrer')). \
        select_from(models.Campaign). \
        group_by(models.Campaign.id). \
        join(models.InfluencerPost). \
        join(models.Insight). \
        filter(and_(models.InfluencerPost.campaign_id != None, 
                    models.Campaign.id == models.InfluencerPost.campaign_id, 
                    models.InfluencerPost.id == models.Insight.influencer_post_id))
        

    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.now() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.now() < models.Campaign.end_at)

    if campaign_id:
        campaigns = campaigns.filter(models.Campaign.id == campaign_id)
        
    return campaigns.all()

@router.get("/proceeding", response_model=List[ProceedingSchema])
async def campaign_proceeding(status_filter: StatusFilter, campaign_id: int = None, db: Session = Depends(get_db)):
    campaigns = db.query(models.Campaign, 
        func.avg(models.Insight.hashtag).label('average_hashtag'),
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment'),
        func.avg(models.Insight.official_visit).label('daily_official_visit'),
        func.avg(models.Insight.official_follower).label('daily_official_follower'),
        func.avg(models.Insight.official_referrer).label('daily_official_referrer')). \
        group_by(models.Campaign.id). \
        filter(and_(models.InfluencerPost.campaign_id != None, 
                    models.Campaign.id == models.InfluencerPost.campaign_id, 
                    models.InfluencerPost.id == models.Insight.influencer_post_id,
                    cast(models.Insight.created_at, Date) == (cast(datetime.datetime.now(), Date)) - datetime.timedelta(days=1)))

    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.now() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.now() < models.Campaign.end_at)

    if campaign_id:
        campaigns = campaigns.filter(models.Campaign.id == campaign_id)
        
    return campaigns.all()

