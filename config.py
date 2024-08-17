import os
from pathlib import Path
from utils import SimpleConfig, log, check_proxy

Game = {"token": ""}


def setGameToken(token):
    Game["token"] = token


def getGameToken():
    return Game["token"]


CachePath = Path("update_cache")
CachePath.mkdir(exist_ok=True)
CharaIconPath = CachePath / "chara_icon"


update_config = SimpleConfig(Path("update_config.ini"))
section = "config"

if not update_config.has_section(section):
    update_config.add_section(section)

if not update_config.has_option(section, "http_proxy"):
    update_config.set(section, "http_proxy", "")

if not update_config.has_option(section, "update_all_resources"):
    update_config.set(section, "update_all_resources", "0")

if not update_config.has_option(section, "use_github_mirror"):
    update_config.set(section, "use_github_mirror", "1")

http_proxy = update_config.get(section, "http_proxy", fallback="")

if http_proxy != "":
    log.info(f"正在检查代理可用性: {http_proxy}")
    if not check_proxy(http_proxy):
        log.error("代理不可用")
        raise Exception("代理不可用")

update_all_resources = update_config.getboolean(section, "update_all_resources", fallback=False)

use_github_mirror = update_config.getboolean(section, "use_github_mirror", fallback=True)

update_server_path = Path("update_server.ini")
if not update_server_path.exists():
    log.error("update_server.ini not found")


update_server_config = SimpleConfig(update_server_path)
resource_repo = update_server_config.get("github", "repo")
resource_branch = update_server_config.get("github", "branch")
resource_token = update_server_config.get("github", "token", fallback="")

if not update_config.has_section("game"):
    update_config.add_section("game")
    update_config.set("game", "login_id", "")
    update_config.set("game", "password", "")

dmm_login_id = update_config.get("game", "login_id", fallback="")
dmm_password = update_config.get("game", "password", fallback="")
