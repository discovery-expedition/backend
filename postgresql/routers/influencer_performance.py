from email import header
from genericpath import exists
from ntpath import join
from operator import and_
from pyexpat import model
import sys
from unittest import result

from pymysql import Date
sys.path.append("..")
import models, datetime
from datetime import date
from enum import Enum
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from database import engine, SessionLocal
from sqlalchemy.orm import Session, contains_eager, joinedload, aliased, subqueryload, lazyload
from sqlalchemy import column, distinct, func, desc, null, cast, Date, text
#from sqlalchemy.sql import select
from pydantic import BaseModel, Field
from sqlalchemy.sql.expression import  alias

import pandas as pd
import json
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/influencer",
    tags=["influencer"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

class StatusFilter(str, Enum):
    all        = "all"
    proceeding = "proceeding"
    completion = "completion"

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/")
async def abc(db: Session = Depends(get_db)):
    return db.query(models.Influencer).all()

@router.get("/searchs")
async def abc(keyword: Optional[str], db: Session = Depends(get_db)):
    Influencers = db.query(models.Influencer, \
        func.avg(models.Insight.like).label('average_like'), \
        func.avg(models.Insight.comment).label('average_comment'), \
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.female_follower).label('average_female_follower'),
        func.avg(models.Insight.male_follower).label('average_male_follower')) \
        .select_from(models.Influencer) \
        .group_by(models.Influencer) \
        .group_by(models.Campaign.end_at) \
        .outerjoin(models.InfluencerPost) \
        .outerjoin(models.Insight) \
        .outerjoin(models.Campaign) \
        .options(joinedload("influencer_posts"), joinedload("influencer_posts.campaign")) \
        .filter(models.Influencer.name.contains(keyword))\
        .order_by(desc(models.Campaign.end_at))
    
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

