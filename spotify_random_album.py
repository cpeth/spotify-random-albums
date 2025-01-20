import httpx
import random
import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

class SpotifyRandomAlbums:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_followed_artists(self):
        url = f"{self.base_url}/me/following?type=artist"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        artists = response.json()["artists"]["items"]
        return [artist["id"] for artist in artists]

    def get_albums_by_artist(self, artist_id):
        url = f"{self.base_url}/artists/{artist_id}/albums"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        albums = response.json()["items"]
        return albums

    def get_random_albums(self, n):
        followed_artists = self.get_followed_artists()
        all_albums = []
        for artist_id in followed_artists:
            albums = self.get_albums_by_artist(artist_id)
            all_albums.extend(albums)
        return random.sample(all_albums, n)



# Example usage:
# access_token = "your_spotify_access_token"
# spotify_random_albums = SpotifyRandomAlbums(access_token)
# random_albums = spotify_random_albums.get_random_albums(5)
# for album in random_albums:
#     print(album["name"])

def get_access_token():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = httpx.post(auth_url, data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    })
    auth_response.raise_for_status()
    return auth_response.json()["access_token"]

# Example usage:
# access_token = get_access_token()
# spotify_random_albums = SpotifyRandomAlbums(access_token)
# random_albums = spotify_random_albums.get_random_albums(5)
# for album in random_albums:
#     print(album["name"])

import urllib.parse

class SpotifyAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self.server.auth_code = query_components.get('code')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Authorization successful. You can close this window.')

def get_authorization_code(client_id, redirect_uri):
    auth_url = (
        "https://accounts.spotify.com/authorize"
        "?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        "&scope=user-follow-read"
    )
    webbrowser.open(auth_url)
    
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SpotifyAuthHandler)
    httpd.handle_request()
    
    return httpd.auth_code[0]

def get_access_token_with_auth_code(client_id, client_secret, redirect_uri, auth_code):
    token_url = "https://accounts.spotify.com/api/token"
    response = httpx.post(token_url, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    })
    response.raise_for_status()
    return response.json()["access_token"]

# Example usage:
# client_id = os.getenv("SPOTIFY_CLIENT_ID")
# client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
# redirect_uri = "http://localhost:8080"
# auth_code = get_authorization_code(client_id, redirect_uri)
# access_token = get_access_token_with_auth_code(client_id, client_secret, redirect_uri, auth_code)
# spotify_random_albums = SpotifyRandomAlbums(access_token)
# random_albums = spotify_random_albums.get_random_albums(5)
# for album in random_albums:
#     print(album["name"])