from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base  # Optional: in case you want to use Base.metadata.create_all()

DATABASE_URL = "mysql+pymysql://root:huncho11@127.0.0.1:3306/db1"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)