@router.get("/yoyo")
async def abc(status_filter: StatusFilter, campaign_id: int = None, db: Session = Depends(get_db)):
    '''
    campaigns = db.query(models.Campaign, 
        func.count(distinct(models.InfluencerPost.id)).label('count_post'), 
        func.count(distinct(models.InfluencerPost.influencer_id)).label('count_influencer'),
        func.sum(models.Insight.hashtag).label('sum_hashtag'),
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment')). \
        select_from(models.Campaign). \
        join(models.InfluencerPost). \
        join(models.Insight). \
        group_by(models.Campaign.id). \
        group_by(models.Insight.created_at). \
        order_by(models.Insight.created_at). \
        having(cast(models.Insight.created_at, Date) == cast(datetime.datetime.now(), Date))
    '''

    campaigns = db.query(models.Campaign,
        func.count(distinct(models.InfluencerPost.id)).label('count_post'), 
        func.count(distinct(models.InfluencerPost.influencer_id)).label('count_influencer'),
        func.sum(models.Insight.hashtag).label('sum_hashtag'),
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment'),
        func.sum(models.Insight.official_visit).label('total_official_visit'),
        func.sum(models.Insight.official_follower).label('total_official_follower'),
        func.sum(models.Insight.official_referrer).label('total_official_referrer')). \
        select_from(models.Campaign). \
        group_by(models.Campaign.id)

    insights = db.query(models.Insight).filter(models.Insight.influencer_post_id == models.InfluencerPost.id, models.InfluencerPost.campaign_id == campaign_id)

    
    insights_lol = pd.read_sql(insights.statement, engine)
    date_graph          = insights_lol['created_at'].tolist()
    #options(joinedload('influencer_posts.insights')). \
    #check = date.today() - models.Campaign.created_at
    #check = (datetime.utcnow() - models.Campaign.created_at).days
    check = db.query(models.Campaign.created_at)

    check1 = (datetime.datetime.now() - check[0][0]).days


    '''
    d0 = date(2008, 8, 18)
    d1 = date(2008, 9, 26)
    delta = d1 - d0
    print(delta.days)
    '''
    yesterday = campaigns.filter(cast(models.Insight.created_at, Date) == cast((datetime.datetime.now() - datetime.timedelta(days=1)), Date))
    campaigns = campaigns.filter(cast(models.Insight.created_at, Date) == cast(datetime.datetime.now(), Date))

    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.utcnow() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.utcnow() < models.Campaign.end_at)

    if campaign_id:
        campaigns = campaigns.filter(models.Campaign.id == campaign_id)
    '''
    mycampaigns = db.query(models.Insight). \
        select_from(models.Campaign). \
        join(models.InfluencerPost). \
        group_by(models.Insight.id, models.InfluencerPost.id).filter(models.InfluencerPost.campaign_id == campaign_id, models.Influencer.id == models.Insight.influencer_post_id)
    '''
    graph = campaigns#[0][0].influencer_posts[22].insights
    #www = len(campaigns[0][0].influencer_posts)
    
    df = pd.DataFrame(graph)
    
    #df = pd.DataFrame(campaigns)
    dfff = df.values.tolist()
    lol = pd.read_sql(campaigns.statement, engine)
    lol2 = lol.columns.tolist()
    #ssss = pd.MultiIndex.from_arrays(campaigns)
    #asadf = ssss.reindex(ssss)
    #lol3 = pd.read_sql(ffff, engine)
    #sadf3 = lol3['created_at'].tolist()
    #date_graph = lol['influencer_posts']['insights']['created_at'].tolist()
    '''
    campaigns_graph = campaigns.filter(datetime.datetime.utcnow() < models.Campaign.end_at).order_by(desc(models.Campaign.end_at)).limit(5)
    lol = pd.read_sql(campaigns_graph.statement, engine)


    date_graph          = lol['created_at'].tolist()
    total_hashtag_graph = lol['sum_hashtag'].tolist()
    count_post_graph    = lol['count_post'].tolist()
    official_visit      = lol['average_comment'].tolist()
    official_follower   = lol['total_official_visit'].tolist()
    official_referrer   = lol['total_official_referrer'].tolist()
    campaign_name       = lol['name'].tolist()

    graph = {
        "date_graph"                    : date_graph,
        "total_hashtag_graph"           : total_hashtag_graph,
        "count_post_graph"              : count_post_graph,
        "official_visit"                : official_visit,
        "official_follower"             : official_follower,
        "official_referrer"             : official_referrer,
        "campaign_name"                 : campaign_name,
    }
    '''

    results = [{
        "id"                   : campaign[0].id,
        "name"                 : campaign[0].name,
        "tag"                  : campaign[0].tag,
        "description"          : campaign[0].description,
        "end_at"               : campaign[0].end_at,
        "image"                : campaign[0].image,
        "created_at"           : campaign[0].created_at,
        "updated_at"           : campaign[0].updated_at,
        "average_like"         : int(campaign.average_like),
        "average_exposure"     : int(campaign.average_exposure),
        "average_comment"      : int(campaign.average_comment),
        "average_participation": int((campaign.average_like) + (campaign.average_comment)),
        "count_influencer"     : campaign.count_influencer,
        "hashtag"              : campaign.sum_hashtag,
        #"hashtag_compared_to_yesterday1": round((campaign.sum_hashtag / yesterday[campaign_id - 1].sum_hashtag * 100), 2) - 100 if campaign.sum_hashtag <= yesterday[campaign_id - 1].sum_hashtag else round(campaign.sum_hashtag / yesterday[campaign_id - 1].sum_hashtag * 100, 2),
        "count_post"           : campaign.count_post,
        "official_visit"       : campaign.total_official_visit,
        "official_follower"    : campaign.total_official_follower,
        "official_referrer"    : campaign.total_official_referrer,
        "campaign_status"      : "완료" if datetime.datetime.utcnow() >= campaign[0].end_at else "진행 중",
        "hashtag_compared_to_yesterday": 
            round((campaign.sum_hashtag / yesterday[campaign[0].id - 1].sum_hashtag * 100) - 100, 2) 
            if campaign.sum_hashtag <= yesterday[campaign[0].id - 1].sum_hashtag 
            else round(campaign.sum_hashtag / yesterday[campaign[0].id - 1].sum_hashtag * 100, 2),
        "count_post_compared_to_yesterday": 
            round((campaign.count_post / yesterday[campaign[0].id - 1].count_post * 100) - 100, 2) 
            if campaign.count_post <= yesterday[campaign[0].id - 1].count_post 
            else round(campaign.count_post / yesterday[campaign[0].id - 1].count_post * 100, 2),
        "total_official_visit_compared_to_yesterday": 
            round((campaign.total_official_visit / yesterday[campaign[0].id - 1].total_official_visit * 100) - 100, 2) 
            if campaign.total_official_visit <= yesterday[campaign[0].id - 1].total_official_visit 
            else round(campaign.total_official_visit / yesterday[campaign[0].id - 1].total_official_visit * 100, 2),
        "total_official_follower_compared_to_yesterday": 
            round((campaign.total_official_follower / yesterday[campaign[0].id - 1].total_official_follower * 100) - 100, 2) 
            if campaign.total_official_follower <= yesterday[campaign[0].id - 1].total_official_follower 
            else round(campaign.total_official_follower / yesterday[campaign[0].id - 1].total_official_follower * 100, 2),
        "total_official_referrer_compared_to_yesterday": 
            round((campaign.total_official_referrer / yesterday[campaign[0].id - 1].total_official_referrer * 100) - 100, 2) 
            if campaign.total_official_referrer <= yesterday[campaign[0].id - 1].total_official_referrer 
            else round(campaign.total_official_referrer / yesterday[campaign[0].id - 1].total_official_referrer * 100, 2),
        "asd": datetime.datetime.today()
    } for campaign in campaigns]
    print(type(graph))
    print(type(campaigns))
    print(type(campaigns.statement))
    print(insights_lol)
    return #, check[0][0], check1, check.all(), mycampaigns.all(), graph, lol2, campaigns.all()#, results, campaigns[0][0].influencer_posts[0].insights#, yesterday[5].sum_hashtag

