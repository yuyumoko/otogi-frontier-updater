import gzip
import ujson as json

from utils import AsyncCache

from .GitHubFileFetcher import GitHubFileFetcher

from config import resource_repo, resource_branch, resource_token


def str_path_to_dict(raw_data):
    data = {}
    for key, value in raw_data.items():
        if "\\" in key:
            path, sub_key = key.split("\\", 1)
            if path not in data:
                data[path] = {}

            data[path] = str_path_to_dict({**data[path], **{sub_key: value}})

        else:
            data[key] = value
    return data


class GitHubServer(GitHubFileFetcher):
    _instance = None
    hash_data: dict = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GitHubServer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            super().__init__(resource_repo, resource_branch, resource_token, proxy=True)
            self._initialized = True

    async def init(self):
        if self.hash_data is not None:
            return

        path = "hash.json.gz"
        raw_data = await self.fetch_binary(path)
        raw_data = json.loads(gzip.decompress(raw_data))
        self.hash_data = str_path_to_dict(raw_data)

    @AsyncCache()
    async def getSpecials(self):
        raw_data = await self.fetch_json(f"VieableEpisodeList/special")
        return raw_data["Episodes"]

    @AsyncCache()
    async def getUserCharacterIDS(self):
        await self.init()

        ids = [
            int(id)
            for id in self.hash_data["VieableEpisodeList"].keys()
            if id.isdigit()
        ]

        return ids

    @AsyncCache()
    async def getCharacterEpisodes(self, character_id):
        episodes = await self.fetch_json(f"VieableEpisodeList/{character_id}")
        return {
            "RootMonsterId": character_id,
            "RootSpiritId": 0,
            "Favorite": False,
            "Episodes": episodes,
        }

    @AsyncCache()
    async def getMScenes(self, MSceneId):
        await self.init()
        if str(MSceneId) not in self.hash_data["typeadv"]["MScenes"].keys():
            return None

        return await self.fetch_json(f"typeadv/MScenes/{MSceneId}")

    @AsyncCache()
    async def getZHMScenes(self, MSceneId):
        await self.init()
        if str(MSceneId) not in self.hash_data["typeadv"]["MScenes_TW"].keys():
            return None

        return await self.fetch_json(f"typeadv/MScenes_TW/{MSceneId}")

    @AsyncCache()
    async def getMAdults(self, MAdultId):
        await self.init()
        if str(MAdultId) not in self.hash_data["json"].keys():
            return None

        return await self.fetch_json(f"json/{MAdultId}")

    @AsyncCache()
    async def getZHMAdults(self, MAdultId):
        await self.init()
        if str(MAdultId) not in self.hash_data["jsoncn"].keys():
            return None

        return await self.fetch_json(f"jsoncn/{MAdultId}")

    @AsyncCache()
    async def getHomestandFix(self):
        return await self.fetch_json(f"fix/homestand_fix.json")

    @AsyncCache()
    async def getHomestandFixName(self):
        return await self.fetch_json(f"fix/homestand_fix_name.json")
