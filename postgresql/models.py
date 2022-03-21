from numpy import integer
from sqlalchemy          import Column, Integer, String, ForeignKey, Table, DateTime, func
from sqlalchemy_utils    import URLType
from sqlalchemy.orm      import relationship
from database import Base

class SnsInfo(Base):
    __tablename__ = 'sns_infos'

    id                        = Column(Integer, primary_key=True, index=True)
    post                      = Column(Integer)
    url                       = Column(URLType)
    created_at                = Column(DateTime, nullable=False, default=func.utc_timestamp())
    social_network_service_id = Column(ForeignKey('social_network_services.id'))
    influencer_id             = Column(ForeignKey('influencers.id'))
    influencer                = relationship('Influencer',
                                             primaryjoin='SnsInfo.influencer_id == Influencer.id',
                                             backref='sns_infos')
    social_network_service    = relationship('SocialNetworkService',
                                             primaryjoin='SnsInfo.social_network_service_id == SocialNetworkService.id',
                                             backref='sns_infos')

class Insight(Base):
    __tablename__ = 'insights'

    id                 = Column(Integer, primary_key=True, index=True)
    search_frequency   = Column(Integer)
    visit_frequency    = Column(Integer)
    like               = Column(Integer)
    comment            = Column(Integer)
    male_follower      = Column(Integer)
    female_follower    = Column(Integer)
    bookmark           = Column(Integer)
    exposure           = Column(Integer)
    profile            = Column(Integer)
    profile_visit      = Column(Integer)
    website_click      = Column(Integer)
    hashtag            = Column(Integer)
    reaction           = Column(Integer)
    home               = Column(Integer)
    official_visit     = Column(Integer)
    official_follower  = Column(Integer)
    official_referrer  = Column(Integer)
    created_at         = Column(DateTime, nullable=False, default=func.utc_timestamp())
    influencer_post_id = Column(ForeignKey('influencer_posts.id'))
    influencer_id      = Column(ForeignKey('influencers.id'))

    influencer = relationship('Influencer', primaryjoin='Insight.influencer_id == Influencer.id', backref='insights')
    influencer_post = relationship('InfluencerPost', primaryjoin='Insight.influencer_post_id == InfluencerPost.id',
                                      backref='insights')

class InfluencerPost(Base):
    __tablename__ = 'influencer_posts'

    id            = Column(Integer, primary_key=True, index=True)
    tag           = Column(String(length=(50)))
    url           = Column(URLType)
    created_at    = Column(DateTime, nullable=False, default=func.utc_timestamp())
    campaign_id   = Column(ForeignKey('campaigns.id'))
    influencer_id = Column(ForeignKey('influencers.id'))    

    campaign = relationship('Campaign', primaryjoin='InfluencerPost.campaign_id == Campaign.id',
                               backref='influencer_posts')
    influencer = relationship('Influencer', primaryjoin='InfluencerPost.influencer_id == Influencer.id',
                                 backref='influencer_posts')

class Performance(Base):
    __tablename__ = "performances"

    id         = Column(Integer, primary_key=True, index=True)
    sale       = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    company_id = Column(Integer, ForeignKey('companies.id'))
    company    = relationship('Company', primaryjoin='Performance.company_id == Company.id', backref='performances')

class Company(Base):
    __tablename__ = "companies"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(length=(50)))
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

class Influencer(Base):
    __tablename__ = "influencers"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(length=(50)))
    full_name     = Column(String(length=(50)))
    profile_image = Column(URLType)
    created_at    = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at    = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    company_id    = Column(Integer, ForeignKey('companies.id'))

    company = relationship('Company', primaryjoin='Influencer.company_id == Company.id', backref='influencers')

class Campaign(Base):
    __tablename__ = "campaigns"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(length=(50)))
    tag         = Column(String(length=(50)))
    description = Column(String(length=(500)))
    end_at      = Column(DateTime)
    image       = Column(URLType)
    budget      = Column(Integer)
    created_at  = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at  = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

class SocialNetworkService(Base):
    __tablename__ = "social_network_services"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(length=(50)))
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True)
    username        = Column(String, unique=True, index=True)
    first_name      = Column(String)
    last_name       = Column(String)
    hashed_password = Column(String)







