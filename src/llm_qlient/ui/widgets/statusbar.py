"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel
from freshqt.animation import Tween, Easing

from llm_qlient import shared


class StatusBar(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setFixedHeight(24)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

        self.page_name_lbl = TypoLabel(type=TypographyType.CAPTION)
        self.page_name_lbl.color = "text_secondary"
        shared.theme.add_widget(self.page_name_lbl)
        layout.addWidget(self.page_name_lbl)

        layout.addStretch()

        self.utilization_lbl = TypoLabel("CPU: 0%     |     GPU: 0%     |     RAM: 15.1GB     |     VRAM: 11.8GB", type=TypographyType.CAPTION)
        self.utilization_lbl.color = "text_secondary"
        shared.theme.add_widget(self.utilization_lbl)
        layout.addWidget(self.utilization_lbl)