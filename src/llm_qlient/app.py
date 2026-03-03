"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import os
import platform
from pathlib import Path

from PyQt6.QtCore import qInstallMessageHandler, QtMsgType, QMessageLogContext
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from freshqt.assets import HEROICONS
from panllm import LLM, LLMBackend, LLMConfig
import miniprofiler

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.types import SettingsDict
from llm_qlient.core.generator import Generator
from llm_qlient.ui.main_window import MainWindow
from llm_qlient.ui.widgets.toast import ToastManager

from freshqt.palettes.catppuccin import (
    UI_CATPPUCCIN_MOCHA,
    UI_CATPPUCCIN_LATTE,
    UI_CATPPUCCIN_FRAPPE
)
from freshqt.palettes.dracula import UI_DRACULA, UI_ALUCARD


class App:
    """
    GUI application entry point of llm-qlient.
    """

    def __init__(self) -> None:
        prof = miniprofiler.Profiler()
        with prof.profile("init"):

            # Redirect Qt's messages to our logger
            qInstallMessageHandler(self._handle_qt_log)

            shared.qapp = QApplication([])

            ROOT = Path.cwd()

            for root, _, files in os.walk(ROOT / "data" / "fonts"):
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
                font = shared.qapp.font()
                font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
                shared.qapp.setFont(font)

            # SVG icons have to be loaded before any raster icons so Qt can select proper icon engine
            for icon_path in HEROICONS.keys():
                shared.icons.load_single(icon_path)
            shared.icons.load(ROOT / "data" / "icons")

            shared.theme.font_family = "Outfit"
            shared.theme.update_palette(UI_CATPPUCCIN_MOCHA)

            shared.settings.changed.connect(self._settings_changed)

            shared.contents.load_all()

            shared.model = LLM(LLMConfig(""), LLMBackend.DUMMY)

            shared.gen = Generator()
            shared.gen.start()

            shared.main_window = MainWindow()
            shared.theme.add_widget(shared.main_window)
            shared.main_window.hide()

            shared.toasts = ToastManager(shared.main_window)

            shared.cleanup.connect(self._cleanup)

        log.info(f"App is initialized in {log.t(prof['init'].last)}")

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

    def _settings_changed(self, changed: SettingsDict) -> None:
        if "theme" in changed:
            if changed["theme"].startswith("builtin:"):
                theme_name = changed["theme"].replace("builtin:", "").strip().lower()
                themes = {
                    "catppuccin mocha": UI_CATPPUCCIN_MOCHA,
                    "catppuccin frappe": UI_CATPPUCCIN_FRAPPE,
                    "catppuccin latte": UI_CATPPUCCIN_LATTE,
                    "dracula": UI_DRACULA,
                    "alucard": UI_ALUCARD
                }

                if theme_name not in themes:
                    theme_name = "catppuccin mocha"

                theme = themes[theme_name]

                shared.theme.font_family = "Outfit"
                shared.theme.update_palette(theme)

        if "ui_font_scale" in changed:
            shared.theme.font_scale = changed["ui_font_scale"]

    def _cleanup(self) -> None:
        shared.gen.should_run = False
        shared.gen._queue.shutdown()
        shared.gen.wait(5000)

        if shared.model is not None:
            shared.model.release()

    def run(self) -> int:
        """ Start running application. """

        shared.main_window.show()

        # After the main window is shown, all the layouts will be settled
        # So this is the time to set the inital page displayed
        # otherwise certain animations will not work
        shared.main_window.change_page(shared.main_window.pages[0].id)

        # Emit settings signal once so all widgets listening to setting
        # changes can initialize themselves
        shared.settings._update(front=True)

        return shared.qapp.exec()