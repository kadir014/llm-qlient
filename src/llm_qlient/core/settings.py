"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from typing import Any

import os
import json
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal


def load_settings() -> dict[str, Any]:
    """ Load user settings if it exists. """

    path = Path.cwd()

    if not os.path.exists(path) or not os.path.isfile(path):
        return {}
    
    with open(path, "r", encoding="utf-8") as file:
        return json.loads(file.read())


def save_settings(settings: dict[str, Any], filename: str = "settings.json") -> None:
    """ Save user settings to a file. """

    path = Path.cwd() / filename

    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(settings))


def merge_settings(default: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
    """ Merge default and user settings. """

    new = {}
    
    for key in default:
        if key in user:
            new[key] = user[key]
        else:
            new[key] = default[key]

    return new


class Settings(QObject):
    
    changed = pyqtSignal()

    def __init__(self, default: dict[str, Any]):
        super().__init__()

        self.__default = default
        self.__user = load_settings()
        self.__front = merge_settings(self.__default, self.__user)

    def __getitem__(self, key: str) -> Any:
        return self.__front[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.__user[key] = value
        save_settings(self.__user)
        self.__front = merge_settings(self.__default, self.__user)

        # Get only changed fields and emit them
        # might help optimize if settings get too large
        self.changed.emit()