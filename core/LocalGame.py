from pathlib import Path

from utils.helper import load_json, save_json
from FileDataPath import CharacterIconPath, SpecialPath


class LocalGame:
    game_root: Path

    def __init__(self, game_root: Path):
        self.game_root = game_root

    def valid_game_path(self):
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

    def saveDataSpecial(self, special_data):
        special_path = self.game_root / SpecialPath
        special_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(special_path, special_data)
