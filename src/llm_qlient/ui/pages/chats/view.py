"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor
from freshqt.core import TypographyType
from freshqt.widgets import Button, Divider, TypoLabel
from freshqt.animation import Tween, Easing

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.models import Conversation
from llm_qlient.ui.pages.base_view import BaseView
from llm_qlient.ui.pages.chats.conversation import ConversationView, ConversationController


class View(BaseView):
    def __init__(self) -> None:
        super().__init__()

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(outer_layout)

        self.convo = Conversation([])

        self.convo_view = ConversationView()
        self.convo_view.setMaximumWidth(880)
        self.convo_view.setMinimumWidth(620)
        self.convo_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer_layout.addWidget(self.convo_view)

        self.convo_cont = ConversationController(self.convo_view, self.convo)