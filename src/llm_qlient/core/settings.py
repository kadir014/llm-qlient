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

from llm_qlient.core import log
from llm_qlient.core.types import SettingsDict


def load_settings(filename: str = "settings.json") -> SettingsDict:
    """
    Load user settings if it exists.
    
    Parameters
    ----------
    filename
        Name of the file to read
    """

    path = Path.cwd() / filename

    if not os.path.exists(path) or not os.path.isfile(path):
        log.debug("No user settings file found.")
        return {}
    
    with open(path, "r", encoding="utf-8") as file:
        return json.loads(file.read())


def save_settings(settings: SettingsDict, filename: str = "settings.json") -> None:
    """
    Save user settings to a file.

    NOTE: Overwrites any file with the same name.
    
    Parameters
    ----------
    settings
        User settings (subset of default settings)
    filename
        Name of the file to write on
    """

    path = Path.cwd() / filename

    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(json.dumps(settings))

    except OSError as e:
        log.error(f"Could't write settings on <fg.yellow>{filename}</>. Traceback:\n{e}")


def merge_settings(
        default: SettingsDict,
        user: SettingsDict
        ) -> tuple[SettingsDict, SettingsDict]:
    """
    Merge default and user settings.

    Returns a tuple of only changed and merged settings.
    
    Parameters
    ----------
    default
        Default settings
    user
        User settings (subset of default)
    """

    new = {}
    changed = {}
    
    for key in default:
        if key in user:
            new[key] = user[key]
            changed[key] = user[key]
        else:
            new[key] = default[key]

    return changed, new


class Settings(QObject):
    """
    Settings manager.
    """
    
    # Signals can't take fancy GenericAlias unfortunately
    changed = pyqtSignal(dict)

    def __init__(self, default: SettingsDict):
        super().__init__()

        self.__default = default
        self.__user = load_settings()
        self.__front = merge_settings(self.__default, self.__user)[1]

    def _update(self, front: bool = False) -> None:
        """ Update front & emit. """
        changed, self.__front = merge_settings(self.__default, self.__user)
        emit = self.__front if front else changed
        self.changed.emit(emit)

    def __getitem__(self, key: str) -> Any:
        return self.__front[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.__user[key] = value
        save_settings(self.__user)
        self._update()