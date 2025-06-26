from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class DownloadLog(Base):
    __tablename__ = "download_logs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)
    title = Column(String)
    artist = Column(String)
    filename = Column(String)
    status = Column(String, default="queued")  # queued / downloading / done / error
    source = Column(String, default="YouTube")
    downloaded_at = Column(DateTime, default=datetime.utcnow)