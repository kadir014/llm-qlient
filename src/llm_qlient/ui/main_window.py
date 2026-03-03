"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import platform
import importlib
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from freshqt.core import Theme, Themeable, change_titlebar_theme
from freshqt.widgets import Divider, Button

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.models import Page
from llm_qlient.ui.widgets.sidebar import SideBar
from llm_qlient.ui.widgets.statusbar import StatusBar
from llm_qlient.ui.hotkey_manager import HotkeyManager


class MainWindow(QWidget, Themeable):
    """
    Top-level main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(f"LLM Qlient v{shared.__version__}")
        self.setWindowIcon(shared.icons.get("windowicon"))
        self.resize(1280, 720)
        self.setMinimumSize(640, 360)

        # This needs to be created *after* main window is defined, but *before*
        # all content is initialized so that they can listen to hotkeys.
        shared.hotkeys = HotkeyManager(self)
        shared.hotkeys.invoked.connect(self._hotkey_invoked)

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
        
        self.sidebar.layout().insertStretch(self.sidebar.layout().count() - 1)

        for page in self.pages:
            button = self.sidebar.page_buttons[page]
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

        self.setObjectName("bg_primary")
        self.page_area.setObjectName("bg_secondary")

        self.page_area_lyt = QVBoxLayout()
        self.page_area_lyt.setContentsMargins(0, 0, 0, 0)
        self.page_area_lyt.setSpacing(0)
        self.page_area.setLayout(self.page_area_lyt)

        dv = Divider(margin=1, orientation=Qt.Orientation.Horizontal)
        shared.theme.add_widget(dv)
        content_lyt.addWidget(dv)

        self.statusbar = StatusBar()
        content_lyt.addWidget(self.statusbar)

        self.init_pages()

    def _hotkey_invoked(self, action: str, key_seq: str) -> None:
        if action == "quit":
            self.close()

    def update_theme(self, theme: Theme) -> None:
        if platform.system() == "Windows":
            ret = change_titlebar_theme(self, theme.palette.is_dark)

            if ret != 0:
                log.warn(f"<fg.blue>change_titlebar_theme</> failed with code <fg.lightred>{ret}</>")

        else:
            log.info("Titlebar themeing is only supported on Windows currently.")

        log.debug(f"Theme <fg.magenta>{theme.palette.name}</> is (re)loaded.")

        self.setStyleSheet(f"""
            QWidget#bg_primary {{
                background-color: {theme.qss(theme.palette.background_primary)};
            }}

            QWidget#bg_secondary {{
                background-color: {theme.qss(theme.palette.background_secondary)};
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 0px 0px 0px 0px;
                border: none;
            }}

            QScrollBar::handle:vertical {{
                min-height: 0px;
                width: 6px;
                margin: 0px 0px 0px 0px;
                background: {theme.qss(theme.palette.text_primary)};
                border: 0px solid black;
                border-radius: 3px;
                opacity: 255;
            }}

            QScrollBar::handle:hover:vertical {{
                background: {theme.qss(theme.palette.text_primary)}
            }}

            QScrollBar::add-line:vertical {{
                height: 0px;
            }}

            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
                height: 0px;
            }}

            QLabel, QTextEdit {{
                selection-background-color: {theme.qss(theme.palette.text_selection)};
            }}
        """)

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
            self.current_page.view.hide()
            self.sidebar.page_buttons[self.current_page].variant = Button.Variant.GHOST

        self.current_page = page
        self.current_page.view.show()
        self.sidebar.page_buttons[page].variant = Button.Variant.SECONDARY

        self.sidebar.change_cursor(page)
        self.statusbar.page_name_lbl.setText(f"#{page.name}")

    def init_pages(self) -> None:
        """ Initialize page widgets. """

        for page in self.pages:
            view = importlib.import_module(f"llm_qlient.ui.pages.{page.id}.view")
            page.view = view.View()
            page.view.hide()

            self.page_area_lyt.addWidget(page.view)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        shared.window_resize.emit()