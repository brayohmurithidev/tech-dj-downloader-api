from fastapi import APIRouter, Request, Header, HTTPException, status, Depends, Query
import requests

from utils.deps import get_spotify_token
from utils.time_format import format_duration

router = APIRouter(prefix='/spotify', dependencies=[Depends(get_spotify_token)], tags=['Spotify'])

SPOTIFY_API_BASE = "https://api.spotify.com/v1"

@router.get('/playlists')
def get_playlists(
        token: str = Depends(get_spotify_token),
        limit: int = Query(20, ge=1, le=50),
        offset: int = Query(0, ge=0)
):

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(f"{SPOTIFY_API_BASE}/me/playlists", headers=headers, params={"limit": limit, "offset": offset})

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = response.text  # Fallback to raw text
        raise HTTPException(status_code=response.status_code, detail=detail)

    playlist_data = response.json()

    #Normalize the result
    playlists = [
        {
            "id": item["id"],
            "name": item["name"],
            "image": item["images"][0]["url"] if item["images"] else None,
            "tracks": item["tracks"]["total"]
        }
        for item in playlist_data.get("items", [])
    ]

    return {"playlists": playlists}


# GET PLAYLIST TRACKS
@router.get('/playlists/{playlist_id}/tracks')
def get_playlist_tracks(
        playlist_id: str,
        token: str = Depends(get_spotify_token),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        sort_by: str = Query(None, regex="^(name|duration|artist)$"),
        sort_order: str = Query("asc", regex="^(asc|desc)$")
):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks"

    response = requests.get(url, headers=headers, params={
        "limit": limit,
        "offset": offset
    })

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()


    # Sorting
    items = data.get("items", [])
    if sort_by:
        def get_sort_key(sort_item):
            sort_track = sort_item.get("track", {})
            if sort_by == "name":
                return sort_track.get("name", "").lower()
            elif sort_by == "duration":
                return sort_track.get("duration_ms", 0)
            elif sort_by == "artist":
                return sort_track.get("artists", [{}])[0].get("name", "").lower()
            return None

        items.sort(key=get_sort_key, reverse=(sort_order == "desc"))
        data["items"] = items

    # Extract useful information only
    tracks = []
    for item in data.get("items", []):
        track = item.get("track")
        if not track:
            continue
        tracks.append({
            "id": track.get("id"),
            "name": track.get("name"),
            "artists": [artist.get("name") for artist in track.get("artists", [])],
            "duration_ms": track.get("duration_ms"),
            "duration_formatted": format_duration(track.get("duration_ms", 0)),
            "preview_url": track.get("preview_url"),
            "external_url": track.get("external_urls", {}).get("spotify"),
            "album": {
                "name": track.get("album", {}).get("name"),
                "images": track.get("album", {}).get("images", [])
            }
        })

    return {"tracks": tracks}