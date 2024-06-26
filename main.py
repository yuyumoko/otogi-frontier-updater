import os
import sys

import asyncio
import argparse

from pathlib import Path

from __version__ import __title__, __version__, __description__

from utils.logger import log

from utils import ArgRequire, ArgRequireOption, Menu


from core.LocalGame import LocalGame
from core.CheckUpdate import check_game_update

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

    if not LocalGame(game_path).valid_game_path():
        log.error("游戏目录不正确")
        return

    return game_path


async def check_update(game_path: Path = Path(".")):
    lg = LocalGame(game_path)
    if not lg.valid_game_path():
        game_path = get_game_path()
        if game_path is None:
            return
        lg = LocalGame(game_path)

    await check_game_update(lg, None, False)
    log.info("更新完成")


def run_check_update():
    asyncio.run(check_update())


def show_menu():
    # try:
    Menu(
        title=f"{__title__} v{__version__} - {__description__}",
        options={
            run_check_update: "自动更新游戏缺少的资源文件 - (第一次需要选择游戏目录)"
        },
    ).show()
    # except Exception as e:
    #     log.error(e)
    # finally:
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

    args = parser.parse_args()

    if args.check_update:
        run_check_update()

    if len(sys.argv) == 1:
        show_menu()
