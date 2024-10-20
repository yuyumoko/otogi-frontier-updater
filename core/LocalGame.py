from pathlib import Path

from utils.helper import load_json, save_json
from FileDataPath import (
    CharacterIconPath,
    SpecialPath,
    ZH_MScenesPath,
    ZH_MAdultsPath,
    VieableEpisodeListPath,
)


def get_path_ids(path: Path):
    return [x.stem for x in path.iterdir() if x.stem.isdigit()]


class LocalGame:
    game_root: Path
    no_character_ids: bool

    def __init__(self, game_root: Path, no_character_ids=False):
        self.game_root = game_root
        self.no_character_ids = no_character_ids

    def validGamePath(self):
        homestand_exists = (self.game_root / CharacterIconPath).exists()
        special_exists = (self.game_root / SpecialPath).exists()
        return homestand_exists and special_exists

    def join(self, *args):
        return self.game_root / Path(*args)

    def remove_icon(self, character_id):
        path = self.game_root / CharacterIconPath / f"{character_id}.png"
        if path.exists():
            path.unlink()

    def find_MSceneId_or_MAdultId(self, id):
        for file in (self.game_root / VieableEpisodeListPath).iterdir():
            if not file.name.isdigit():
                continue

            json_data = load_json(file)
            episodes = (
                json_data["Episodes"] if isinstance(json_data, dict) else json_data
            )
            for episode in episodes:
                if episode["MSceneId"] == id or episode["MAdultId"] == id:
                    return int(file.stem)

    def getCharacters(self):
        exclude_ids = [
            0,
        ]
        homestand = self.game_root / CharacterIconPath
        return [
            int(x.stem)
            for x in homestand.iterdir()
            if x.stem.isdigit() and x.stem[-1] == "1" and int(x.stem) not in exclude_ids
        ]

    def getCharacterIDS(self):
        if self.no_character_ids:
            return []
        return self.getCharacters()

    def getSpecial(self):
        return load_json(self.game_root / SpecialPath)

    def saveDataSpecial(self, special_data, output_path: Path = None):
        path_root = output_path or self.game_root
        save_json(special_data, path_root / SpecialPath)

    def getZH_MSceneIds(self):
        return get_path_ids(self.game_root / ZH_MScenesPath)

    def getZH_MAdultIds(self):
        return get_path_ids(self.game_root / ZH_MAdultsPath)
