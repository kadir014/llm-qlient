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

from PyQt6.QtCore import qInstallMessageHandler, QtMsgType, QMessageLogContext
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from freshqt.assets import HEROICONS

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.ui.main_window import MainWindow
from llm_qlient.ui.icon_manager import IconManager

from freshqt.palettes.catppuccin import UI_CATPPUCCIN_MOCHA


class App:
    """
    GUI application entry point of llm-qlient.
    """

    def __init__(self) -> None:
        start = perf_counter()

        # Redirect Qt's messages to our logger
        qInstallMessageHandler(self._handle_qt_log)

        ROOT = Path.cwd()

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

        shared.icons.load(ROOT / "data" / "icons")

        shared.theme.font_family = "Outfit"
        shared.theme.update_palette(UI_CATPPUCCIN_MOCHA)

        self.mainwindow = MainWindow()
        shared.theme.add_widget(self.mainwindow)
        self.mainwindow.hide()

        elapsed = perf_counter() - start
        log.info(f"App is initialized in <fg.lightcyan>{round(elapsed, 3)}</>s (<fg.lightcyan>{round(elapsed*1000, 3)}</>ms)")

    def _handle_qt_log(self, type_: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
        level_map = {
            QtMsgType.QtDebugMsg: log.LogLevel.DEBUG,
            QtMsgType.QtInfoMsg: log.LogLevel.INFO,
            QtMsgType.QtSystemMsg: log.LogLevel.INFO,
            QtMsgType.QtWarningMsg: log.LogLevel.WARNING,
            QtMsgType.QtCriticalMsg: log.LogLevel.ERROR,
            QtMsgType.QtFatalMsg: log.LogLevel.FATAL
        }

        new_msg = f"<fg.green>[Qt]</> {msg}"

        log.log(level_map[type_], new_msg)

    def run(self) -> int:
        self.mainwindow.show()

        # After the mainwindow is shown, all the layouts will be settled
        # So this is the time to set the inital page displayed
        # otherwise certain animations will not work
        self.mainwindow.change_page(self.mainwindow.pages[0].id)

        # Emit settings signal once so all widgets listening to setting
        # changes can initialize themselves
        shared.settings.changed.emit()

        return self.qapp.exec()