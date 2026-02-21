"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel
from freshqt.animation import Tween, Easing

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.content import load_content
from llm_qlient.core.models import UserPersona
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