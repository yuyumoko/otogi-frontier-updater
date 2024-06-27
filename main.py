import os
import sys

import asyncio
import argparse

from pathlib import Path

from __version__ import __title__, __version__, __description__

from utils.logger import log

from utils import ArgRequire, ArgRequireOption, Menu


from core.LocalGame import LocalGame


from tkinter import filedialog


def input_fn(msg):
    return filedialog.askdirectory(title=msg)


ag = ArgRequire(
    ArgRequireOption(input_fn=input_fn, save=True, save_path="update_config.ini")
)

# DataPath = Path("temp_data")
# DataPath.mkdir(exist_ok=True)


@ag.apply(True, "选择游戏目录")
def get_game_path(game_path: Path):
    if not game_path.exists():
        log.error("游戏目录不存在")
        return

    if not LocalGame(game_path).validGamePath():
        log.error("游戏目录不正确")
        return

    return game_path


def request_game_path(game_path: Path = None):
    if game_path is None:
        game_path = Path(".")

    lg = LocalGame(game_path)
    if not lg.validGamePath():
        game_path = get_game_path()
        if game_path is None:
            return
        lg = LocalGame(game_path)
    return lg


async def check_update():
    from core.CheckUpdate import check_game_update

    lg = request_game_path()
    if lg is None:
        return

    await check_game_update(lg, None, False)
    log.info("更新完成")


async def check_translation():
    from core.CheckTranslate import check_translate

    lg = request_game_path()
    if lg is None:
        return

    await check_translate(lg)
    log.info("汉化文本更新完成")


async def install_client():
    from core.InstallClient import install_client

    lg = request_game_path()
    if lg is None:
        return

    await install_client(lg)
    log.info("客户端更新完成")


def run_check_update():
    asyncio.run(check_update())


def run_check_translation():
    asyncio.run(check_translation())


def run_install_client():
    asyncio.run(install_client())


def show_menu():
    try:
        Menu(
            title=f"{__title__} v{__version__} - {__description__} (第一次需要选择游戏目录)",
            options={
                run_check_update: "更新游戏缺少的资源文件",
                run_check_translation: "更新游戏汉化文件",
                run_install_client: "更新游戏html客户端 (首次需要更新, 为了支持更新的动画)",
            },
        ).show()
    except Exception as e:
        log.exception(e)
    finally:
        os.system("pause")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{__title__} v{__version__} - {__description__}",
        help="显示当前版本号",
    )

    parser.add_argument(
        "-c",
        "--check-update",
        action="store_true",
        help="检查游戏资源更新",
    )

    parser.add_argument(
        "-t",
        "--check-translation",
        action="store_true",
        help="检查游戏汉化文件更新",
    )

    parser.add_argument(
        "-i",
        "--install-client",
        action="store_true",
        help="安装客户端",
    )

    args = parser.parse_args()

    if args.check_update:
        run_check_update()

    if args.check_translation:
        run_check_translation()

    if args.install_client:
        run_install_client()

    if len(sys.argv) == 1:
        show_menu()
