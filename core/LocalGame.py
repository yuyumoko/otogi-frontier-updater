from pathlib import Path

from utils.helper import load_json, save_json
from FileDataPath import CharacterIconPath, SpecialPath, ZH_MScenesPath, ZH_MAdultsPath


def get_path_ids(path: Path):
    return [x.stem for x in path.iterdir() if x.stem.isdigit()]


class LocalGame:
    game_root: Path

    def __init__(self, game_root: Path):
        self.game_root = game_root

    def validGamePath(self):
        homestand_exists = (self.game_root / CharacterIconPath).exists()
        special_exists = (self.game_root / SpecialPath).exists()
        return homestand_exists and special_exists

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
        return self.getCharacters()

    def getSpecial(self):
        return load_json(self.game_root / SpecialPath)

    def saveDataSpecial(self, special_data, output_path: Path=None):
        path_root = output_path or self.game_root
        save_json(special_data, path_root / SpecialPath)

    def getZH_MSceneIds(self):
        return get_path_ids(self.game_root / ZH_MScenesPath)

    def getZH_MAdultIds(self):
        return get_path_ids(self.game_root / ZH_MAdultsPath)
