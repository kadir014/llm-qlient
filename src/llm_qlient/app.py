"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import os
import platform
from time import perf_counter
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from freshqt.assets import HEROICONS

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.ui.main_window import MainWindow


class App:
    """
    GUI application entry point of llm-qlient.
    """

    def __init__(self) -> None:
        start = perf_counter()

        self.qapp = QApplication([])

        # TODO: better path for data fonts icons etc

        for root, _, files in os.walk("data/fonts"):
            for file in files:
                fontpath = os.path.join(root, file)
                font_id = QFontDatabase.addApplicationFont(fontpath)
                if font_id < 0:
                    log.warn(f"Font '{file}' couldn't load.")
                else:
                    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    log.info(f"Font '{file}' loaded in family {font_family}")

        if platform.system() == "Windows":
            # https://stackoverflow.com/a/67219364
            # PreferNoHinting solves fonts looking weird on Windows
            font = self.qapp.font()
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            self.qapp.setFont(font)

        # SVG icons have to be loaded before any raster icons so Qt can select proper icon engine
        for iconname in HEROICONS:
            iconpath = HEROICONS[iconname]
            icon = QIcon(str(iconpath.absolute()))
            shared.icons[iconname] = icon
            log.info(f"Icon {iconname} loaded at path '{iconpath}'")

        for root, _, files in os.walk("data/icons"):
            root = Path(root)
            for file in files:
                iconpath = root / file
                iconname = iconpath.stem
                icon = QIcon(str(iconpath.absolute()))
                shared.icons[iconname] = icon
                log.info(f"Icon {iconname} loaded at path '{iconpath}'")

        shared.theme.font_family = "Outfit"

        self.mainwindow = MainWindow()
        shared.theme.add_widget(self.mainwindow)
        self.mainwindow.hide()

        elapsed = perf_counter() - start
        log.info(f"App is initialized in <fg.lightcyan>{round(elapsed, 3)}</>s (<fg.lightcyan>{round(elapsed*1000, 3)}</>ms)")

    def run(self) -> int:
        self.mainwindow.show()

        # After the mainwindow is shown, all the layouts will be settled
        # So this is the time to set the inital page displayed
        self.mainwindow.change_page("Chats")

        return self.qapp.exec()