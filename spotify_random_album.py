import httpx
import random
import os
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

AUTH_CODE = 'QB6uN8oGzU6Mjv4haDGcHaGIscCoSJFDri7j-2PERM_ThsJ2iPv1IY1NXxe56Mlart36xQ1TU8RJga-OV6siqj5I7tnGF17G9TBP_qbUHvKmYFLj3kFwNVR_i4ma5s6Oz7WCBlZmrCqmRB61t6JUe5xGL9bUDo_GMuRdGwCJ26Cj1vYI2KlQrbIGs1uELtjnUTuSnbtLPH7DqXe_gLAa-RlJYc73LRlsDBNJX1cU2v0TxDsNM8rCy34q-pv'

class SpotifyRandomAlbums:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_followed_artists(self):
        url = f"{self.base_url}/me/following?type=artist"
        artists = []
        while url:
            response = httpx.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            artists.extend(data["artists"]["items"])
            url = data["artists"]["next"]
        print(f'retrieved {len(artists)} artists')
        return [artist["id"] for artist in artists]

    def get_albums_by_artist(self, artist_id):
        url = f"{self.base_url}/artists/{artist_id}/albums"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        albums = response.json()["items"]
        return albums

    def get_random_albums(self, n):
        followed_artists = self.get_followed_artists()
        random_artists = random.sample(followed_artists, n)
        result_albums = []
        for artist_id in random_artists:
            albums = self.get_albums_by_artist(artist_id)
            if albums:
                album = random.choice(albums)
                result_albums.append(album)
        return result_albums

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
        "&scope=user-follow-read user-library-read app-remote-control streaming"
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

if __name__ == "__main__":
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = "http://localhost:8080"
    auth_code = get_authorization_code(client_id, redirect_uri)
    print(f'auth_code: {auth_code}')
    access_token = get_access_token_with_auth_code(client_id, client_secret, redirect_uri, auth_code)
    spotify_random_albums = SpotifyRandomAlbums(access_token)
    random_albums = spotify_random_albums.get_random_albums(5)
    for album in random_albums:
        print(f'{album["name"]} by {album["artists"][0]["name"]} ({album["release_date"]})')