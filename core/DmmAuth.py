import re
import asyncio
import ujson as json

from urllib.parse import quote_plus, urlparse, parse_qs
from aiohttp import ClientSession

LOGIN_URL = "https://accounts.dmm.co.jp/service/login/password/"
PLAY_URL = "https://pc-play.games.dmm.co.jp/play/"


class DmmAuth:

    session: ClientSession

    def __init__(self, login_id, password, game_name, proxy=None):
        self.session = ClientSession()
        self.login_id = login_id
        self.password = password
        self.game_name = game_name
        self.proxy = proxy

    def get_page_data(self, html):
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
        )
        if match is None:
            raise Exception("Failed to find __NEXT_DATA__")

        return json.loads(match.group(1))

    async def login(self):
        game_url = quote_plus(f"{PLAY_URL}{self.game_name}/")

        async with self.session.get(
            f"{LOGIN_URL}=/path={game_url}", allow_redirects=False, proxy=self.proxy
        ) as response:
            if response.status != 200:
                raise Exception("Failed to get login page")

            data = self.get_page_data(await response.text())

            return {
                "token": data["props"]["pageProps"]["token"],
                "login_id": self.login_id,
                "password": self.password,
                "path": game_url,
            }

    async def authenticate(self):
        login_params = await self.login()
        async with self.session.post(
            f"{LOGIN_URL}authenticate", data=login_params, proxy=self.proxy
        ) as response:
            if response.status != 200:
                raise Exception("Failed to login")

            async with self.session.get(
                f"{PLAY_URL}{self.game_name}/",
                proxy=self.proxy,
            ) as response:
                game_html = await response.text()
                match = re.search(r'(//osapi\.dmm\.com/gadgets/ifr[^"]+)', game_html)
                if match is None:
                    raise Exception("Failed to find game iframe")

                game_query = urlparse(match.group(1).replace("amp;", "")).query
                query_dict = parse_qs(game_query)
                res_data = {}
                for k, v in query_dict.items():
                    res_data[k] = v[0]

                return res_data

    async def makeRequest(self, game_url):
        osapi_info = await self.authenticate()

        data = {
            "url": game_url,
            "httpMethod": "POST",
            "headers": "Content-Type=application%2Fx-www-form-urlencoded",
            "postData": "xmlVer=1706159549",
            "authz": "signed",
            "st": osapi_info["st"],
            "contentType": "JSON",
            "numEntries": "3",
            "getSummaries": "false",
            "signOwner": "true",
            "signViewer": "true",
            "gadget": osapi_info["url"],
            "container": "dmm",
            "bypassSpecCache": "",
            "getFullHeaders": "false",
            "oauthState": "",
            "OAUTH_SIGNATURE_PUBLICKEY": "key_2032",
        }

        async with self.session.post(
            "https://osapi.dmm.com/gadgets/makeRequest", data=data
        ) as response:
            text = await response.text()

            data = json.loads(text[27:])
            data = next(iter(data.values()))

            data["body"] = json.loads(data["body"])
            return data


async def run_test():
    DMM = DmmAuth("", "", "angelicr", proxy="http://127.0.0.1:7890")
    await DMM.authenticate()


if __name__ == "__main__":
    asyncio.run(run_test())