@router.get("/yooo")
async def abc(status_filter: StatusFilter, campaign_id: int = None, db: Session = Depends(get_db)):
    '''
    influencerpost1 = aliased(models.InfluencerPost)
    campaign1       = aliased(models.Campaign)
    campaigns = db.query(models.Campaign, \
        func.sum(models.Insight.hashtag).label('sum_hashtag'), \
        func.count(models.InfluencerPost.id).label('count_post')) \
        .select_from(models.Campaign) \
        .group_by(models.Campaign.id) \
        .join(models.InfluencerPost) \
        .join(models.Insight) \
        .options(joinedload('influencer_posts')) \
        .filter(models.Campaign.id == campaign_id, models.Campaign.id == models.InfluencerPost.campaign_id).all()
    asd = db.query(func.count(models.InfluencerPost.id).label('asd')).filter(models.Campaign.id == campaign_id, models.Campaign.id == models.InfluencerPost.campaign_id)
    
    qqq = db.query(models.Campaign) \
        .join(models.InfluencerPost) \
        .join(models.Insight) \
        .options(joinedload('influencer_posts')) \
        .filter(models.Campaign.id == campaign_id).all()
    www = db.query(
        func.sum(models.Insight.hashtag).label('sum_hashtag'), \
        func.count(models.InfluencerPost.tag).label('count_post')).all()
    '''

    '''
    campaigns = db.query(models.Campaign, \
        func.sum(models.Insight.hashtag).label('sum_hashtag'), \
        func.count(models.InfluencerPost.tag).label('count_post')) \
        .select_from(models.Campaign) \
        .group_by(models.Campaign.id) \
        .options(joinedload('influencer_posts')) \
        .filter(models.Campaign.id == campaign_id).all()
    '''
    campaignss = db.query(models.Campaign, 
        func.count(models.InfluencerPost.id).label('count_post'), 
        func.count(distinct(models.InfluencerPost.influencer_id)).label('count_influencer')). \
        join(models.InfluencerPost). \
        filter(models.Campaign.id == campaign_id). \
        group_by(models.Campaign.id).all()
    
    influencer_posts = db.query(models.InfluencerPost, 
        func.sum(models.Insight.hashtag).label('sum_hashtag'),
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment')). \
        join(models.Insight). \
        group_by(models.InfluencerPost.id). \
        filter(models.InfluencerPost.campaign_id == campaign_id) \
    


    ggg = db.query(models.Campaign,
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment')) \
        .select_from(models.Campaign) \
        .group_by(models.Campaign.id) \
        .options(joinedload('influencer_posts')) \
        .filter(models.Campaign.id == campaign_id, models.Campaign.id == models.InfluencerPost.campaign_id)


    campaigns = db.query(models.Campaign, 
        func.count(distinct(models.InfluencerPost.id)).label('count_post'), 
        func.count(distinct(models.InfluencerPost.influencer_id)).label('count_influencer'),
        func.sum(models.Insight.hashtag).label('sum_hashtag'),
        func.avg(models.Insight.like).label('average_like'),
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.comment).label('average_comment'),
        func.sum(models.Insight.official_visit).label('total_official_visit'),
        func.sum(models.Insight.official_follower).label('total_official_follower'),
        func.sum(models.Insight.official_referrer).label('total_official_referrer')). \
        select_from(models.Campaign). \
        join(models.InfluencerPost). \
        join(models.Insight). \
        group_by(models.Campaign.id)

    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.utcnow() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.utcnow() < models.Campaign.end_at)

    if campaign_id:
        campaigns = campaigns.filter(models.Campaign.id == campaign_id)
    df = pd.read_sql(campaigns.statement, engine).to_json()
    ff = pd.read_sql(campaigns.statement, engine).values.tolist()
    gg = pd.read_sql(campaigns.statement, engine)

    campaigns_graph = campaigns.filter(datetime.datetime.utcnow() >= models.Campaign.end_at).order_by(desc(models.Campaign.end_at)).limit(5)
    lol = pd.read_sql(campaigns_graph.statement, engine)


    date_graph          = lol['created_at'].tolist()
    total_hashtag_graph = lol['sum_hashtag'].tolist()
    count_post_graph    = lol['count_post'].tolist()
    official_visit      = lol['average_comment'].tolist()
    official_follower   = lol['total_official_visit'].tolist()
    official_referrer   = lol['total_official_referrer'].tolist()
    campaign_name       = lol['name'].tolist()
    '''
    total_hashtag_graph = gg['total_hashtag'].tolist()
    count_post_graph    = gg['count_post'].tolist()
    official_visit      = gg['official_visit'].tolist()
    official_follower   = gg['official_follower'].tolist()
    official_referrer   = gg['official_referrer'].tolist()
    '''
    #gg['created_at'].tolist()

    '''
    count            = 0
    total_hashtag    = 0
    average_like     = 0
    average_exposure = 0
    average_comment  = 0

    for i in influencer_posts:
        total_hashtag += i.sum_hashtag
        average_like  += i.average_like
        average_exposure += i.average_exposure
        average_comment += i.average_comment
        count += 1
    '''
    
    results = [{
        "id"                            : campaign[0].id,
        "name"                          : campaign[0].name,
        "tag"                           : campaign[0].tag,
        "description"                   : campaign[0].description,
        "end_at"                        : campaign[0].end_at,
        "image"                         : campaign[0].image,
        "created_at"                    : campaign[0].created_at,
        "updated_at"                    : campaign[0].updated_at,
        "average_like"                  : int(campaign.average_like),
        "average_comment"               : int(campaign.average_comment),
        "average_exposure"              : int(campaign.average_exposure),        
        "average_participation"         : int((campaign.average_like) + (campaign.average_comment)),
        "participated_influencer_count" : campaign.count_influencer,
        "budget"                        : campaign[0].budget,
        "total_hashtag"                 : campaign.sum_hashtag,
        "count_post"                    : campaign.count_post,
        "official_visit"                : campaign.total_official_visit,
        "official_follower"             : campaign.total_official_follower,
        "official_referrer"             : campaign.total_official_referrer,
        "campaign_status"               : "완료" if datetime.datetime.utcnow() >= campaign[0].end_at else "진행 중",
    } for campaign in campaigns]

    graph = {
        "date_graph"                    : date_graph,
        "total_hashtag_graph"           : total_hashtag_graph,
        "count_post_graph"              : count_post_graph,
        "official_visit"                : official_visit,
        "official_follower"             : official_follower,
        "official_referrer"             : official_referrer,
        "campaign_name"                 : campaign_name,
    }

    '''
    "total_hashtag_graph"           : total_hashtag_graph,
    "count_post_graph"              : count_post_graph,
    "official_visit"                : official_visit,
    "official_follower"             : official_follower,
    "official_referrer"             : official_referrer,
    '''
    '''
    results_1 = [{
        "id"              : campaign[0].id,
        "name"            : campaign[0].name,
        "tag"             : campaign[0].tag,
        "description"     : campaign[0].description,
        "end_at"          : campaign[0].end_at,
        "image"           : campaign[0].image,
        "created_at"      : campaign[0].created_at,
        "updated_at"      : campaign[0].updated_at,
        "average_like"    : int(average_like / count),
        "average_exposure": int(average_exposure / count),
        "average_comment" : int(average_comment / count),
        "average_participation": int((average_like / count) + (average_comment / count)),
        "count_influencer": campaign.count_influencer,
        "total_hashtag"   : total_hashtag,
        "count_post"      : campaign.count_post,
    } for campaign in campaigns]
    '''
    '''
    results = [{
        "id"              : campaign[0].id,
        "name"            : campaign[0].name,
        "tag"             : campaign[0].tag,
        "description"     : campaign[0].description,
        "end_at"          : campaign[0].end_at,
        "image"           : campaign[0].image,
        "created_at"      : campaign[0].created_at,
        "updated_at"      : campaign[0].updated_at,
        "average_like"    : int(campaign.sum_hashtag),
        "average_comment" : campaign.count_post,
    } for campaign in campaigns]
    '''
    return results, graph #, JSONResponse(content=jsonable_encoder(df)), ff, gg['created_at'].tolist(), gg['average_comment'].tolist()
    
