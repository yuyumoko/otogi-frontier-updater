import UnityPy
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