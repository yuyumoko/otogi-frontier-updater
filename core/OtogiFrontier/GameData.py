import gzip
import ujson as json

from utils.session import HTTPSessionApi
from ..DataServer.GitHubServer import GitHubServer

from utils import AsyncCache

API_HOST = "https://otogi-rest.otogi-frontier.com/api/"


class GameData(HTTPSessionApi):
    use_github_data: bool = False
    GithubDataServer: GitHubServer = None

    characterData: dict = None
    Specials: list = None

    def __init__(self, proxy: str = "", use_github_data: bool = False):
        super().__init__(API_HOST, proxy)
        self.use_github_data = use_github_data
        if use_github_data:
            self.GithubDataServer = GitHubServer()

    async def getMSpiritsData(self):
        url = "MasterData/MSpirits.gz"
        res = await self.request_raw_data(
            url, host="https://web-assets.otogi-frontier.com/prodassets/"
        )
        return json.loads(gzip.decompress(res.data))

    async def getMMonstersData(self):
        url = "MasterData/MMonsters.gz"
        res = await self.request_raw_data(
            url, host="https://web-assets.otogi-frontier.com/prodassets/"
        )
        return json.loads(gzip.decompress(res.data))

    async def initCharacterData(self):
        res_json = await self.getMMonstersData()
        data = {}
        for item in res_json:
            data[item["id"]] = item
        self.characterData = data

        res_json = await self.getMSpiritsData()
        data = {}
        for item in res_json:
            data[item["id"]] = item

        self.characterData.update(data)

        return data

    async def getCharacterRmids(self, ids):
        if self.characterData is None:
            await self.initCharacterData()

        return [
            self.characterData[x]["rmid"]
            for x in ids
            if x in self.characterData and "rmid" in self.characterData[x]
        ]

    async def getCharacterInfo(self, id):
        if self.characterData is None:
            await self.initCharacterData()

        return self.characterData.get(id)

    @AsyncCache()
    async def getCharacterStory(self):
        url = "Episode/CharacterStory?CharacterStoryTypes=Monster&CharacterStoryTypes=Spirit&CharacterStoryTypes=Special&CharacterStoryTypes=Premium"
        return (await self.request_json(url)).data

    async def getUserCharacterIDS(self):
        if self.use_github_data:
            self.Specials = await self.GithubDataServer.getSpecials()
            return await self.GithubDataServer.getUserCharacterIDS()

        data = await self.getCharacterStory()
        Monsters = [x["RootMonsterId"] for x in data["Monsters"]]
        Spirits = [x["RootSpiritId"] for x in data["Spirits"]]
        self.Specials = data["Specials"]
        return Monsters + Spirits

    async def getCharacterEpisodes(self, character_id):
        if self.use_github_data:
            return await self.GithubDataServer.getCharacterEpisodes(character_id)

        if character_id > 80000:
            url = f"episode/spirits/{character_id}"
        else:
            url = f"episode/monsters/{character_id}"
        return (await self.request_json(url)).data

    async def getMScenes(self, MSceneId):
        if self.use_github_data:
            return await self.GithubDataServer.getMScenes(MSceneId)

        url = f"MScenes/{MSceneId}"
        return (await self.request_json(url)).data

    async def getZHMScenes(self, MSceneId):
        return await self.GithubDataServer.getZHMScenes(MSceneId)

    async def getMAdults(self, MAdultId):
        if self.use_github_data:
            return await self.GithubDataServer.getMAdults(MAdultId)

        url = f"MAdults/MonsterMAdults/{MAdultId}"
        return (await self.request_json(url)).data

    async def getZHMAdults(self, MAdultId):
        return await self.GithubDataServer.getZHMAdults(MAdultId)

    async def geNextAdultScene(self, MSceneId):
        url = f"MAdults/NextAdultScene/{MSceneId}"
        return (await self.request_json(url)).data
