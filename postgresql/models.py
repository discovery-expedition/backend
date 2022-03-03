from sqlalchemy          import Column, Integer, String, ForeignKey, Table, DateTime, func
from sqlalchemy_utils    import URLType
from sqlalchemy.orm      import relationship
from postgresql.database import Base

class SnsInfo(Base):
    __tablename__ = 'sns_info'

    id            = Column(Integer, primary_key=True, index=True)
    sns_id        = Column(ForeignKey('sns.id'))
    influencer_id = Column(ForeignKey('influencers.id'))
    post          = Column(Integer)
    url           = Column(URLType)
    created_at    = Column(DateTime, nullable=False, default=func.utc_timestamp())
    sns           = relationship("Sns", back_populates="sns")
    influencer    = relationship("Influencer", back_populates="influencers")

class Insight(Base):
    __tablename__ = 'insight'

    id                     = Column(Integer, primary_key=True, index=True)
    influencer_post_id     = Column(ForeignKey('influencer_post.id'))
    influencer_id          = Column(ForeignKey('influencers.id'))
    search_frequency       = Column(Integer)
    visit_frequency        = Column(Integer)
    like                   = Column(Integer)
    comment                = Column(Integer)
    male_follower          = Column(Integer)
    female_follower        = Column(Integer)
    bookmark               = Column(Integer)
    created_at             = Column(DateTime, nullable=False, default=func.utc_timestamp())
    influencer             = relationship("Influencer", back_populates="influencers")
    influencer_post        = relationship("InfluencerPost", back_populates="influencer_posts")

class InfluencerPost(Base):
    __tablename__ = 'influencer_post'

    id                     = Column(Integer, primary_key=True, index=True)
    campaign_id            = Column(ForeignKey('campaigns.id'))
    influencer_id          = Column(ForeignKey('influencers.id'))
    tag                    = Column(String)
    url                    = Column(Integer)
    campaign               = relationship("Campaign", back_populates="campaigns")
    influencer             = relationship("Influencer", back_populates="influencers")
    influencers            = relationship("Insight", back_populates="influencers")


class Performance(Base):
    __tablename__ = "performances"

    id         = Column(Integer, primary_key=True, index=True)
    sale       = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    company_id = Column(Integer, ForeignKey('companies.id'))
    company    = relationship("companies", backref="performances")

class Comapny(Base):
    __tablename__ = "companies"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

class Influencer(Base):
    __tablename__ = "influencers"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String)
    profile_image   = Column(URLType)
    created_at      = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at      = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    company         = Column(Integer, ForeignKey('companies.id'))
    sns             = relationship("SnsInfo", back_populates="influencers")
    campaigns       = relationship("InfluencerPost", back_populates="influencers")
    company         = relationship("Company", backref="influencers")
    influencer_post = relationship("Insight", back_populates="influencers")

class Campaign(Base):
    __tablename__ = "campaigns"

    id                 = Column(Integer, primary_key=True, index=True)
    name               = Column(String)
    tag                = Column(String)
    description        = Column(String)
    end_at             = Column(DateTime)
    created_at         = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at         = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    influencer_posts   = relationship("InfluencerPost", back_populates="campaigns")

class Sns(Base):
    __tablename__ = "sns"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)
    created_at  = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at  = Column(DateTime, nullable=True, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    influencers = relationship("SnsInfo", back_populates="sns")








