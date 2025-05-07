from app.models.base import Base
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship

class Props(Base):
    __tablename__ = 'props'

    prop_id = Column(Integer, primary_key=True, index=True)
    category = Column(String(255))
    units = Column(String(255))
    description = Column(String(255))
    scrape_timestamp = Column(TIMESTAMP)

    statlines = relationship("Statlines", back_populates="prop")