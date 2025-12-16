from app.models.base import Base
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

class Statlines(Base):
    __tablename__ = 'statlines'

    line_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey ("books.book_id"))
    player_name = Column(String(255))
    matchup_id = Column(Integer, ForeignKey ("matchups.matchup_id"))
    prop_id = Column(Integer, ForeignKey ("props.prop_id"))
    price = Column(DECIMAL)
    points = Column(DECIMAL(precision=10,scale=1))
    designation = Column(String(255))
    line_type = Column(String(255))

    prop = relationship("Props", back_populates="statlines")
    book = relationship("Books", back_populates ="statlines")
    matchup = relationship("Matchups", back_populates="statlines")

