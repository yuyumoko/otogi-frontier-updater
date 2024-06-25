import os
import re
from typing import Callable
import dumb_menu


def _show_clean_menu(options, selected_index):
    os.system("cls" if os.name == "nt" else "clear")
    for i, option in enumerate(options):
        if isinstance(option, dict):
            if option.get("__title__"):
                print(option["__title__"])

    for i, option in enumerate(options):
        if isinstance(option, dict):
            continue
        if i == selected_index:
            print(f"> {option}")
        else:
            print(f"  {option}")


def _scan_short_cuts(options):
    shortcuts = {}
    for i, option in enumerate(options):
        if isinstance(option, dict):
            continue
        match = re.match(r"\[(.*)\](.*)", option)
        if match:
            shortcut, text = match.group(1, 2)
            shortcuts[shortcut] = i
    return shortcuts


dumb_menu.show_clean_menu = _show_clean_menu
dumb_menu.scan_short_cuts = _scan_short_cuts


class Menu:
    """
    例子
    Menu(
        title="---这是标题---",
        options={
            test1: "这是选项1",
            test2: "这是选项2",
        },
        args={test2: {"arg3": 123}},
    ).show()

    """

    def __init__(
        self, options: dict[str, Callable], args=None, title: str = None
    ) -> None:
        self.options = options
        self.args = args if args is not None else {}
        self.title = title

    def show(self):
        menu_options = list(self.options.values())

        if self.title is not None:
            menu_options.append({"__title__": self.title})

        self.index = dumb_menu.get_menu_choice(menu_options, True)
        func = list(self.options.keys())[self.index]
        if func in self.args.keys():
            return func(**self.args[func])
        else:
            return func()
