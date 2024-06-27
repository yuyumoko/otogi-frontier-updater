import re
import ujson as json
import UnityPy

from pathlib import Path

from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from utils import log, save_json, file_size_format, UnityEnv
from config import http_proxy, CharaIconPath
from FileDataPath import (
    MasterDataPath,
    VieableEpisodeListPath,
    BGPath,
    BGMPath,
    AdventureVoicePath,
    StillVoicePath,
    StillSpinePath,
)

from core.OtogiFrontier import OtogiApi
from core.FetchGameRes import FetchGameRes
from core.LocalGame import LocalGame


def save_unity_voice(env: UnityEnv, output_path):
    for obj in env.objects:
        if obj.type.name == "AudioClip":
            clip = obj.read()
            for name, data in clip.samples.items():
                with (output_path / name).open("wb") as f:
                    f.write(data)


async def init_chara_icon_cache(GameApi: OtogiApi):
    all_char_icon_size = await GameApi.resource.getAllCharacterIconDataSize()
    log.info(f"图标大小: [{file_size_format(all_char_icon_size)}]")
    if not CharaIconPath.exists() or CharaIconPath.stat().st_size != all_char_icon_size:
        dl_bar = tqdm(total=all_char_icon_size, desc="更新缓存图标数据中", unit="B", unit_scale=True)
        chara_icon_file_f = CharaIconPath.open("wb+")

        def chunk_handler(chunk):
            dl_bar.update(len(chunk))
            chara_icon_file_f.write(chunk)

        await GameApi.resource.getAllCharacterIconData(chunk_handler)
        chara_icon_file_f.close()
        dl_bar.close()
    else:
        log.info(f"当前图标缓存已经是最新")


async def save_chara_res(char_id, output_path: Path, force_download=False):
    request_res_task = [
        FetchGameRes().save_chara_stand(char_id, output_path, force_download),
        FetchGameRes().save_home_stand(char_id, output_path, force_download),
    ]

    await tqdm_asyncio.gather(*request_res_task)


