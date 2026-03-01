"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout
from freshqt.core import TypographyType
from freshqt.widgets import TypoLabel

from llm_qlient import shared
from llm_qlient.ui.pages.base_view import BaseView


class View(BaseView):
    def __init__(self) -> None:
        super().__init__()

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(outer_layout)

        lbl = TypoLabel("🚧 This page is under construction.", type=TypographyType.LARGE_TITLE)
        shared.theme.add_widget(lbl)
        outer_layout.addWidget(lbl)

        lbl = TypoLabel("Come back later!", type=TypographyType.BODY)
        shared.theme.add_widget(lbl)
        outer_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignHCenter)