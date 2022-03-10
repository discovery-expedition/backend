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
    created_at         = Column(DateTime, nullable=False, default=func.utc_timestamp())
    influencer_post_id = Column(ForeignKey('influencer_posts.id'))
    influencer_id      = Column(ForeignKey('influencers.id'))

    influencer = relationship('Influencer', primaryjoin='Insight.influencer_id == Influencer.id', backref='insights')
    influencer_post = relationship('InfluencerPost', primaryjoin='Insight.influencer_post_id == InfluencerPost.id',
                                      backref='insights')

class InfluencerPost(Base):
    __tablename__ = 'influencer_posts'

    id            = Column(String)
    url           = Column(URLType)
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
    name       = Column(String)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

class Influencer(Base):
    __tablename__ = "influencers"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String)
    full_name     = Column(String)
    profile_image = Column(URLType)
    created_at    = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at    = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    company_id    = Column(Integer, ForeignKey('companies.id'))

    company = relationship('Company', primaryjoin='Influencer.company_id == Company.id', backref='influencers')

class Campaign(Base):
    __tablename__ = "campaigns"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)
    tag         = Column(String)
    description = Column(String)
    end_at      = Column(DateTime)
    created_at  = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at  = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

class SocialNetworkService(Base):
    __tablename__ = "social_network_services"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())








