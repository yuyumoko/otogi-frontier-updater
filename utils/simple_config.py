from pathlib import Path
from configparser import ConfigParser


class SimpleConfig(ConfigParser):
    __slots__ = ("configPath",)

    def __init__(self, configPath: Path | str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configPath = configPath
        if not self.read(configPath, encoding="utf-8"):
            configPath.parent.mkdir(parents=True, exist_ok=True)
            configPath.touch()
            self.read(configPath, encoding="utf-8")

    def set(self, section: str, option: str, value: str):
        if not self.has_section(section):
            self.add_section(section)
        super().set(section, option, value)
        with self.configPath.open("w", encoding="utf-8") as f:
            self.write(f)

    def remove_option(self, section: str, option: str) -> bool:
        super().remove_option(section, option)
        with self.configPath.open("w", encoding="utf-8") as f:
            self.write(f)