@router.get("/search/{status_filter}")
async def abc(status_filter: StatusFilter, q: Optional[str] = None,  db: Session = Depends(get_db)):
    '''
    campaigns = db.query(models.Campaign) \
        .outerjoin(models.InfluencerPost.insights) \
        .options(contains_eager("influencer_posts"), \
                 contains_eager("influencer_posts.insights"))\
        .all()
    db_influencer_posts = db.query(models.InfluencerPost).outerjoin("insights").options(contains_eager("insights")).all()
    '''

    campaigns = db.query(models.Campaign, \
        func.avg(models.Insight.like).label('average_like'), \
        func.avg(models.Insight.comment).label('average_comment'), \
        func.avg(models.Insight.exposure).label('average_exposure'),
        func.avg(models.Insight.female_follower).label('average_female_follower'),
        func.avg(models.Insight.male_follower).label('average_male_follower')) \
        .select_from(models.Campaign) \
        .group_by(models.Campaign.id) \
        .join(models.InfluencerPost) \
        .join(models.Insight) \
        .order_by(desc(models.Campaign.end_at))
        
    if status_filter == StatusFilter.completion:
        campaigns = campaigns.filter(datetime.datetime.utcnow() >= models.Campaign.end_at)
    
    if status_filter == StatusFilter.proceeding:
        campaigns = campaigns.filter(datetime.datetime.utcnow() < models.Campaign.end_at)
    
    if q:
        campaigns = campaigns.filter(models.Campaign.name.contains(q))
    
    
    
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

    '''
    campaignss = db.query(models.Campaign) \
        .outerjoin(models.InfluencerPost) \
        .join(models.InfluencerPost.insights) \
        .options(contains_eager("influencer_posts"), \
                 contains_eager("influencer_posts.insights"))\
        .filter(models.Campaign.name.contains(keyword)).all()
    '''

    return results

