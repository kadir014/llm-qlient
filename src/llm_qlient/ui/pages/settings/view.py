"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel, Switch
from freshqt.animation import Tween, Easing

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.ui.pages.base_view import BaseView


class View(BaseView):
    def __init__(self) -> None:
        super().__init__()

        #Load defaults
        #Load user settings (if they exist)
        #Merge them

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(outer_layout)

        content = QWidget()
        content.setMaximumWidth(880)
        content.setMinimumWidth(620)
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer_layout.addWidget(content)

        self.content_lyt = QVBoxLayout()
        self.content_lyt.setContentsMargins(0, 30, 0, 0)
        self.content_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_lyt.setSpacing(45)
        content.setLayout(self.content_lyt)

        self.h1("Settings")

        self.content_lyt.addSpacing(9)

        self.setting("Show system metrics", switch=True)

        self.setting_desc("System metrics update frequency", "Controls how often the system metrics are refreshed, in seconds.")

        self.setting_desc("System metrics display format", "Customize the text shown for system metrics in the status bar. For example <code>\"CPU usage: {cpu}%\"</code>.")

    def h1(self, text: str) -> None:
        lbl = TypoLabel(text, TypographyType.TITLE1)
        shared.theme.add_widget(lbl)
        self.content_lyt.addWidget(lbl)

    def h3(self, text: str) -> None:
        lbl = TypoLabel(text, TypographyType.TITLE3)
        shared.theme.add_widget(lbl)
        self.content_lyt.addWidget(lbl)

    def setting(self, text, switch: bool = False) -> None:
        setting_lyt = QHBoxLayout()
        setting_lyt.setContentsMargins(0, 0, 0, 0)
        self.content_lyt.addLayout(setting_lyt)

        lbl = TypoLabel(text, TypographyType.SUBTITLE)
        shared.theme.add_widget(lbl)
        setting_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        if switch:
            sw = Switch()
            sw.setFixedSize(55, 25)
            shared.theme.add_widget(sw)
            setting_lyt.addWidget(sw, alignment=Qt.AlignmentFlag.AlignRight)

    def setting_desc(self, text: str, desc: str, switch: bool = False) -> None:
        setting_lyt = QHBoxLayout()
        setting_lyt.setContentsMargins(0, 0, 0, 0)
        self.content_lyt.addLayout(setting_lyt)

        desc_lyt = QVBoxLayout()
        desc_lyt.setContentsMargins(0, 0, 0, 0)
        desc_lyt.setSpacing(10)
        setting_lyt.addLayout(desc_lyt)

        lbl = TypoLabel(text, TypographyType.SUBTITLE)
        shared.theme.add_widget(lbl)
        desc_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        lbl = TypoLabel(desc, TypographyType.BODY)
        lbl.color = "text_secondary"
        shared.theme.add_widget(lbl)
        desc_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        if switch:
            sw = Switch()
            sw.setFixedSize(55, 25)
            shared.theme.add_widget(sw)
            setting_lyt.addWidget(sw, alignment=Qt.AlignmentFlag.AlignRight)