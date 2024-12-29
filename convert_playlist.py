import os
import pprint
import requests
import argparse
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

class ConvertPlaylist():

    def __init__(self):
        self.youtube = self.get_youtube_client()
        self.playlist = {'tracks': []}

    # sarch for song in spotify
    def get_spotify_song(self, track):
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            track['name'],
            track['artist']
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri

    # get spotify playlist
    def get_spotify_playlist(self, spotify_uri):
        playlist_id = spotify_uri
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        response_json = sp.playlist(playlist_id)
        self.playlist['title'] = response_json['name']
        self.playlist['description'] = response_json['description']
        items = response_json['tracks']['items']
        for item in items:
            track_name = item['track']['name']
            main_artist = item['track']['artists'][0]['name']
            track = {'name': track_name,
                     'artist': main_artist}
            self.playlist['tracks'].append(track)

    # create spotify playlist
    def create_spotify_playlist(self, title, description=""):
        pass

    # add song to a playlist
    def add_song_to_spotify_playlist(self):
        pass

    # Log into Youtube
    def get_youtube_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        scopes = ["https://www.googleapis.com/auth/youtubepartner"]

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_local_server(port=0)
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
        )
        response = request.execute()
        return youtube

    # search for song in youtube
    def get_youtube_video(self, track):
        query = "{} - {}".format(track['artist'], track['name'])
        # get response
        request = self.youtube.search().list(
            part="snippet",
            q=query
        )
        response = request.execute()
        # get video id (and title)
        for item in response['items']:
            if item['id']['kind'] == 'youtube#video':

                video_title = item['snippet']['title']
                video_id = item['id']['videoId']
                break

        return video_id

    # get youtube playlist
    def get_youtube_playlist(self):
        # does sth. with self.playlist
        pass

    # create youtube playlist
    def create_youtube_playlist(self, title, description=""):
        request = self.youtube.playlists().insert(
            part="snippet",
            body={
                "snippet": {
                    "title": title,
                    "description": description
                }
            }
        )
        response = request.execute()

        playlist_id = response['id']
        playlist_title = response['snippet']['localized']['title']
        print('-' * 30)
        print(playlist_title)
        print("https://www.youtube.com/playlist?list={}".format(playlist_id))
        print('-' * 30)

        return playlist_id

    # add video to a playlist
    def add_video_to_youtube_playlist(self, video_id, playlist_id):
        request = self.youtube.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        )
        request.execute()

    def convert(self, spotify_uri):
        # get spotify playlist
        self.get_spotify_playlist(spotify_uri)
        # create youtube playlist
        title = '\'\'spotify_' + self.playlist['title']
        playlist_id = self.create_youtube_playlist(title, self.playlist['description'])
        for track in self.playlist['tracks']:
            # search video on youtube [artist - song name]
            video_id = self.get_youtube_video(track)
            # add video to youtube playlist
            self.add_video_to_youtube_playlist(video_id, playlist_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a Spotify playlist to a YouTube playlist')
    parser.add_argument('spotify_uri', type=str, help='Spotify Playlist > ... > Share > Copy Spotify URI')
    args = parser.parse_args()

    cp = ConvertPlaylist()
    cp.convert(args.spotify_uri)