async def save_MScenes_MAdults_res(
    MSceneId, MAdultId, output_path: Path, force_download=False
):
    GameApi = OtogiApi(proxy=http_proxy)
    MScenes = await GameApi.char.getMScenes(MSceneId)
    MAdults = await GameApi.char.getMAdults(MAdultId)

    async def MScenes_handler(MScenes, output_path):
        GameApi = OtogiApi(proxy=http_proxy)
        for MScene in MScenes:
            if len(MScene["MSceneDetails"]) > 0:
                pbar = tqdm(MScene["MSceneDetails"], desc="获取章节资源")
                for MSceneDetail in pbar:
                    await save_chara_res(
                        MSceneDetail["MMonsterId"],
                        output_path,
                        force_download=force_download,
                    )
                    if bg_id := MSceneDetail.get("BackgroundImage"):
                        if (
                            not (output_path / BGPath / (bg_id + ".png")).exists()
                            or force_download
                        ):
                            (output_path / BGPath).mkdir(parents=True, exist_ok=True)
                            bg_data = await GameApi.resource.getAdventureBG(bg_id)
                            bg_env = UnityPy.load(bg_data)
                            for obj in bg_env.objects:
                                if obj.type.name == "Texture2D":
                                    data = obj.read()
                                    data_name = Path(data.container).name
                                    data.image.save(output_path / BGPath / data_name)

                    if bgm_name := MSceneDetail.get("BGM"):
                        if (
                            not (output_path / BGMPath / (bgm_name + ".m4a")).exists()
                            or force_download
                        ):
                            (output_path / BGMPath).mkdir(parents=True, exist_ok=True)
                            bgm_data = await GameApi.resource.getAdventureBGM(bgm_name)
                            bgm_env = UnityPy.load(bgm_data)
                            save_unity_voice(bgm_env, output_path / BGMPath)

                pbar.close()

            if MRichSceneDetails := MScene.get("MRichSceneDetails"):
                if len(MRichSceneDetails) > 0:
                    pbar = tqdm(MRichSceneDetails, desc="获取章节资源")
                    for MRichSceneDetail in pbar:
                        for chara in MRichSceneDetail["Characters"]:
                            await save_chara_res(
                                chara["MMonsterId"],
                                output_path,
                                force_download=force_download,
                            )

            
            if MSceneDetails := MScene.get("MSceneDetails"):
                if len(MSceneDetails) > 0:
                    pbar = tqdm(MSceneDetails, desc="获取章节资源")
                    for MSceneDetail in pbar:
                        await save_chara_res(
                                MSceneDetail["MMonsterId"],
                                output_path,
                                force_download=force_download,
                            )

                

    async def BGM_handler(MAdults, output_path):
        GameApi = OtogiApi(proxy=http_proxy)
        pbar = tqdm(MAdults["MAdultDetails"], desc="获取BGM资源")
        for info in pbar:
            bgm_name = info["BGM"]
            if bgm_name is None:
                continue

            if (
                not (output_path / BGMPath / (bgm_name + ".m4a")).exists()
                or force_download
            ):
                (output_path / BGMPath).mkdir(parents=True, exist_ok=True)
                bgm_data = await GameApi.resource.getAdventureBGM(bgm_name)
                bgm_env = UnityPy.load(bgm_data)
                save_unity_voice(bgm_env, output_path / BGMPath)
        pbar.close()

    async def Voice_handler(MSceneId, MAdultId, output_path):
        GameApi = OtogiApi(proxy=http_proxy)
        pbar = tqdm(range(2), desc="获取语音资源")
        AdventureVoice_path = output_path / AdventureVoicePath
        AdventureVoice_path.mkdir(parents=True, exist_ok=True)
        AdventureVoice_file = AdventureVoice_path / f"voice_adventure_{MSceneId}"
        if not AdventureVoice_file.exists() or force_download:
            AdventureVoice_file.mkdir(parents=True, exist_ok=True)
            AdventureVoice_data = await GameApi.resource.getAdventureVoice(MSceneId)
            AdventureVoice_env = UnityPy.load(AdventureVoice_data)
            save_unity_voice(AdventureVoice_env, AdventureVoice_file)
            pbar.update()

        StillVoice_path = output_path / StillVoicePath / str(MAdultId)
        if not StillVoice_path.exists() or force_download:
            StillVoice_path.mkdir(parents=True, exist_ok=True)
            StillVoice_data = await GameApi.resource.getCharacterStillVoice(MAdultId)
            StillVoice_env = UnityPy.load(StillVoice_data)
            save_unity_voice(StillVoice_env, StillVoice_path)
            pbar.update()
        pbar.close()

    async def Spine_handler(MAdultId, output_path):
        GameApi = OtogiApi(proxy=http_proxy)

        def spine_json_sorter(x):
            if "_" in x:
                f = re.findall(r"\d+", x.split("_")[-1])
                return int(f[0] if f else 0)
            return int(re.findall(r"\d+", x)[-1])

        StillSpine_path = output_path / StillSpinePath / str(MAdultId)
        if not StillSpine_path.exists() or force_download:
            StillSpine_path.mkdir(parents=True, exist_ok=True)
            StillSpine_data = await GameApi.resource.getCharacterStillSpine(MAdultId)
            # with (Path(".") / "test").open("wb") as f:
            #     f.write(StillSpine_data)
            StillSpine_env = UnityPy.load(StillSpine_data)
            atlas_list = []
            skel_json_list = []
            pbar = tqdm(StillSpine_env.objects, desc="获取Spine资源")
            for obj in pbar:
                if obj.type.name == "Texture2D":
                    data = obj.read()
                    data_name = Path(data.container).name
                    data.image.save(StillSpine_path / f"{data.name}.png")
                if obj.type.name == "TextAsset":
                    data = obj.read()
                    data_name = Path(data.container).name
                    output_path = StillSpine_path / data_name

                    if data_name == f"{MAdultId}.atlas.txt":
                        data_name = f"{MAdultId}.prefab.atlas.txt"

                    if data_name == f"{MAdultId}.json":
                        data_name = f"{MAdultId}.prefab.json"

                    output_path = StillSpine_path / data_name
                    try:
                        json.loads(data.text)
                        skel_json_list.append(output_path.stem)
                    except:
                        atlas_list.append(output_path)

                    if not output_path.exists() or force_download:
                        with output_path.open("wb") as f:
                            f.write(data.script)
            pbar.close()
            if len(skel_json_list) != 0:
                skel_json_list = sorted(skel_json_list, key=spine_json_sorter)
                fake_skel_json = {
                    "skeleton": {"spine": "0.0.0"},
                    "skeleton_list": skel_json_list,
                }
                save_json(fake_skel_json, StillSpine_path / f"{MAdultId}.json")

    handler_tasks = [
        MScenes_handler(MScenes, output_path),
        BGM_handler(MAdults, output_path),
        Voice_handler(MSceneId, MAdultId, output_path),
        Spine_handler(MAdultId, output_path),
    ]
    await tqdm_asyncio.gather(*handler_tasks)


