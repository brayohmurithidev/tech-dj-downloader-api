from fastapi import APIRouter
from starlette.responses import RedirectResponse
import urllib.parse
import requests
import os

router = APIRouter(prefix='/auth')

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
SCOPES = os.environ.get("SPOTIFY_SCOPES")
SPOTIFY_CLIENT_SECRET=os.environ.get("SPOTIFY_CLIENT_SECRET")
FRONTEND_REDIRECT=os.environ.get("FRONTEND_REDIRECT")


# Login
@router.get('/spotify/login')
def login():
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SCOPES,
    }
    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


# Callback
@router.get('/spotify/callback')
def spotify_callback(code: str):
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)
    data = response.json()

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")

    # Optionally generate your own JWT and send to frontend
    redirect_url = f"{FRONTEND_REDIRECT}?token={access_token}"
    return RedirectResponse(f"http://localhost:5173/auth/callback?token={access_token}")