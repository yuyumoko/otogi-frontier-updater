import UnityPy

from pathlib import Path

from tqdm import tqdm
from utils import log, save_json, UnityEnv

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

from config import http_proxy, CharaIconPath

from core.OtogiFrontier import OtogiApi
from core.FixHomeStandImage import FixHomeStandImage


class FetchGameRes:
    GameApi: OtogiApi = None

    def __init__(self, GameApi: OtogiApi = None):
        self.GameApi = GameApi or OtogiApi(proxy=http_proxy)

    async def save_chara_icon(self, char_id, save_path: Path, force_download=False):
        icon_path = save_path / CharacterIconPath
        icon_path.mkdir(parents=True, exist_ok=True)
        icon_path = icon_path / f"{char_id}.png"
        if not icon_path.exists() or force_download:
            CharaIcon = UnityPy.load(CharaIconPath.read_bytes())
            pbar = tqdm(CharaIcon.objects, desc="保存角色图标")
            for obj in pbar:
                if obj.type.name == "Sprite":
                    data = obj.read()
                    if data.name == str(char_id):
                        data.image.save(icon_path)
                        pbar.close()
                        return True
        return False

    async def save_stand_image(self, char_id, save_path: Path, force_download=False):
        charInfo = await self.GameApi.char.getCharacterInfo(char_id)
        if charInfo is None:
            return False

        standimage_path = save_path / StandimagePath
        pbar = tqdm(range(0, charInfo["r"]), desc="保存立绘")

        for num in pbar:
            img_id = char_id + num
            standimage_img_path = standimage_path / f"{img_id}.png"
            if not standimage_img_path.exists() or force_download:
                standimage_img_path.parent.mkdir(parents=True, exist_ok=True)
                standimage_data = (
                    await self.GameApi.resource.getCharacterStandImageLarge(img_id)
                )
                standimage_env = UnityPy.load(standimage_data)
                for obj in standimage_env.objects:
                    if obj.type.name == "Texture2D":
                        data = obj.read()
                        data.image.save(standimage_img_path)
        pbar.close()
        return True

    async def save_chara_stand(self, char_id, save_path: Path, force_download=False):
        CharaStand_path = save_path / CharaStandPath / str(char_id)
        if not CharaStand_path.exists() or force_download:
            CharaStand_path.mkdir(parents=True, exist_ok=True)
            CharaStand_data = await self.GameApi.resource.getCharacterStand(char_id)
            CharaStand_env = UnityPy.load(CharaStand_data)
            # pbar = tqdm(CharaStand_env.objects, desc="保存剧情立绘")

            for obj in CharaStand_env.objects:
                if obj.byte_size < 600:
                    continue

                if obj.type.name == "Sprite":
                    data = obj.read()
                    data.image.save(CharaStand_path / f"{data.name}.png")

                if obj.type.name == "Texture2D":
                    data = obj.read()
                    data_name = data.name
                    if data_name.startswith("sactx-"):
                        continue
                    if data_name.isdigit():
                        data_name = "body"

                    data.image.save(CharaStand_path / f"{data_name}.png")
            # pbar.close()
            return True
        return False

    async def save_home_stand(self, char_id, save_path: Path, force_download=False):
        homestand_path = save_path / HomeStandPath / str(char_id)
        if not homestand_path.exists() or force_download:
            homestand_path.mkdir(parents=True, exist_ok=True)
            homestand_data = await self.GameApi.resource.getCharacterHomestand(char_id)
            homestand_env = UnityPy.load(homestand_data)

            # pbar = tqdm(homestand_env.objects, desc="保存剧情立绘2")
            for obj in homestand_env.objects:
                if obj.byte_size < 600:
                    continue

                if obj.type.name == "Sprite":
                    data = obj.read()
                    if data.name == "_stand1":
                        continue

                    data.image.save(homestand_path / f"{data.name}.png")

                if obj.type.name == "Texture2D":
                    data = obj.read()
                    data_name = data.name
                    if data_name.startswith("sactx-"):
                        continue
                    if data_name.isdigit():
                        data_name = "body"

                    data.image.save(homestand_path / f"{data_name}.png")
            # pbar.close()
            await FixHomeStandImage(save_path / HomeStandPath, char_id).fix()
            return True
        return False

    async def save_MScenes(self, MSceneId, save_path: Path, force_download=False):
        MScenes = await self.GameApi.char.getMScenes(MSceneId)
        if MScenes is None:
            return False

        MScenes_path = save_path / MScenesPath
        MScenes_file = MScenes_path / str(MSceneId)
        if not MScenes_file.exists() or force_download:
            save_json(MScenes, MScenes_file)

        if self.GameApi.char.use_github_data:
            MScenes = await self.GameApi.char.getZHMScenes(MSceneId)
            if MScenes is None:
                log.warning(f"获取 [{MSceneId}] 汉化数据失败, 等更新")
                return False

            MScenes_path = save_path / ZH_MScenesPath
            MScenes_file = MScenes_path / str(MSceneId)
            if not MScenes_file.exists() or force_download:
                save_json(MScenes, MScenes_file)

    async def save_MAdults(self, MAdultId, save_path: Path, force_download=False):
        MAdults = await self.GameApi.char.getMAdults(MAdultId)
        if MAdults is None:
            return False

        MAdults_path = save_path / MAdultsPath
        MAdults_file = MAdults_path / str(MAdultId)
        if not MAdults_file.exists() or force_download:
            save_json(MAdults, MAdults_file)

        if self.GameApi.char.use_github_data:
            MAdults = await self.GameApi.char.getZHMAdults(MAdultId)
            if MAdults is None:
                log.warning(f"获取 [{MAdults}] 汉化数据失败, 等更新")
                return False

            MAdults_path = save_path / ZH_MAdultsPath
            MAdults_file = MAdults_path / str(MAdultId)
            if not MAdults_file.exists() or force_download:
                save_json(MAdults, MAdults_file)
