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
from freshqt.widgets import (
    Button,
    TypoLabel,
    Switch,
    LineEdit,
    BadgeLabel,
    Slider
)

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

        self.content_scroller = QScrollArea()
        self.content_scroller.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_scroller.setWidget(content)
        self.content_scroller.setWidgetResizable(True)
        self.content_scroller.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        outer_layout.addWidget(self.content_scroller)

        self.content_scroller.setStyleSheet("""
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

        self.add_setting(
            "Theme",
            "Filepath to global application theme to use.\nYou can use the native ones with the indicator \"builtin: ...\".",
            "theme",
            browse_file=True
        )

        hdivider(3, self.content_lyt)

        self.add_setting(
            "Center conversation view",
            "Try to center conversation view relative to viewport instead of its layout.\nMight be more visually appealing for some.",
            "center_conversation_view"
        )

        self.add_setting(
            "Font scale",
            "Scaling factor applied to almost all text content on the interface.",
            "ui_font_scale",
            slider=True
        )

        self.add_setting(
            "Pair brackets",
            "In text editors, pair characters like `(`, `[`, `{` and `\"` with their closing counterparts automatically.",
            "editor_auto_pair"
        )

        self.add_setting(
            "Enter sends message",
            "Send new message in the text conversation with 'enter' or 'return' key.",
            "editor_enter_sends"
        )

        hdivider(3, self.content_lyt)

        self.add_setting("Show system metrics", "", "system_metrics_show")

        self.add_setting(
            "System metrics update frequency",
            "Controls how often the system metrics are refreshed, in seconds.",
            "system_metrics_interval"
        )

        self.add_setting(
            "System metrics display format",
            "Customize the text shown for system metrics in the status bar. For example <code>\"CPU usage: {cpu}%\"</code>.",
            "system_metrics_formatter"
        )

        hdivider(3, self.content_lyt)

        self.add_setting(
            "Allow dummy text generation",
            "If no model is loaded, instead of warning the user, generate dummy text imitating assistant response.\nUseful for debugging purposes.",
            "dev_allow_dummy_gen"
        )

        hdivider(3, self.content_lyt)

        self.add_version_section()

        self.content_lyt.addSpacing(35)

    def add_setting(self,
            text: str,
            desc: str,
            setting: str | None = None,
            browse_file: bool = False,
            slider: bool = False
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
        slider
            Use a slider instead of text input for numerical settings
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
                def _():
                    shared.settings[setting] = sw.on

            elif isinstance(shared.settings[setting], str):
                line_lyt = QHBoxLayout()
                line_lyt.setContentsMargins(0, 0, 0, 0)
                desc_lyt.addLayout(line_lyt)

                line = LineEdit(shared.settings[setting])
                shared.theme.add_widget(line)
                line_lyt.addWidget(line)

                @line.editingFinished.connect
                def _():
                    shared.settings[setting] = line.text()

                if browse_file:
                    browse_btn = Button(icon_name="hi-magnifying-glass", variant=Button.Variant.OUTLINE)
                    browse_btn.border_radius = -1
                    browse_btn.setFixedSize(35, 35)
                    shared.theme.add_widget(browse_btn)
                    line_lyt.addWidget(browse_btn)

                    @browse_btn.clicked.connect
                    def _():
                        path = QFileDialog.getOpenFileName(
                            self,
                            str(Path.cwd().absolute()),
                        )[0]

                        line.setText(path)
                        shared.settings[setting] = path

            elif isinstance(shared.settings[setting], float):
                if slider:
                    slider_lyt = QHBoxLayout()
                    slider_lyt.setContentsMargins(0, 0, 0, 0)
                    slider_lyt.setSpacing(10)
                    desc_lyt.addLayout(slider_lyt)

                    sl = Slider()
                    shared.theme.add_widget(sl)
                    slider_lyt.addWidget(sl)

                    # TODO: Hardcoded magic numbers! Make them configurable
                    # [0.25, 2.0] * 100
                    sl.setMaximum(200)
                    sl.setMinimum(25)
                    sl.setValue(int(shared.settings[setting] * 100.0))

                    # To disable controlling with mouse wheel and arrow keys
                    sl.setSingleStep(0)
                    sl.setPageStep(0)

                    sl.setFixedHeight(16)

                    slider_lbl = BadgeLabel(f"{round(shared.settings[setting] * 100.0)}%")
                    slider_lbl.bg_color = "background_tertiary"
                    shared.theme.add_widget(slider_lbl)
                    slider_lyt.addWidget(slider_lbl)

                    @sl.sliderReleased.connect
                    def _():
                        value = float(sl.value()) / 100.0
                        shared.settings[setting] = value
                        slider_lbl.setText(f"{round(value * 100.0)}%")

                    @sl.valueChanged.connect
                    def _():
                        value = float(sl.value()) / 100.0
                        slider_lbl.setText(f"{round(value * 100.0)}%")

                else:
                    line = LineEdit(str(shared.settings[setting]))
                    shared.theme.add_widget(line)
                    desc_lyt.addWidget(line)

                    @line.editingFinished.connect
                    def _():
                        value = line.text()
                        
                        try:
                            value = float(value)
                        except ValueError:
                            value = shared.settings[setting]

                        shared.settings[setting] = value
                        line.setText(str(value))
        
    def add_version_section(self) -> None:
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