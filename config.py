from pathlib import Path
from utils import SimpleConfig

CachePath = Path("update_cache")
CachePath.mkdir(exist_ok=True)
CharaIconPath = CachePath / "chara_icon"


update_config = SimpleConfig(Path("update_config.ini"))
section = "config"

if not update_config.has_section(section):
    update_config.add_section(section)

if not update_config.has_option(section, "http_proxy"):
    update_config.set(section, "http_proxy", "")

http_proxy = update_config.get(section, "http_proxy", fallback="")

update_server_path = Path("update_server.ini")
if not update_server_path.exists():
    raise FileNotFoundError(f"you need update_server.ini file")

update_server_config = SimpleConfig(update_server_path)
resource_repo = update_server_config.get("github", "repo")
resource_branch = update_server_config.get("github", "branch")
resource_token = update_server_config.get("github", "token", fallback="")
