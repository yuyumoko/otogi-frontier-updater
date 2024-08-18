import UnityPy

from typing import List

from UnityPy.tools.extractor import extract_assets

from pathlib import Path

from Crypto.Cipher import AES

from utils.session import HTTPSessionApi, HTTPMethod

from FileDataPath import (
    CharacterIconPath,
    StandimagePath,
    CharaStandPath,
    HomeStandPath,
    MScenesPath,
    MAdultsPath,
    ZH_MScenesPath,
    ZH_MAdultsPath,
)

API_HOST = "https://web-assets.otogi-frontier.com/prodassets/GeneralWebGL/Assets/"

AES_KEY = b"kms1kms2kms3kms4"
AES_IV = b"nekonekonyannyan"


def decrypt(data: bytes, key, iv) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(data)
    unpad = lambda s: s[: -ord(s[len(s) - 1 :])]
    decrypted = unpad(decrypted)
    return decrypted


class GameResource(HTTPSessionApi):
    def __init__(self, proxy: str = ""):
        super().__init__(API_HOST, proxy)

    async def getAllCharacterIconDataSize(self):
        url = f"chara_icon"
        res = await self.request_raw_data(url, method=HTTPMethod.OPTIONS)
        return int(res.headers.get("Content-Length", 0))

    async def getAllCharacterIconData(self, chunk_handler=None, chunk_size=1024):
        # https://web-assets.otogi-frontier.com/prodassets//GeneralWebGL/Assets/item_icon
        # https://web-assets.otogi-frontier.com/prodassets//GeneralWebGL/Assets/material_icon
        # https://web-assets.otogi-frontier.com/prodassets//GeneralWebGL/Assets/chara_icon
        url = f"chara_icon"
        res = await self.request_raw_data(
            url, chunk_handler=chunk_handler, chunk_size=chunk_size
        )
        return res.data

    async def GetAssetBundlePatch(self, AssetsVersion):
        # https://web-assets.otogi-frontier.com/prodassets/GeneralWebGL/AssetBundlePatch/FullList/464_ad.csv
        url = f"https://web-assets.otogi-frontier.com/prodassets/GeneralWebGL/AssetBundlePatch/FullList/{AssetsVersion}_ad.csv"
        return (await self.request_raw_data(url)).data

    async def getCharacterSpine(self, id):
        url = f"chara/spine/{id}"
        return (await self.request_raw_data(url)).data

    async def getCharacterHomestand(self, id):
        url = f"chara/homestand/{id}"
        return (await self.request_raw_data(url)).data

    async def getCharacterStandImageLarge(self, id):
        url = f"chara/standimagelarge/{id}"
        return (await self.request_raw_data(url)).data

    async def getCharacterAlbumVoice(self, id):
        url = f"sound/voice/album/voice_album_{id}"
        return (await self.request_raw_data(url)).data

    async def getHomeVoice(self, id):
        url = f"sound/voice/home/voice_home_{id}"
        return (await self.request_raw_data(url)).data

    async def getAdventureVoice(self, id):
        url = f"sound/voice/adventure/voice_adventure_{id}"
        return (await self.request_raw_data(url)).data

    async def getAdventureBG(self, id):
        url = f"bg/adventure/{id}"
        return (await self.request_raw_data(url)).data

    async def getAdventureBGM(self, id):
        url = f"sound/bgm/{id}"
        return (await self.request_raw_data(url)).data

    async def getCharacterStand(self, id):
        url = f"chara/stand/{id}"
        return (await self.request_raw_data(url)).data

    async def getCharacterStillSpine(self, id):
        # 加密
        url = f"chara/still/{id}"
        data = (await self.request_raw_data(url)).data
        return decrypt(data, AES_KEY, AES_IV)

    async def getCharacterStillVoice(self, id):
        url = f"sound/voice/still/voice_still_{id}"
        return (await self.request_raw_data(url)).data

    async def getAssetsFromPath(self, url_path: str) -> bytes:
        has_encrypt = url_path.startswith("chara/still/")
        data = (await self.request_raw_data(url_path)).data
        return decrypt(data, AES_KEY, AES_IV) if has_encrypt else data

    async def ExtractAsset(self, url_path: str, out_path: Path) -> List[int]:
        raw_data = await self.getAssetsFromPath(url_path)
        file_path = out_path / url_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as f:
            f.write(raw_data)
            
        # 全部解压效率低还大, 不如自己解包
        # if url_path.startswith("chara/homestand/") or url_path.startswith("chara/stand/"):
        #     file_path = out_path / "assets/assetbundleresources" / url_path
        #     file_path.mkdir(parents=True, exist_ok=True)
            
        #     env = UnityPy.load(raw_data)

        #     for obj in env.objects:
        #         if obj.byte_size < 600:
        #             continue

        #         if obj.type.name == "Sprite":
        #             data = obj.read()
        #             if data.name == "_stand1":
        #                 continue

        #             data.image.save(file_path / f"{data.name}.png")

        #         if obj.type.name == "Texture2D":
        #             data = obj.read()
        #             data_name = data.name
        #             # if data_name.startswith("sactx-"):
        #             #     continue
        #             if data_name.isdigit():
        #                 data_name = "body"

        #             data.image.save(file_path / f"{data_name}.png")
        #     return [1]

        # return extract_assets(raw_data, out_path, ignore_first_container_dirs=None)
