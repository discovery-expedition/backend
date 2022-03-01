from sqlalchemy          import Column, Integer, String
from postgresql.database import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String)
