from typing import Optional

from pydantic import BaseModel

class SearchRequest(BaseModel):
    title: str
    artist: str

class SearchResult(BaseModel):
    title: str
    duration: int #in seconds
    url: Optional[str] = None
    video_id: str
    thumbnail: Optional[str] = None


class DownloadRequest(BaseModel):
    video_id: str
    title: str


