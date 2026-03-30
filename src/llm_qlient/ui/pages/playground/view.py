"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy
from freshqt.core import TypographyType, Theme, Themeable
from freshqt.widgets import Button
from panllm import ChatChunk, GenerationStats

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.models import GenerationRequest
from llm_qlient.ui.factories import *
from llm_qlient.ui.pages.base_view import BaseView
from llm_qlient.ui.widgets.auto_pair_editor import AutoPairEditor


class View(BaseView, Themeable):
    def __init__(self) -> None:
        super().__init__()
        shared.theme.add_widget(self)

        outerlayout = QVBoxLayout()
        outerlayout.setContentsMargins(100, 0, 100, 0)
        self.setLayout(outerlayout)

        outerlayout.addSpacing(25)
        h1("Playground", outerlayout)
        outerlayout.addSpacing(25)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        outerlayout.addLayout(layout)

        self.editor = AutoPairEditor()
        self.editor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.editor)
        self.editor.setPlaceholderText(
            "Write anything...\n\n"
            "The text you write here is purely passed down to the model as the initial prompt when generating.\n"
            "No chat templates or formatting is applied."
        )

        layout.addSpacing(20)

        control_lyt = QVBoxLayout()
        control_lyt.setContentsMargins(0, 0, 0, 0)
        control_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(control_lyt)

        self.gen_button = Button("Generate", icon_name="hi-play")
        self.gen_button.background_color = "state_success"
        self.gen_button.clicked.connect(self.start_generating)
        shared.theme.add_widget(self.gen_button)
        control_lyt.addWidget(self.gen_button)
        self.gen_button.setMinimumWidth(105)

        self.stop_button = Button("Stop", icon_name="hi-stop")
        self.stop_button.background_color = "state_error"
        self.stop_button.clicked.connect(shared.gen.stop_gen)
        shared.theme.add_widget(self.stop_button)
        control_lyt.addWidget(self.stop_button)
        self.stop_button.hide()
        self.stop_button.setMinimumWidth(105)

        outerlayout.addSpacing(35)

        shared.gen.generation_started.connect(self._generation_started)
        shared.gen.generation_finished.connect(self._generation_finished)
        shared.gen.new_chat_chunk.connect(self._new_chat_chunk)

    def set_state(self, state: bool) -> None:
        """ Set user interface generation state. """

        if state:
            self.editor.setReadOnly(True)

            self.gen_button.hide()
            self.stop_button.show()

        else:
            self.editor.setReadOnly(False)

            self.gen_button.show()
            self.stop_button.hide()

    def start_generating(self) -> None:
        """ Start generating with current prompt. """

        if not shared.gen.is_available:
            log.debug("No model loaded, skipping playground gen.")
            shared.toasts.error("No model loaded!")
            return

        prompt = self.editor.toPlainText()
        shared.gen.start_gen(GenerationRequest(prompt, "text"))

    @pyqtSlot(str)
    def _generation_started(self, mode: str) -> None:
        if mode not in {"text"}:
            return
        
        self.set_state(True)

    @pyqtSlot(str, ChatChunk, GenerationStats)
    def _generation_finished(self,
            mode: str,
            chunk: ChatChunk,
            stats: GenerationStats
            ) -> None:
        if mode not in {"text"}:
            return
        
        self.set_state(False)

    @pyqtSlot(str, ChatChunk)
    def _new_chat_chunk(self, mode: str, chunk: ChatChunk) -> None:
        if mode not in {"text"}:
            return
        
        curr_prompt = self.editor.toPlainText()
        self.editor.setPlainText(curr_prompt + chunk.content)

    def update_theme(self, theme: Theme) -> None:
        font_size = int(round(theme.get_typo_size(TypographyType.BODY) * theme.font_scale))
        if font_size <= 0:
            font_size = 1

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: {theme.font_family};
                font-size: {font_size}px;
                color: {theme.qss(theme.palette.text_primary)};
                background-color: {theme.qss(theme.palette.background_tertiary)};
                border: 1px solid {theme.qss(theme.palette.text_tertiary)};
                border-radius: 10px;
                selection-background-color: {theme.qss(theme.palette.text_selection)};
                padding: 5px;
            }}
        """)