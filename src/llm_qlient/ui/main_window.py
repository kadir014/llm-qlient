"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import platform

from PyQt6.QtWidgets import QWidget
from freshqt.core import Theme, Themeable, change_titlebar_theme

from llm_qlient.core import log


class MainWindow(QWidget, Themeable):
    """
    Top-level main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("LLM Qlient")
        self.resize(1280, 720)
        self.setMinimumSize(1280, 720)

    def update_theme(self, theme: Theme) -> None:
        if platform.system() == "Windows":
            ret = change_titlebar_theme(self, theme.palette.is_dark)

            if ret != 0:
                log.warn(f"<fg.blue>change_titlebar_theme</> failed with code <fg.lightred>{ret}</>")
        
        else:
            log.info("Titlebar themeing is only supported on Windows currently.")