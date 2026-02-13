"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

import platform

from PyQt6.QtCore import Qt, QSize, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLineEdit, QScrollArea
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.core import __version__ as __freshqt_version__
from freshqt.widgets import Button, Divider, TypoLabel, Switch, LineEdit, BadgeLabel
from freshqt.animation import Tween, Easing
from panllm import __version__ as __panllm_version__

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.ui.pages.base_view import BaseView


class View(BaseView):
    def __init__(self) -> None:
        super().__init__()

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(outer_layout)

        content = QWidget()
        content.setMaximumWidth(880)
        content.setMinimumWidth(620)

        content_scroller = QScrollArea()
        content_scroller.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_scroller.setWidget(content)
        content_scroller.setWidgetResizable(True)
        content_scroller.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        outer_layout.addWidget(content_scroller)

        content_scroller.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        content.setStyleSheet("background: transparent;")

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

        self.version_section()

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

    def setting_desc(self, text: str, desc: str, setting: str | None = None) -> None:
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

        if setting is not None:
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
        
    def version_section(self) -> None:
        desc_lyt = QVBoxLayout()
        desc_lyt.setContentsMargins(0, 0, 0, 0)
        desc_lyt.setSpacing(10)
        self.content_lyt.addLayout(desc_lyt)

        lbl = TypoLabel("Version information", TypographyType.SUBTITLE)
        shared.theme.add_widget(lbl)
        desc_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        versions = (
            ("Python", f"{platform.python_version()} - {platform.python_compiler()}"),
            ("Qt", QT_VERSION_STR),
            ("PyQt", PYQT_VERSION_STR),
            ("FreshQt", __freshqt_version__),
            ("PanLLM", __panllm_version__),
            ("LLM Qlient", shared.__version__)
        )
        for name, version in versions:
            version_lyt = QHBoxLayout()
            version_lyt.setContentsMargins(0, 0, 0, 0)
            version_lyt.setAlignment(Qt.AlignmentFlag.AlignLeft)
            desc_lyt.addLayout(version_lyt)

            lbl = TypoLabel(name, TypographyType.BODY)
            lbl.color = "text_secondary"
            shared.theme.add_widget(lbl)
            version_lyt.addWidget(lbl)

            lbl = BadgeLabel(version, color="brand_primary")
            lbl.border_radius = 7
            shared.theme.add_widget(lbl)
            version_lyt.addWidget(lbl)