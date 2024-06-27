import asyncio
from pathlib import Path

from tqdm.asyncio import tqdm_asyncio

from utils import log

from core.DataServer.GitHubServer import GitHubServer, save_server_binary
from core.LocalGame import LocalGame

async def download(names, server_path, output_path, download_num=20):
    semaphore = asyncio.Semaphore(download_num)
    tasks = [save_server_binary(semaphore, name, server_path, output_path) for name in names]
    await tqdm_asyncio.gather(*tasks)

async def install_client(lg: LocalGame, output_path: Path = None):
    if output_path is None:
        output_path = lg.game_root

    log.info(f"正在更新客户端...")
    res_server = GitHubServer()
    await res_server.init()

    clients = res_server.hash_data['client'].keys()
    await download(clients, "client/", output_path)
    
    index_html = output_path / "index.html"
    index2_html = output_path / "启动离线版.html"
    if index_html.exists() and index2_html.exists():
        index_html.unlink()
        index2_html.rename(index_html)
        
    
