"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import platform
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
    QFileDialog
)
from freshqt.core import TypographyType
from freshqt.widgets import Button, TypoLabel, Switch, LineEdit, BadgeLabel

from llm_qlient import shared
from llm_qlient.ui.pages.base_view import BaseView
from llm_qlient.ui.factories import *


class View(BaseView):
    """
    Settings user interface view.
    """

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

        h1("Settings", self.content_lyt)

        self.content_lyt.addSpacing(9)

        self.setting(
            "Theme",
            "Filepath to global application theme to use.\nYou can use the native ones with the indicator \"builtin: ...\".",
            "theme",
            browse_file=True
        )

        hdivider(3, self.content_lyt)

        self.setting(
            "Center conversation view",
            "Try to center conversation view relative to viewport instead of its layout.\nMight be more visually appealing for some.",
            "center_conversation_view"
        )

        hdivider(3, self.content_lyt)

        self.setting("Show system metrics", "", "system_metrics_show")

        self.setting(
            "System metrics update frequency",
            "Controls how often the system metrics are refreshed, in seconds.",
            "system_metrics_interval"
        )

        self.setting(
            "System metrics display format",
            "Customize the text shown for system metrics in the status bar. For example <code>\"CPU usage: {cpu}%\"</code>.",
            "system_metrics_formatter"
        )

        self.version_section()

    def setting(self,
            text: str,
            desc: str,
            setting: str | None = None,
            browse_file: bool = False
            ) -> None:
        """
        Add new setting section.

        Parameters
        ----------
        text
            Short title for the setting
        desc
            Description of setting
        setting
            Setting key
        browse_file
            Whether to add a file browsing option to text input
        """

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

        if desc:
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
                line_lyt = QHBoxLayout()
                line_lyt.setContentsMargins(0, 0, 0, 0)
                desc_lyt.addLayout(line_lyt)

                line = LineEdit(shared.settings[setting])
                shared.theme.add_widget(line)
                line_lyt.addWidget(line)

                @line.editingFinished.connect
                def line_slot():
                    shared.settings[setting] = line.text()

                if browse_file:
                    browse_btn = Button(icon_name="hi-magnifying-glass", variant=Button.Variant.OUTLINE)
                    browse_btn.border_radius = -1
                    browse_btn.setFixedSize(35, 35)
                    shared.theme.add_widget(browse_btn)
                    line_lyt.addWidget(browse_btn)

                    @browse_btn.clicked.connect
                    def browse_slot():
                        path = QFileDialog.getOpenFileName(
                            self,
                            str(Path.cwd().absolute()),
                        )[0]

                        line.setText(path)
                        shared.settings[setting] = path

            elif isinstance(shared.settings[setting], float):
                line = LineEdit(str(shared.settings[setting]))
                shared.theme.add_widget(line)
                desc_lyt.addWidget(line)

                @line.editingFinished.connect
                def line_slot():
                    value = line.text()
                    
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0

                    shared.settings[setting] = value
                    line.setText(str(value))
        
    def version_section(self) -> None:
        """ Add a version information section. """

        desc_lyt = QVBoxLayout()
        desc_lyt.setContentsMargins(0, 0, 0, 0)
        desc_lyt.setSpacing(10)
        self.content_lyt.addLayout(desc_lyt)

        lbl = TypoLabel("Version information", TypographyType.SUBTITLE)
        shared.theme.add_widget(lbl)
        desc_lyt.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        versions = (
            ("Python", f"{platform.python_version()} - {platform.python_compiler()}"),
            ("Qt", shared.__qt_version__),
            ("PyQt", shared.__pyqt_version__),
            ("FreshQt", shared.__freshqt__version__),
            ("PanLLM", shared.__panllm_version__),
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