"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QHBoxLayout
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType, Theme, Themeable
from freshqt.widgets import Button, Divider, TypoLabel, Avatar
from freshqt.animation import Tween, Easing

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.ui.factories import *
from llm_qlient.core.models import Conversation, Character
from llm_qlient.ui.pages.base_view import BaseView


class ChatHistoryEntry(QWidget):
    def __init__(self, convo: Conversation) -> None:
        super().__init__()

        self._convo = convo

        layout = QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(layout)

        self.avatar = Avatar()
        self.avatar.setFixedSize(24, 24)
        shared.theme.add_widget(self.avatar)
        layout.addWidget(self.avatar)

        title = convo.character.name

        self.button = Button(title, variant=Button.Variant.GHOST)
        self.button.setContentsMargins(5, 5, 5, 5)
        self.button.text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        self.button.border_radius = -1
        shared.theme.add_widget(self.button)
        layout.addWidget(self.button)

        # TODO: Delete chat history button


class ChatHistory(QWidget, Themeable):
    """
    Chat history view widget.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setFixedWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        layout.setContentsMargins(7, 14, 7, 7)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

        h3lbl = h3("Chat History", layout)
        h3lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        hdivider(30, layout)

    def add_entry(self, convo: Conversation) -> ChatHistoryEntry:
        """ Add new chat history entry. """
        entry = ChatHistoryEntry(convo)
        self.layout().addWidget(entry)
        return entry

    def paintEvent(self, e) -> None:
        pt = QPainter(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=False)

        color = shared.theme.qcolor(shared.theme.palette.background_primary)
        pt.fillRect(0, 0, self.width(), self.height(), color)