async def save_episode_res(
    MSceneId,
    MAdultId,
    Description,
    output_path: Path,
    force_download=False,
):
    GameApi = OtogiApi(proxy=http_proxy)

    MScenes = await GameApi.char.getMScenes(MSceneId)
    if MScenes is None:
        log.warning(f"角色需要 [{Description}]")
        return

    MAdults = await GameApi.char.getMAdults(MAdultId)
    if MAdults is None:
        log.warning(f"获取MAdults[{MAdultId}]失败")
        return

    GameResApi = FetchGameRes(GameApi)
    await GameResApi.save_MScenes(MSceneId, output_path, force_download)
    await GameResApi.save_MAdults(MAdultId, output_path, force_download)

    await save_MScenes_MAdults_res(MSceneId, MAdultId, output_path, force_download)


async def save_specials(
    GameApi: OtogiApi, local_special_episodes, output_path: Path, force_download=False
):

    def is_local_episode(episode):
        return episode["MSceneAdultFlowId"] in [
            x["MSceneAdultFlowId"] for x in local_special_episodes
        ]

    res_special = []
    pbar = tqdm(GameApi.char.Specials, desc="获取报酬中")
    for special in pbar:
        title = special["Title"]
        MSceneId = special["MSceneId"]
        MAdultId = special["MAdultId"]
        Description = special["Description"]

        if not special["Viewable"]:
            print(f"报酬({title})未解锁")
            continue

        if is_local_episode(special):
            pbar.set_description(f"报酬已获取 [{title}]")
            continue

        res_special.append(special)

        await save_MScenes_MAdults_res(MSceneId, MAdultId, output_path, force_download)
    return res_special


async def check_game_update(
    lg: LocalGame, output_path: Path = None, force_download=False
):
    if output_path is None:
        output_path = lg.game_root

    log.info(f"正在检查资源更新..")

    local_ids = lg.getCharacterIDS()
    log.info(f"本地角色ID数量: {len(local_ids)}")

    GameApi = OtogiApi(proxy=http_proxy)

    log.info(f"正在初始化数据")
    MMonstersData = await GameApi.char.getMMonstersData()
    MSpiritsData = await GameApi.char.getMSpiritsData()

    save_json(MMonstersData, output_path / MasterDataPath / "MMonsters.json")
    save_json(MSpiritsData, output_path / MasterDataPath / "MSpirits.json")

    log.info(f"正在初始化图标数据")
    await init_chara_icon_cache(GameApi)

    log.info(f"正在获取可更新角色总数")
    game_ids = await GameApi.char.getUserCharacterIDS()
    log.info(f"可更新角色总数: {len(game_ids)}")
    
    diff_ids = list(set(game_ids).difference(set(local_ids)))
    
    exclude_ids = [80831, 80261, 15111]
    diff_ids = [x for x in diff_ids if x not in exclude_ids]
    
    log.info(f"正在获取购入报酬更新")
    local_special = lg.getSpecial()
    local_special_Episodes = local_special["Episodes"]
    res_special = await save_specials(
        GameApi, local_special_Episodes, output_path, force_download
    )
    if len(res_special) != 0:
        local_special["Episodes"] += res_special
        lg.saveDataSpecial(local_special)

    log.info(f"检测到 [{len(diff_ids)}] 个角色需要更新")

    for index, char_id in enumerate(diff_ids):
        charInfo = await GameApi.char.getCharacterInfo(char_id)
        if charInfo is None:
            log.warning(f"获取角色信息失败: {char_id}")
            continue
        charName = charInfo["n"]

        log.info(f"正在更新角色 [{charName}] ({index + 1}/{len(diff_ids)})")

        log.info(f"正在下载资源")
        await save_chara_res(char_id, output_path, force_download=force_download)

        log.info(f"获取角色章节信息")
        char_episodes = await GameApi.char.getCharacterEpisodes(char_id)

        VieableEpisodeFile = output_path / VieableEpisodeListPath / str(char_id)
        save_json(char_episodes["Episodes"], VieableEpisodeFile)

        for episode in char_episodes["Episodes"]:
            MSceneId = episode["MSceneId"]
            MAdultId = episode["MAdultId"]
            Description = episode["Description"]

            # 跳过非h章节
            if MAdultId is None:
                continue

            log.info(f"正在下载章节资源: [{MSceneId} - {MAdultId}]")
            await save_episode_res(
                MSceneId,
                MAdultId,
                Description,
                output_path,
                force_download=force_download,
            )

        request_res_task = [
            FetchGameRes().save_chara_icon(char_id, output_path, force_download),
            FetchGameRes().save_stand_image(char_id, output_path, force_download),
        ]
        await tqdm_asyncio.gather(*request_res_task)
