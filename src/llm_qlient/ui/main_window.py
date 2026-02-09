"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import platform
import importlib
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QColor
from freshqt.core import Theme, Themeable, change_titlebar_theme
from freshqt.widgets import Divider, Button

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.models import Page
from llm_qlient.ui.widgets.sidebar import SideBar
from llm_qlient.ui.widgets.statusbar import StatusBar


class MainWindow(QWidget, Themeable):
    """
    Top-level main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("LLM Qlient")
        self.setWindowIcon(shared.icons.get("windowicon"))
        self.resize(1280, 720)
        self.setMinimumSize(640, 360)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.sidebar = SideBar()
        layout.addWidget(self.sidebar)

        self.pages = (
            Page("chats", "hi-chat-bubble-oval-left"),
            Page("characters", "hi-users"),
            Page("personas", "hi-identification"),
            Page("playground", "hi-pencil-square"),
            Page("models", "hi-cube"),
            Page("settings", "hi-cog-6-tooth")
        )

        self.current_page = self.pages[0]

        for page in self.pages:
            self.sidebar.add_page_button(page)
        
        self.sidebar.layout().insertStretch(self.sidebar.layout().count() - 2)

        for page in self.pages:
            button = self.sidebar.page_buttons[page.id]
            button.clicked.connect(partial(self.change_page, page.id))

        dv = Divider(margin=1, orientation=Qt.Orientation.Vertical)
        shared.theme.add_widget(dv)
        layout.addWidget(dv)

        content_lyt = QVBoxLayout()
        content_lyt.setContentsMargins(0, 0, 0, 0)
        content_lyt.setSpacing(0)
        layout.addLayout(content_lyt)

        self.page_area = QWidget()
        self.page_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_lyt.addWidget(self.page_area)

        dv = Divider(margin=1, orientation=Qt.Orientation.Horizontal)
        shared.theme.add_widget(dv)
        content_lyt.addWidget(dv)

        self.statusbar = StatusBar()
        content_lyt.addWidget(self.statusbar)

        self.init_pages()

    def update_theme(self, theme: Theme) -> None:
        log.info(f"Changed app theme to {theme.palette.name}")

        if platform.system() == "Windows":
            ret = change_titlebar_theme(self, theme.palette.is_dark)

            if ret != 0:
                log.warn(f"<fg.blue>change_titlebar_theme</> failed with code <fg.lightred>{ret}</>")

        else:
            log.info("Titlebar themeing is only supported on Windows currently.")

        self.setStyleSheet(f"background-color: {theme.qss(theme.palette.background_primary)};")

        self.page_area.setStyleSheet(f"background-color: {theme.qss(theme.palette.background_secondary)};")

    def get_page_from_id(self, page_id: str) -> Page | None:
        """ Get page dict from name. None if not found. """

        for page in self.pages:
            if page_id == page.id:
                return page

    def change_page(self, page_id: str) -> None:
        """
        Change the current page and update animations.

        Parameters
        ----------
        page_id
            Page id to switch to
        """

        page = self.get_page_from_id(page_id)

        if self.current_page is not None:
            self.sidebar.page_buttons[self.current_page.id].variant = Button.Variant.GHOST

        self.current_page = page
        self.sidebar.page_buttons[page_id].variant = Button.Variant.SECONDARY

        self.sidebar.change_cursor(page)
        self.statusbar.page_name_lbl.setText(f"#{page.name}")

    def init_pages(self) -> None:
        """ Initialize page widgets. """

        for page in self.pages:
            view = importlib.import_module(f"llm_qlient.ui.pages.{page.id}.view")
            v = view.View()