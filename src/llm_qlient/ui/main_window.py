"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import platform
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from freshqt.core import Theme, Themeable, change_titlebar_theme
from freshqt.widgets import Divider, Button

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.ui.widgets.sidebar import Sidebar


class MainWindow(QWidget, Themeable):
    """
    Top-level main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("LLM Qlient")
        self.setWindowIcon(shared.icons["windowicon"])
        self.resize(1280, 720)
        self.setMinimumSize(640, 360)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        self.sidebar.add_page_button("Chats", shared.icons["hi-chat-bubble-oval-left"])
        self.sidebar.add_page_button("Agents", shared.icons["hi-users"])
        self.sidebar.add_page_button("Personas", shared.icons["hi-identification"])
        self.sidebar.add_page_button("Playground", shared.icons["hi-pencil-square"])
        self.sidebar.add_page_button("Models", shared.icons["hi-cube"])
        self.sidebar.layout().addStretch()
        self.sidebar.add_page_button("Settings", shared.icons["hi-cog-6-tooth"])

        for page_name, button in self.sidebar.page_buttons.items():
            if page_name == "LLM Qlient": continue
            button.clicked.connect(partial(self.change_page, page_name))
        
        self.current_page = ""

        dv = Divider(margin=3, orientation=Qt.Orientation.Vertical)
        shared.theme.add_widget(dv)
        layout.addWidget(dv)

    def update_theme(self, theme: Theme) -> None:
        log.info(f"Changed app theme to {theme.palette.name}")

        if platform.system() == "Windows":
            ret = change_titlebar_theme(self, theme.palette.is_dark)

            if ret != 0:
                log.warn(f"<fg.blue>change_titlebar_theme</> failed with code <fg.lightred>{ret}</>")

        else:
            log.info("Titlebar themeing is only supported on Windows currently.")

        self.setStyleSheet(f"background-color: {theme.qss(theme.palette.background_primary)};")

    def change_page(self, page_name: str) -> None:
        """
        Change the current page and update animations.

        Parameters
        ----------
        page_name
            Page name to switch to
        """

        if len(self.current_page) > 0:
            self.sidebar.page_buttons[self.current_page].variant = Button.Variant.GHOST

        self.current_page = page_name
        self.sidebar.page_buttons[page_name].variant = Button.Variant.SECONDARY
        self.sidebar.change_cursor(page_name)