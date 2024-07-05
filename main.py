import os
import sys

import asyncio
import argparse

from datetime import datetime
from pathlib import Path

from __version__ import __title__, __version__, __description__

from utils.logger import log

from utils import ArgRequire, ArgRequireOption, Menu

from core.OtogiFrontier import OtogiApi
from core.LocalGame import LocalGame

from config import setGameToken

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


def require_game_path(game_path: Path = None):
    if game_path is None:
        game_path = Path(".")

    lg = LocalGame(game_path)
    if not lg.validGamePath():
        game_path = get_game_path()
        if game_path is None:
            return
        lg = LocalGame(game_path)
    return lg


@ag.apply(lambda msg: input(msg), "输入游戏token")
def get_game_token(token):
    if not OtogiApi.valid_access_token(token):
        log.error("无效的token, 类似于: 80f2b125-bf29-4205-9d4e-ab6d06614f55")
        return

    return token


async def check_update(update_output_path: Path = None, force=False):
    from core.CheckUpdate import check_game_update

    lg = require_game_path()
    if lg is None:
        return

    if force:
        log.info("强制检查游戏资源文件")
        lg.no_character_ids = True

    if update_output_path is not None:
        update_output_path = lg.game_root / update_output_path

    await check_game_update(lg, update_output_path=update_output_path)
    log.info("更新完成")


token_login_print = """
注意: *请先更新离线资源到最新后再选次选项*
-------------------------------------------------------
这个是游戏已经出的角色, 更新游戏资源又没有
说明服务器资源并没有更新, 但你可以通过获取游戏token强制更新
这样的话, 会缺少汉化文件
更新后输出的更新包可以提供给管理员, 用于更新服务器资源
          """


async def check_update_with_token(token=None, print_help=True):
    if print_help:
        print(
            token_login_print
            + """
    token获取方法:
    -------------------------------------------------------
    进入游戏后, 浏览器按F12 选择Network(网络)
    然后游戏内点击角色一览
    在控制台看到All并选择, 找到Headers里面的Token字段即可
            """
        )

    if token is None:
        token = get_game_token()

    update_output_path = Path(
        f"更新数据/[{datetime.now().strftime('%Y-%m-%d')}] 服务器数据"
    )

    await OtogiApi(token).char.getUserCharacterIDS()

    setGameToken(token)
    await check_update(update_output_path)
    log.info(f"更新数据已保存到游戏目录下的: {update_output_path}")


async def get_game_token_with_login_id(dmm_login_id, print_help=True):
    if print_help:
        print()


async def check_update_with_login_id(only_get_token=False):
    help_msg = """
    使用账号:
    -------------------------------------------------------
    在当前目录下的 update_config.ini 文件中添加
    [game]
    login_id = 登录账号
    password = 登录密码

    添加好后重新运行程序即可
    """

    get_token_msg = """
    -------------------------------------------------------
    仅获取游戏的token, 可能使你现在其他端的游戏登录失效
    其他端游戏重新登录后会导致次token失效
    
    请不要随意给别人, 程序也不会保存账号或者密码
    """

    if only_get_token:
        print(token_login_print + help_msg)
    else:
        print(help_msg + get_token_msg)

    from config import dmm_login_id, dmm_password, http_proxy
    from core.DmmAuth import DmmAuth

    if dmm_login_id is None or dmm_login_id == "":
        log.error("请先设置账号密码")
        return

    log.info(f"正在登录...")
    auth = DmmAuth(dmm_login_id, dmm_password, "otogi_f_r", http_proxy)
    data = await auth.makeRequest("https://otogi-rest.otogi-frontier.com/api/DMM/auth")
    await auth.session.close()
    token = data["hash"]

    if only_get_token:
        log.info(f"游戏token: {token}")
        return

    await check_update_with_token(token, print_help=False)


async def check_translation():
    from core.CheckTranslate import check_translate

    lg = require_game_path()
    if lg is None:
        return

    await check_translate(lg)
    log.info("汉化文本更新完成")


async def install_client():
    from core.InstallClient import install_client

    lg = require_game_path()
    if lg is None:
        return

    await install_client(lg)
    log.info("客户端更新完成")


def run_check_update():
    asyncio.run(check_update())


def run_check_update_force():
    asyncio.run(check_update(force=True))


def run_check_update_with_token():
    asyncio.run(check_update_with_token())


def run_check_update_with_login_id():
    asyncio.run(check_update_with_login_id())


def run_only_get_token_with_login_id():
    asyncio.run(check_update_with_login_id(only_get_token=True))


def run_check_translation():
    asyncio.run(check_translation())


def run_install_client():
    asyncio.run(install_client())


def run_game_web_server(host="0.0.0.0", port=8182):
    import webbrowser
    from aiohttp import web

    lg = require_game_path()
    if lg is None:
        return
    app = web.Application()
    app.add_routes([web.static("/", lg.game_root, show_index=True)])

    if (lg.game_root / "启动离线版.html").exists():
        webbrowser.open(f"http://{host}:{port}/启动离线版.html")
    else:
        webbrowser.open(f"http://{host}:{port}/index.html")

    web.run_app(app, host=host, port=port)


def show_menu():
    try:
        Menu(
            title=f"{__title__} v{__version__} - {__description__} (第一次需要选择游戏目录)",
            options={
                run_check_update: "1.更新文件",
                run_check_update_force: "2.强制更新所有文件(时间可能较长)",
                run_check_translation: "3.更新汉化",
                run_install_client: "4.更新游戏html客户端 (首次需要更新, 为了支持更新的动画)",
                run_only_get_token_with_login_id: "5.获取游戏token",
                run_check_update_with_token: "6.输入token更新文件",
                run_check_update_with_login_id: "7.使用账号更新文件",
                run_game_web_server: "8.我只想启动游戏",
            },
        ).show()
    except Exception as e:
        if "Expected string or C-contiguous bytes-like object" in repr(e):
            log.error("请获取 update_server.ini 文件到运行目录下, token不是游戏token")
        else:
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
        "-ct",
        "--check-update-with-token",
        action="store_true",
        help="使用游戏的token更新资源",
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

    parser.add_argument(
        "-w",
        "--web-server",
        action="store_true",
        help="启动游戏web服务器",
    )

    args = parser.parse_args()

    if args.check_update:
        run_check_update()

    if args.check_update_with_token:
        run_check_update_with_token()

    if args.check_translation:
        run_check_translation()

    if args.install_client:
        run_install_client()

    if args.web_server:
        run_game_web_server()

    if len(sys.argv) == 1:
        show_menu()
