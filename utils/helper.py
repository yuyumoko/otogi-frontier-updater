import UnityPy
import requests
import psutil
import ujson as json
from pathlib import Path
from typing import TypeVar

UnityEnv = TypeVar("UnityEnv", bound="UnityPy.environment.Environment")


class Error_Message(Exception):
    def __init__(self, message=""):
        self.message = message

    def __repr__(self):
        return self.message


def file_size_format(size):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    while size >= 1024:
        size /= 1024
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def ids_difference(old_ids, new_ids):
    return list(set(new_ids).difference(set(old_ids)))


def check_proxy(proxy_url):
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        res = requests.get(
            url="http://icanhazip.com/", timeout=2, proxies={"http": proxy_url}
        )
        proxyIP = res.text
        return proxyIP
    except:
        raise Exception("代理IP无效! : " + proxy_url)


def parse_csv_from_string(csv_content: str):
    lines = csv_content.strip().splitlines()

    for line in lines[1:]:
        parts = line.strip().split(",")

        if len(parts) == 3:
            url_path = parts[0]
            md5 = parts[1]
            size = int(parts[2])
            yield (url_path, md5, size)
        else:
            print(f"Unexpected line format: {line}")

def check_process_running(processName: Path | str):
    processName = processName.name if isinstance(processName, Path) else processName
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False