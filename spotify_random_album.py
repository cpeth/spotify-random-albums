import httpx
import random
import os

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