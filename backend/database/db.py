import os
import sys

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# Get the directory path of the current file
current_dir_path = os.path.dirname(current_file_path)
# Get the parent directory path
parent_dir_path = os.path.dirname(current_dir_path)
# Add the parent directory path to the sys.path
sys.path.insert(0, parent_dir_path)

from backend.utils.logger import logger
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


postg_host = os.getenv("postg_host")
postg_port = os.getenv("postg_port")
postg_user = os.getenv("postg_user")
postg_password = os.getenv("postg_password")
postg_database = os.getenv("postg_database")

# Define Database URL (Modify with actual credentials)
POSTGRES_DATABASE_URL = f"postgresql+psycopg2://{postg_user}:{postg_password}@{postg_host}:{postg_port}/{postg_database}"


mysql_host = os.getenv("mysql_host", "localhost")
mysql_port = int(os.getenv("mysql_port", "3306"))
mysql_user = os.getenv("mysql_user", "root")
mysql_password = os.getenv("mysql_password", "")
mysql_database = os.getenv("mysql_database", "db")

# database URL
MYSQL_DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"


# Create Engine & Session
engine = create_engine(MYSQL_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Base
Base = declarative_base()


# UUID Generator for MySQL
def generate_uuid():
    return str(uuid.uuid4())


# User Table
class User(Base):
    __tablename__ = "users"
    id = Column(
        CHAR(36), primary_key=True, default=generate_uuid
    )  # MySQL doesn't support native UUID
    email = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    role = Column(
        String(50), CheckConstraint("role IN ('user', 'admin')"), default="user"
    )
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# Chat History Table
class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)


# Embeddings Metadata Table (Milvus stores vectors)
class EmbeddingsMetadata(Base):
    __tablename__ = "embeddings_metadata"
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    text = Column(Text, nullable=False)
    vector_id = Column(
        String(255), unique=True, nullable=False
    )  # Reference to Milvus vector
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# Feedback Table
class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(
        CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    feedback = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# Initialize Database
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
