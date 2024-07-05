import asyncio

from pathlib import Path

from tqdm.asyncio import tqdm_asyncio

from utils import log, ids_difference
from FileDataPath import (
    ZH_MScenesPath,
    ZH_MAdultsPath,
)

from core.DataServer.GitHubServer import GitHubServer, save_server_json
from core.LocalGame import LocalGame


async def download(ids, server_path, output_path, download_num=20):
    semaphore = asyncio.Semaphore(download_num)
    tasks = [save_server_json(semaphore, id, server_path, output_path) for id in ids]
    await tqdm_asyncio.gather(*tasks)


async def check_translate(lg: LocalGame, output_path: Path = None, download_num=20):
    if output_path is None:
        output_path = lg.game_root

    log.info(f"正在检查汉化更新..")

    localMSceneIds = lg.getZH_MSceneIds()
    localMAdultIds = lg.getZH_MAdultIds()

    log.info(f"汉化场景：{len(localMSceneIds)}")
    log.info(f"侍寝场景：{len(localMAdultIds)}")

    log.info(f"正在获取最新汉化资源列表...")
    res_server = GitHubServer()
    await res_server.init()

    # fmt: off
    diff_MSceneIds = ids_difference(localMSceneIds, res_server.hash_data["typeadv"]["MScenes_TW"].keys())
    diff_MAdultIds = ids_difference(localMAdultIds, res_server.hash_data["jsoncn"].keys())
    
    if "MStory" in diff_MSceneIds:
        diff_MSceneIds.remove("MStory")
    # fmt: on

    log.info(f"新增场景：{len(diff_MSceneIds)}")
    log.info(f"新增侍寝：{len(diff_MAdultIds)}")

    log.info(f"正在下载汉化文本...")
    # fmt: off
    if len(diff_MSceneIds) > 0:
        await download(diff_MSceneIds, "typeadv/MScenes_TW/", output_path / ZH_MScenesPath, download_num)
    if len(diff_MAdultIds) > 0:
        await download(diff_MAdultIds, "jsoncn/", output_path / ZH_MAdultsPath, download_num)
    # fmt: on
