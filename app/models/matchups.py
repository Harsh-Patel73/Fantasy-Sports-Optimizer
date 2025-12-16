from app.models.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Matchups(Base):
    __tablename__ = 'matchups'

    matchup_id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String(255))
    away_team = Column(String(255))

    statlines = relationship("Statlines", back_populates="matchup")

