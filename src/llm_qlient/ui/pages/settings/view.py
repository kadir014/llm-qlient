"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLineEdit
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel, Switch, LineEdit
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

        self.setting("Show system metrics", "system_metrics_show")

        self.setting_desc(
            "System metrics update frequency",
            "Controls how often the system metrics are refreshed, in seconds.",
            "system_metrics_interval"
        )

        self.setting_desc(
            "System metrics display format",
            "Customize the text shown for system metrics in the status bar. For example <code>\"CPU usage: {cpu}%\"</code>.",
            "system_metrics_formatter"
        )

        shared.settings.changed.connect(self._settings_changed)

    def _settings_changed(self) -> None:
        # for key, switch in self.switches.items():
        #     switch.on = shared.settings[key]
        ...

    def h1(self, text: str) -> None:
        lbl = TypoLabel(text, TypographyType.TITLE1)
        shared.theme.add_widget(lbl)
        self.content_lyt.addWidget(lbl)

    def h3(self, text: str) -> None:
        lbl = TypoLabel(text, TypographyType.TITLE3)
        shared.theme.add_widget(lbl)
        self.content_lyt.addWidget(lbl)

    def setting(self, text: str, setting: str) -> None:
        setting_lyt = QHBoxLayout()
        setting_lyt.setContentsMargins(0, 0, 0, 0)
        self.content_lyt.addLayout(setting_lyt)

        lbl = TypoLabel(text, TypographyType.SUBTITLE)
        shared.theme.add_widget(lbl)
        setting_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        if isinstance(shared.settings[setting], bool):
            sw = Switch(on=shared.settings[setting])
            sw.setFixedSize(55, 25)
            shared.theme.add_widget(sw)
            setting_lyt.addWidget(sw, alignment=Qt.AlignmentFlag.AlignRight)

            @sw.toggled.connect
            def sw_slot():
                shared.settings[setting] = sw.on

    def setting_desc(self, text: str, desc: str, setting: str, float_only: bool = True) -> None:
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

        if isinstance(shared.settings[setting], bool):
            sw = Switch(on=shared.settings[setting])
            sw.setFixedSize(55, 25)
            shared.theme.add_widget(sw)
            setting_lyt.addWidget(sw, alignment=Qt.AlignmentFlag.AlignRight)

            @sw.toggled.connect
            def sw_slot():
                shared.settings[setting] = sw.on

        elif isinstance(shared.settings[setting], str):
            line = LineEdit(shared.settings[setting])
            shared.theme.add_widget(line)
            desc_lyt.addWidget(line)

            @line.textChanged.connect
            def line_slot():
                shared.settings[setting] = line.text()

        elif isinstance(shared.settings[setting], float):
            line = LineEdit(str(shared.settings[setting]))
            shared.theme.add_widget(line)
            desc_lyt.addWidget(line)

            @line.textChanged.connect
            def line_slot():
                value = line.text()
                
                try:
                    value = float(value)
                except ValueError:
                    value = 0.0

                shared.settings[setting] = value
                line.setText(str(value))