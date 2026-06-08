import os
import bcrypt
import secrets
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "uniocr.db"

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_initial_setup = Column(Boolean, default=True)
    totp_secret = Column(String, nullable=True)
    is_2fa_enabled = Column(Boolean, default=False)
    totp_secret_pending = Column(String, nullable=True)

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, index=True)
    name = Column(String)
    prefix = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Config(Base):
    __tablename__ = "config"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize default admin and config if not exists
def init_db():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            salt = bcrypt.gensalt()
            default_hash = bcrypt.hashpw(b"admin", salt).decode("utf-8")
            admin = User(username="admin", password_hash=default_hash, is_initial_setup=True)
            db.add(admin)
            
        jwt_secret = db.query(Config).filter(Config.key == "jwt_secret").first()
        if not jwt_secret:
            db.add(Config(key="jwt_secret", value=secrets.token_hex(32)))
            
        is_ocr_public = db.query(Config).filter(Config.key == "is_ocr_public").first()
        if not is_ocr_public:
            db.add(Config(key="is_ocr_public", value="true"))
            
        db.commit()
    finally:
        db.close()

init_db()
