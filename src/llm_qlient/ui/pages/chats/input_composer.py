"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from freshqt.core import TypographyType, Theme, Themeable
from freshqt.widgets import Button

from llm_qlient import shared
from llm_qlient.ui.widgets.auto_pair_editor import AutoPairEditor


class InputComposer(QWidget, Themeable):
    """
    Input message composer widget.
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        composer_height = 90
        btn_height = round(composer_height / 3.5)
        icon_height = round(composer_height / 4.7)
        self.setMaximumHeight(composer_height)

        self.editor = AutoPairEditor()
        layout.addWidget(self.editor)
        self.editor.setPlaceholderText("Ask anything to your local LLM...")

        buttons_lyt = QVBoxLayout()
        buttons_lyt.setContentsMargins(0, 0, 0, 0)
        buttons_lyt.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(buttons_lyt)

        self.send_btn = Button(icon_name="hi-paper-airplane", variant=Button.Variant.GHOST)
        self.send_btn.setFixedSize(btn_height, btn_height)
        self.send_btn.setIconSize(QSize(icon_height, icon_height))
        self.send_btn.border_radius = -1
        shared.theme.add_widget(self.send_btn)
        buttons_lyt.addWidget(self.send_btn)

        self.retry_btn = Button(icon_name="hi-arrow-path", variant=Button.Variant.GHOST)
        self.retry_btn.setFixedSize(btn_height, btn_height)
        self.retry_btn.setIconSize(QSize(icon_height, icon_height))
        self.retry_btn.border_radius = -1
        shared.theme.add_widget(self.retry_btn)
        buttons_lyt.addWidget(self.retry_btn)

        self.continue_btn = Button(icon_name="hi-forward", variant=Button.Variant.GHOST)
        self.continue_btn.setFixedSize(btn_height, btn_height)
        self.continue_btn.setIconSize(QSize(icon_height, icon_height))
        self.continue_btn.border_radius = -1
        shared.theme.add_widget(self.continue_btn)
        buttons_lyt.addWidget(self.continue_btn)

        self.stop_btn = Button(icon_name="hi-stop", variant=Button.Variant.GHOST)
        self.stop_btn.setFixedSize(btn_height, btn_height)
        self.stop_btn.setIconSize(QSize(icon_height, icon_height))
        self.stop_btn.border_radius = -1
        shared.theme.add_widget(self.stop_btn)
        buttons_lyt.addWidget(self.stop_btn)

        self.send_btn.setToolTip("Send message")
        self.retry_btn.setToolTip("Regenerate last assistant message")
        self.continue_btn.setToolTip("Resume generating last assistant message")
        self.stop_btn.setToolTip("Stop generating")

        self.set_buttons_state(False)

    def update_theme(self, theme: Theme) -> None:
        font_size = int(round(theme.get_typo_size(TypographyType.BODY) * theme.font_scale))
        if font_size <= 0:
            font_size = 1

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: {theme.font_family};
                font-size: {font_size}px;
                color: {theme.qss(theme.palette.text_primary)};
                background-color: {theme.qss(theme.palette.background_secondary)};
                border: 1px solid {theme.qss(theme.palette.text_tertiary)};
                border-radius: 10px;
                selection-background-color: {theme.qss(theme.palette.text_selection)};
                padding: 5px;
            }}
        """)

    def get_message(self) -> str:
        """ Get input message text. """
        return self.editor.toPlainText().strip()
    
    def clear_message(self) -> None:
        """ Clear input message text. """
        self.editor.clear()

    def set_buttons_state(self, generating: bool) -> None:
        """
        Set control buttons state.

        Either show action buttons or show the stop button.
        
        Parameters
        ----------
        generating
            Generation state
        """

        if generating:
            self.send_btn.hide()
            self.retry_btn.hide()
            self.continue_btn.hide()
            self.stop_btn.show()

        else:
            self.send_btn.show()
            self.retry_btn.show()
            self.continue_btn.show()
            self.stop_btn.hide()