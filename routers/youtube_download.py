from fastapi import APIRouter, HTTPException, BackgroundTasks


from schemas import SearchResult, SearchRequest, DownloadRequest
from yt_dlp import YoutubeDL
import  os
from uuid import uuid4
from hooks import make_progress_hook, download_progress
import re

def sanitize_filename(name: str) -> str:
    # Remove characters not allowed in filenames
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()



router = APIRouter()

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


@router.post('/search', response_model=list[SearchResult])
def search_track(req: SearchRequest):
    query = f"{req.title} {req.artist}"

    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch1", #upto 10 results
        "skip_download": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            search_result = ydl.extract_info(query, download=False)
            entries = search_result.get("entries", [])

            if not entries:
                raise HTTPException(status_code=404, detail="No tracks found")
            results = []
            for e in entries:
                # Skip invalid results
                if not e or not e.get("id") or not e.get("title"):
                    continue
                results.append(  {
                        "title": e.get("title"),
                        "duration": e.get("duration"),
                        "url": f"https://www.youtube.com/watch?v={e['id']}",
                        "video_id": e.get("id"),
                    "thumbnail": e.get("thumbnail") or f"https://i.ytimg.com/vi/{e['id']}/hqdefault.jpg",
                    })
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")





def download_audio(url: str, output_path:str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@router.post("/download")
def download_track(req: DownloadRequest, background_tasks: BackgroundTasks):
    video_id = req.video_id
    title = sanitize_filename(req.title)
    track_id  = str(uuid4())
    output_path = os.path.join(DOWNLOADS_DIR, f"{title}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "progress_hooks": [make_progress_hook(video_id)],
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }

    def run_download():
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        except Exception as e:
            download_progress[video_id]["error"] = str(e)

    background_tasks.add_task(run_download)

    return {
        "status":"started",
        "track_id": track_id,
        "video_id": video_id,
    }


# FETCHING DOWNLOAD PROGRESS
@router.get('/progress/{video_id}')
def get_download_progress(video_id: str):
    progress = download_progress.get(video_id)
    if not progress:
        raise HTTPException(status_code=404, detail=f"Video {video_id} progess not found")
    return progress