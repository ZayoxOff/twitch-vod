import json
import requests
from urllib.parse import urlencode

class TwitchVodFetcher:
    def __init__(self, vod_id: str):
        self.vod_id = vod_id
        self.client_id = "kimne78kx3ncx6brgo4mv6wki5h1ko"
        self.device_id = "ujCGhgLom0CwwEzxQn4f3A7RNK9I6b9c"
        self.sig = None
        self.token = None

        self.fetch_access_token()

    def fetch_access_token(self):
        response = requests.post(
            url = "https://gql.twitch.tv/gql",
            data = json.dumps({
                "operationName": "PlaybackAccessToken_Template",
                "query": """query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!, $platform: String!) {
                streamPlaybackAccessToken(channelName: $login, params: {platform: $platform, playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isLive) {
                    value
                    signature
                    authorization { isForbidden forbiddenReasonCode }
                    __typename
                }
                videoPlaybackAccessToken(id: $vodID, params: {platform: $platform, playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isVod) {
                    value
                    signature
                    __typename
                }
                }""",
                "variables": {
                    "isLive": False,
                    "login": "",
                    "isVod": True,
                    "vodID": self.vod_id,
                    "playerType": "site",
                    "platform": "web"
                }
            }),
            headers = {
                "client-id": self.client_id,
                "device-id": self.device_id,
                "content-type": "text/plain; charset=UTF-8",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "origin": "https://www.twitch.tv",
                "referer": "https://www.twitch.tv/",
            }
        ).json()["data"]["videoPlaybackAccessToken"]
        self.sig = response["signature"]
        self.token = response["value"]

    def fetch_m3u8(self):
        if not self.sig or not self.token:
            raise Exception("Token and signature not fetched. Run fetch_access_token() first.")
        
        return f"https://usher.ttvnw.net/vod/{self.vod_id}.m3u8?{urlencode({
            "allow_source": "true",
            "playlist_include_framerate": "true",
            "reassignments_supported": "true",
            "platform": "web",
            "player_backend": "mediaplayer",
            "player_version": "1.40.0-rc.1",
            "play_session_id": "a6242922978066143662c74615aa6c9a",
            "cdm": "wv",
            "browser_family": "chrome",
            "browser_version": "135.0",
            "os_name": "Windows",
            "os_version": "NT 10.0",
            "supported_codecs": "av1,h265,h264",
            "transcode_mode": "cbr_v1",
            "sig": self.sig,
            "token": self.token
        })}"

if __name__ == "__main__":
    vod_id = "2436366516"
    fetcher = TwitchVodFetcher(vod_id)
    
    m3u8_content = fetcher.fetch_m3u8()
    print(m3u8_content)
