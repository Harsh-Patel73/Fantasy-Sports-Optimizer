from app.models.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Books(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True, index=True)
    book_name = Column(String(255))
    book_type = Column(String(255))

    statlines = relationship("Statlines", back_populates ="book")