@router.get("/{influencer_id}")
async def abc(influencer_id: int, db: Session = Depends(get_db)):
    insights_influencer = db.query(models.Insight).filter(models.Insight.influencer_id == influencer_id).all()
    #insights_tag = db.query(models.Insight.influencer_post).filter(models.Insight.influencer_post.id == influencer_id).all()
    #insights_tag = db.query(models.Insight).join(models.InfluencerPost).join(models.Campaign).options(contains_eager("influencer_post"), contains_eager("influencer_post.campaign")).filter(models.Insight.influencer_post.influencer_id == influencer_id).all()
    #insights_tag = db.query(models.Insight).join(models.InfluencerPost).join(models.Campaign).options(
    #    contains_eager("influencer_post"), contains_eager("influencer_post.campaign")).filter(
    #    models.InfluencerPost.influencer_id == influencer_id).all()
    #insights_tag = db.query(models.Influencer).outerjoin(models.Insight).options(contains_eager('insights')).filter(models.Insight.influencer_id == influencer_id).all()
    insights_tag = db.query(models.Influencer) \
                    .join(models.Insight) \
                    .join(models.InfluencerPost) \
                    .join(models.InfluencerPost.campaign) \
                    .options(contains_eager('insights'), contains_eager('influencer_posts'), contains_eager('influencer_posts.campaign')) \
                    .filter(models.Insight.influencer_id == influencer_id).all()
    total  = insights_influencer[-1].male_follower + insights_influencer[-1].female_follower
    male   = insights_influencer[-1].male_follower / total * 100
    female = insights_influencer[-1].female_follower / total * 100
    return {"male": round(male), "female": round(female)}, insights_tag
