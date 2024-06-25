import re

from .GameData import GameData
from .GameResource import GameResource


class OtogiApi:
    char: GameData
    resource: GameResource
    access_token: str

    def valid_access_token(self, access_token):
        uuid_pattern = re.compile(
            r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
        )
        return bool(uuid_pattern.match(access_token))

    def _request_headers(self):
        return {
            "authority": "otogi-rest.otogi-frontier.com",
            "accept": "application/Json",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-encoding": "gzip, deflate, br",
            "referer": "https://otogi-rest.otogi-frontier.com/Content/Atom?adult=True",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "token": self.access_token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36",
            "x-client-name": "PC",
            # "x-client-version": "635",
        }

    def __init__(self, access_token="", proxy=""):
        if access_token != "":
            if not self.valid_access_token(access_token):
                raise ValueError(
                    "access token 错误, 类似于: 80f2b125-bf29-4205-9d4e-ab6d06614f55"
                )

        self.access_token = access_token
        self.char = GameData(proxy, use_github_data=access_token == "")
        self.resource = GameResource(proxy)

        self.char.request_headers = self._request_headers()
        self.resource.request_headers = self._request_headers()
